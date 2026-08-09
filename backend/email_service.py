"""Gmail SMTP + traveler-voiced HTML invite email.

Design: boarding pass strip + passport-stamped hero + torn tape + luggage tag +
paper-plane CTA + postcard-back footer. Tables + inline CSS = email-client safe.
"""

from __future__ import annotations

import logging
import os
import random
import ssl
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import make_msgid

import aiosmtplib

from quotes import COUNTRY_STAMP_HINTS, INVITE_HERO_IMAGES, TRAVEL_QUOTES

log = logging.getLogger(__name__)

# Wanderly palette
CREAM = "#FAF3E7"
SAND = "#E8D5B7"
KRAFT = "#D4A574"
TERRACOTTA = "#C65D3A"
SAGE = "#A8B89A"
INK = "#2C2416"
NAVY = "#3A5068"  # faded passport-stamp ink


# ------------------------------------------------------------------ inline SVG assets

# Paper airplane icon for the CTA button (cream on terracotta)
_PLANE_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' "
    "fill='none' stroke='%23FAF3E7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
    "<line x1='22' y1='2' x2='11' y2='13'></line>"
    "<polygon points='22 2 15 22 11 13 2 9 22 2'></polygon>"
    "</svg>"
)


def _passport_stamp_svg(text: str, rotate: int, ink: str = NAVY) -> str:
    """Rotated circular passport stamp — inline SVG."""
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140' viewBox='0 0 140 140' "
        f"style='transform:rotate({rotate}deg);'>"
        f"<circle cx='70' cy='70' r='60' stroke='{ink}' stroke-width='3' fill='none' "
        f"stroke-opacity='0.75'/>"
        f"<circle cx='70' cy='70' r='50' stroke='{ink}' stroke-width='1.5' fill='none' "
        f"stroke-opacity='0.55' stroke-dasharray='3 3'/>"
        f"<text x='50%' y='50%' text-anchor='middle' dominant-baseline='middle' "
        f"font-family='Bebas Neue, Impact, sans-serif' font-size='19' letter-spacing='2' "
        f"fill='{ink}' fill-opacity='0.85'>{text}</text>"
        f"<text x='50%' y='72%' text-anchor='middle' dominant-baseline='middle' "
        f"font-family='Bebas Neue, Impact, sans-serif' font-size='11' letter-spacing='2' "
        f"fill='{ink}' fill-opacity='0.7'>WANDERLY</text>"
        f"</svg>"
    )


def _compass_svg() -> str:
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='38' height='38' viewBox='0 0 24 24' "
        "fill='none' stroke='%232C2416' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'>"
        "<circle cx='12' cy='12' r='10'></circle>"
        "<polygon points='16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76'></polygon>"
        "</svg>"
    )


# ------------------------------------------------------------------ HTML

def _render_html(
    recipient_name: str,
    trip_name: str,
    organizer_name: str,
    destination: str,
    dates: str,
    accept_url: str,
    hero_image: str,
    quote: str,
) -> str:
    """Bulletproof HTML email — tables + inline CSS + inline SVG, mobile-friendly."""
    boarding_date = datetime.now(timezone.utc).strftime("%d %b %Y").upper()
    flight_no = f"WA-{random.randint(100, 999)}"
    gate = random.choice(["A26", "B14", "C07", "D22", "E09", "F31"])
    seat = f"{random.randint(1, 42)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"

    stamp_labels = [random.choice(COUNTRY_STAMP_HINTS)[0] for _ in range(2)]
    stamp1 = _passport_stamp_svg(stamp_labels[0], rotate=-8, ink=NAVY)
    stamp2 = _passport_stamp_svg(stamp_labels[1], rotate=12, ink=TERRACOTTA)

    upper_dest = destination.upper()
    upper_recipient = recipient_name.upper()

    # Style tag with @media for mobile stacking (Gmail web supports this)
    styles = """
      @media only screen and (max-width: 600px) {
        .container { width:100% !important; max-width:100% !important; }
        .px-40 { padding-left:24px !important; padding-right:24px !important; }
        .stack-col { display:block !important; width:100% !important; }
        .h-display { font-size:44px !important; line-height:1 !important; }
        .h-boarding { font-size:11px !important; letter-spacing:2px !important; }
        .hero-img { height:220px !important; }
        .stamp-abs { display:none !important; }
        .luggage-tag { padding:20px !important; }
        .cta-btn { padding:14px 26px !important; font-size:15px !important; }
      }
      @font-face { font-family: 'Fraunces'; }
      @font-face { font-family: 'Caveat'; }
      @font-face { font-family: 'Bebas Neue'; }
    """

    return f"""\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pack your bags — {trip_name}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=Caveat:wght@500;700&family=Bebas+Neue&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>{styles}</style>
</head>
<body style="margin:0;padding:0;background:{KRAFT};font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:{INK};-webkit-font-smoothing:antialiased;">
  <span style="display:none !important;opacity:0;color:transparent;height:0;width:0;overflow:hidden;">{organizer_name} just added you to {trip_name} — {destination}, {dates}. Pack your bags.</span>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{KRAFT};background-image:radial-gradient(circle at 20% 10%, rgba(255,255,255,0.16), transparent 40%),radial-gradient(circle at 80% 90%, rgba(0,0,0,0.05), transparent 40%);">
    <tr>
      <td align="center" style="padding:32px 12px;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" class="container" style="max-width:600px;width:100%;background:{CREAM};border-radius:14px;overflow:hidden;box-shadow:0 12px 40px rgba(44,36,22,0.18);">

          <!-- BOARDING PASS STRIP -->
          <tr>
            <td style="background:{INK};padding:0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="padding:14px 20px 10px 20px;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td class="h-boarding" style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:13px;letter-spacing:4px;color:{CREAM};">
                          &#9992;&#65039;&nbsp; WANDERLY&nbsp;&nbsp;&middot;&nbsp;&nbsp;BOARDING PASS
                        </td>
                        <td align="right" class="h-boarding" style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:12px;letter-spacing:3px;color:{SAND};">
                          FLIGHT {flight_no} &nbsp;&middot;&nbsp; GATE {gate} &nbsp;&middot;&nbsp; SEAT {seat}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:6px 20px 18px 20px;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td class="stack-col" width="47%" valign="top" style="padding-right:12px;">
                          <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:10px;letter-spacing:3px;color:{SAND};opacity:0.75;">PASSENGER</div>
                          <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:24px;letter-spacing:2px;color:{CREAM};margin-top:2px;line-height:1;">{upper_recipient}</div>
                        </td>
                        <td class="stack-col" width="6%" align="center" style="color:{SAND};font-size:10px;letter-spacing:2px;opacity:0.7;">
                          &mdash; &mdash;
                        </td>
                        <td class="stack-col" width="47%" valign="top" align="right" style="padding-left:12px;">
                          <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:10px;letter-spacing:3px;color:{SAND};opacity:0.75;">DESTINATION</div>
                          <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:24px;letter-spacing:2px;color:{TERRACOTTA};margin-top:2px;line-height:1;">{upper_dest}</div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Perforated divider -->
          <tr>
            <td style="background:{INK};height:12px;line-height:12px;font-size:1px;position:relative;">
              <div style="background-image:linear-gradient(to right,{CREAM} 50%,transparent 0);background-size:14px 2px;background-position:center;background-repeat:repeat-x;height:12px;">&nbsp;</div>
            </td>
          </tr>

          <!-- HERO IMAGE with overlaid passport stamps -->
          <tr>
            <td style="padding:0;position:relative;line-height:0;">
              <img src="{hero_image}" alt="{destination}" width="600" class="hero-img" style="display:block;width:100%;max-width:600px;height:280px;object-fit:cover;border:0;outline:none;text-decoration:none;">
            </td>
          </tr>

          <!-- Stamp row (below hero, since abs-positioning is unreliable in email) -->
          <tr>
            <td style="padding:0;background:{CREAM};">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:-70px;">
                <tr>
                  <td align="left" class="stamp-abs" style="padding:0 18px;line-height:0;" width="50%">
                    <div style="display:inline-block;">{stamp1}</div>
                  </td>
                  <td align="right" class="stamp-abs" style="padding:0 18px;line-height:0;" width="50%">
                    <div style="display:inline-block;">{stamp2}</div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- BIG DISPLAY HEADLINE -->
          <tr>
            <td class="px-40" style="padding:24px 44px 0 44px;">
              <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:12px;letter-spacing:5px;color:{TERRACOTTA};margin-bottom:14px;">
                &mdash;&nbsp;&nbsp;A NEW ADVENTURE
              </div>
              <h1 class="h-display" style="margin:0;font-family:'Fraunces','Playfair Display',Georgia,serif;font-weight:900;font-size:64px;line-height:0.92;color:{INK};letter-spacing:-1.5px;">
                PACK YOUR<br>
                <span style="font-style:italic;color:{TERRACOTTA};font-weight:700;">bags.</span>
              </h1>
              <p style="margin:22px 0 0 0;font-family:'Inter',Arial,sans-serif;font-size:17px;line-height:1.55;color:{INK};">
                <b>{organizer_name}</b> just added you to <b style="color:{TERRACOTTA};">{trip_name}</b>. {destination} is calling &mdash; and the crew wants you in.
              </p>
            </td>
          </tr>

          <!-- TORN TAPE WITH HANDWRITTEN NOTE -->
          <tr>
            <td class="px-40" style="padding:26px 44px 8px 44px;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="left">
                <tr>
                  <td style="background:#FFE8A8;padding:10px 22px;transform:rotate(-2deg);box-shadow:0 4px 14px rgba(44,36,22,0.10);border-left:1px dashed rgba(44,36,22,0.15);border-right:1px dashed rgba(44,36,22,0.15);">
                    <div style="font-family:'Caveat','Homemade Apple',cursive;font-size:26px;color:{INK};line-height:1.1;">
                      can't wait!! &mdash; {organizer_name.split()[0]}
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- LUGGAGE TAG (trip details card) -->
          <tr>
            <td class="px-40" style="padding:38px 44px 8px 44px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="luggage-tag" style="background:{SAND};border-radius:8px;position:relative;">
                <tr>
                  <td style="padding:28px 30px 26px 30px;">
                    <!-- tag string SVG -->
                    <div style="position:relative;">
                      <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:11px;letter-spacing:4px;color:{TERRACOTTA};margin-bottom:14px;">
                        &#9679;&nbsp;&nbsp;LUGGAGE TAG&nbsp;&nbsp;&#9679;
                      </div>

                      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td class="stack-col" width="50%" valign="top" style="padding:8px 8px 8px 0;">
                            <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:10px;letter-spacing:3px;color:{INK};opacity:0.55;">WHERE</div>
                            <div style="font-family:'Fraunces','Playfair Display',Georgia,serif;font-size:22px;font-weight:700;color:{INK};margin-top:4px;line-height:1.15;">{destination}</div>
                          </td>
                          <td class="stack-col" width="50%" valign="top" style="padding:8px 0 8px 8px;">
                            <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:10px;letter-spacing:3px;color:{INK};opacity:0.55;">WHEN</div>
                            <div style="font-family:'Fraunces','Playfair Display',Georgia,serif;font-size:22px;font-weight:700;color:{INK};margin-top:4px;line-height:1.15;">{dates}</div>
                          </td>
                        </tr>
                        <tr><td colspan="2" style="border-top:1px dashed rgba(44,36,22,0.20);padding-top:14px;">
                          <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:10px;letter-spacing:3px;color:{INK};opacity:0.55;">TRIP</div>
                          <div style="font-family:'Caveat',cursive;font-size:30px;color:{TERRACOTTA};margin-top:2px;line-height:1;">{trip_name}</div>
                          <div style="font-family:'Inter',Arial,sans-serif;font-size:12px;color:{INK};opacity:0.7;margin-top:8px;">Hosted by <b>{organizer_name}</b> &middot; boarding date {boarding_date}</div>
                        </td></tr>
                      </table>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA BUTTON WITH PAPER PLANE -->
          <tr>
            <td class="px-40" style="padding:32px 44px 6px 44px;text-align:center;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin:0 auto;">
                <tr>
                  <td align="center" style="background:{TERRACOTTA};border-radius:999px;box-shadow:0 8px 22px rgba(198,93,58,0.35);">
                    <a href="{accept_url}" class="cta-btn"
                       style="display:inline-block;padding:18px 44px;font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:19px;font-weight:700;letter-spacing:3px;color:#FFFFFF;text-decoration:none;border-radius:999px;">
                      <img src="data:image/svg+xml;utf8,{_PLANE_SVG}" width="18" height="18" alt="" style="vertical-align:-3px;margin-right:10px;">
                      JOIN THE TRIP
                    </a>
                  </td>
                </tr>
              </table>
              <div style="margin-top:14px;font-family:'Inter',Arial,sans-serif;font-size:12px;color:{INK};opacity:0.6;letter-spacing:0.3px;">
                See who's in &middot; Split expenses &middot; Book together &middot; Share the vibe
              </div>
            </td>
          </tr>

          <!-- POSTCARD BACK -->
          <tr>
            <td class="px-40" style="padding:40px 44px 4px 44px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CREAM};border:1px solid {SAND};border-radius:6px;">
                <tr>
                  <td style="padding:12px 18px;border-bottom:1px solid {SAND};font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:11px;letter-spacing:4px;color:{NAVY};">
                    &#9992;&#65039;&nbsp;&nbsp;POSTCARD &nbsp;&middot;&nbsp; PAR AVION
                  </td>
                </tr>
                <tr>
                  <td style="padding:22px 22px 26px 22px;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td class="stack-col" width="60%" valign="top" style="padding-right:14px;border-right:1px dashed {SAND};">
                          <div style="font-family:'Caveat',cursive;font-size:22px;line-height:1.35;color:{INK};">
                            &ldquo;{quote}&rdquo;
                          </div>
                          <div style="margin-top:14px;font-family:'Inter',Arial,sans-serif;font-size:11px;letter-spacing:2px;color:{INK};opacity:0.55;">
                            &mdash; from a fellow wanderer
                          </div>
                        </td>
                        <td class="stack-col" width="40%" valign="top" align="right" style="padding-left:14px;">
                          <div style="display:inline-block;border:2px solid {TERRACOTTA};padding:10px 8px;transform:rotate(3deg);">
                            <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:14px;letter-spacing:2px;color:{TERRACOTTA};line-height:1.1;">WANDERLY<br>POSTAGE</div>
                            <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:10px;letter-spacing:2px;color:{TERRACOTTA};margin-top:4px;opacity:0.75;">2026 &middot; \u20B90</div>
                          </div>
                          <div style="margin-top:10px;font-family:'Inter',Arial,sans-serif;font-size:10px;letter-spacing:2px;color:{INK};opacity:0.55;text-transform:uppercase;">
                            TO: {recipient_name}<br>
                            {destination}
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- FOOTER STAMP -->
          <tr>
            <td style="padding:28px 44px 34px 44px;background:{INK};text-align:center;margin-top:20px;">
              <div style="font-family:'Bebas Neue',Impact,Arial,sans-serif;font-size:22px;letter-spacing:6px;color:{CREAM};">
                WANDERLY&nbsp;&nbsp;//&nbsp;&nbsp;WHERE EVERY TRIP BECOMES A STORY
              </div>
              <div style="margin-top:10px;font-family:'Inter',Arial,sans-serif;font-size:11px;color:{SAND};opacity:0.7;letter-spacing:1px;">
                You received this because {organizer_name} added you to their trip. If it wasn't for you, feel free to ignore.
              </div>
            </td>
          </tr>

        </table>

        <!-- Tiny attribution outside card -->
        <div style="max-width:600px;width:100%;padding:14px 12px 0 12px;text-align:center;font-family:'Inter',Arial,sans-serif;font-size:10px;color:{INK};opacity:0.55;letter-spacing:1px;">
          &#9992;&#65039; Sent with terracotta &amp; wanderlust
        </div>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _plain_text(
    recipient_name: str,
    trip_name: str,
    organizer_name: str,
    destination: str,
    dates: str,
    accept_url: str,
    quote: str,
) -> str:
    return (
        f"PACK YOUR BAGS, {recipient_name}.\n\n"
        f"{organizer_name} just added you to {trip_name}. {destination} is calling.\n\n"
        f"  \u2708  LUGGAGE TAG\n"
        f"  WHERE:  {destination}\n"
        f"  WHEN:   {dates}\n"
        f"  TRIP:   {trip_name}\n"
        f"  HOST:   {organizer_name}\n\n"
        f"Join the trip: {accept_url}\n\n"
        f"See who's in \u00b7 Split expenses \u00b7 Book together \u00b7 Share the vibe\n\n"
        f'"{quote}"\n\n'
        f"\u2014 Wanderly // Where every trip becomes a story."
    )


# ------------------------------------------------------------------ SMTP send

async def send_invite_email(
    to_email: str,
    recipient_name: str,
    trip_name: str,
    organizer_name: str,
    destination: str,
    dates: str,
) -> dict:
    """Send the invite via Gmail SMTP over STARTTLS. Returns {'message_id': ...}."""
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pw = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_pw:
        raise RuntimeError("GMAIL_USER / GMAIL_APP_PASSWORD not set in backend/.env")

    hero = random.choice(INVITE_HERO_IMAGES)
    quote = random.choice(TRAVEL_QUOTES)
    accept_url = f"https://wanderly.app/invite/accept?token=DEMO_TOKEN_{uuid.uuid4().hex[:8]}"

    html_body = _render_html(
        recipient_name, trip_name, organizer_name, destination, dates, accept_url, hero, quote,
    )
    text_body = _plain_text(
        recipient_name, trip_name, organizer_name, destination, dates, accept_url, quote,
    )

    msg = EmailMessage()
    msg["From"] = f"Wanderly <{gmail_user}>"
    msg["To"] = to_email
    msg["Subject"] = f"\u2708\ufe0f Pack your bags \u2014 {trip_name}"
    msg["Message-ID"] = make_msgid(domain="wanderly.app")
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    log.info(
        "SMTP: sending invite email to=%s trip=%s from_gmail_user=%s html_size=%d",
        to_email, trip_name, gmail_user, len(html_body),
    )

    try:
        tls_ctx = ssl.create_default_context()
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=gmail_user,
            password=gmail_pw,
            tls_context=tls_ctx,
            timeout=30,
        )
    except aiosmtplib.SMTPAuthenticationError as e:
        log.error("SMTP auth failed. Check GMAIL_APP_PASSWORD. code=%s message=%s", e.code, e.message)
        raise
    except aiosmtplib.SMTPException as e:
        log.error("SMTP error while sending invite: %s", e)
        raise
    except Exception as e:  # network / TLS / timeout
        log.exception("Unexpected error while sending invite email: %s", e)
        raise

    log.info("SMTP: invite email sent successfully to=%s message_id=%s", to_email, msg["Message-ID"])
    return {"message_id": msg["Message-ID"]}
