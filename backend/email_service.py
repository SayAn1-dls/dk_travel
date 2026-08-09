"""Gmail SMTP + Pinterest-aesthetic HTML invite email."""

from __future__ import annotations

import logging
import os
import random
import ssl
import uuid
from email.message import EmailMessage
from email.utils import make_msgid

import aiosmtplib

from quotes import INVITE_HERO_IMAGES, TRAVEL_QUOTES

log = logging.getLogger(__name__)

# Wanderly palette
CREAM = "#FAF3E7"
SAND = "#E8D5B7"
TERRACOTTA = "#C65D3A"
SAGE = "#A8B89A"
INK = "#2C2416"


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
    """Bulletproof HTML email (tables + inline CSS) matching Pinterest travel aesthetic."""
    return f"""\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>You've been invited — {trip_name}</title>
<!--[if mso]><style>* {{ font-family: Georgia, serif !important; }}</style><![endif]-->
</head>
<body style="margin:0;padding:0;background:{CREAM};font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:{INK};">
  <span style="display:none !important;opacity:0;color:transparent;height:0;width:0;overflow:hidden;">{organizer_name} has invited you to {trip_name} in {destination} — {dates}.</span>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CREAM};">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(44,36,22,0.08);">

          <!-- Brand bar -->
          <tr>
            <td style="padding:20px 32px 8px 32px;background:{CREAM};">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="left" style="font-family:'Playfair Display',Georgia,serif;font-size:22px;font-weight:700;letter-spacing:0.5px;color:{TERRACOTTA};">
                    Wanderly
                  </td>
                  <td align="right" style="font-family:'Inter',Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:{INK};opacity:0.55;">
                    A Trip Invitation
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Hero image -->
          <tr>
            <td style="padding:0;">
              <img src="{hero_image}" alt="{destination}" width="600" style="display:block;width:100%;max-width:600px;height:auto;border:0;outline:none;text-decoration:none;">
            </td>
          </tr>

          <!-- Headline -->
          <tr>
            <td style="padding:44px 40px 8px 40px;text-align:center;">
              <div style="font-family:'Inter',Arial,sans-serif;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:{TERRACOTTA};margin-bottom:12px;">
                Hey {recipient_name} —
              </div>
              <h1 style="margin:0;font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:38px;line-height:1.15;color:{INK};letter-spacing:-0.5px;">
                You've been invited<br>
                <span style="font-style:italic;color:{TERRACOTTA};">to a trip</span> &#9992;&#65039;
              </h1>
              <p style="margin:18px 0 0 0;font-family:'Inter',Arial,sans-serif;font-size:15px;line-height:1.6;color:{INK};opacity:0.75;">
                <b style="color:{INK};opacity:1;">{organizer_name}</b> wants you along for the ride. Grab your camera, pack light, and say yes.
              </p>
            </td>
          </tr>

          <!-- Trip details card -->
          <tr>
            <td style="padding:32px 40px 8px 40px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CREAM};border:1px dashed {SAND};border-radius:12px;">
                <tr>
                  <td style="padding:24px 28px;">
                    <div style="font-family:'Caveat',cursive,'Playfair Display',Georgia,serif;font-size:30px;color:{TERRACOTTA};line-height:1;margin-bottom:6px;">
                      {trip_name}
                    </div>

                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:14px;">
                      <tr>
                        <td width="90" style="font-family:'Inter',Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:{INK};opacity:0.55;padding:6px 0;vertical-align:top;">
                          Where
                        </td>
                        <td style="font-family:'Playfair Display',Georgia,serif;font-size:20px;color:{INK};padding:4px 0;">
                          {destination}
                        </td>
                      </tr>
                      <tr>
                        <td style="font-family:'Inter',Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:{INK};opacity:0.55;padding:6px 0;vertical-align:top;">
                          When
                        </td>
                        <td style="font-family:'Playfair Display',Georgia,serif;font-size:20px;color:{INK};padding:4px 0;">
                          {dates}
                        </td>
                      </tr>
                      <tr>
                        <td style="font-family:'Inter',Arial,sans-serif;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:{INK};opacity:0.55;padding:6px 0;vertical-align:top;">
                          Host
                        </td>
                        <td style="font-family:'Playfair Display',Georgia,serif;font-size:20px;color:{INK};padding:4px 0;">
                          {organizer_name}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA button -->
          <tr>
            <td style="padding:28px 40px 8px 40px;text-align:center;">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin:0 auto;">
                <tr>
                  <td align="center" style="background:{TERRACOTTA};border-radius:999px;">
                    <a href="{accept_url}"
                       style="display:inline-block;padding:16px 40px;font-family:'Inter',Arial,sans-serif;font-size:15px;font-weight:600;letter-spacing:0.5px;color:#ffffff;text-decoration:none;border-radius:999px;">
                      Accept Invite &amp; Join Trip &#8594;
                    </a>
                  </td>
                </tr>
              </table>
              <div style="margin-top:12px;font-family:'Inter',Arial,sans-serif;font-size:12px;color:{INK};opacity:0.55;">
                Tap the button above — no login required to RSVP.
              </div>
            </td>
          </tr>

          <!-- Divider -->
          <tr><td style="padding:36px 40px 0 40px;"><div style="border-top:1px solid {SAND};height:1px;line-height:1px;font-size:1px;">&nbsp;</div></td></tr>

          <!-- Rotating travel quote -->
          <tr>
            <td style="padding:24px 40px 12px 40px;text-align:center;">
              <div style="font-family:'Caveat',cursive,'Playfair Display',Georgia,serif;font-size:26px;line-height:1.35;color:{SAGE};max-width:440px;margin:0 auto;">
                &ldquo; {quote} &rdquo;
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px 36px 40px;text-align:center;background:{CREAM};border-top:1px solid {SAND};">
              <div style="font-family:'Playfair Display',Georgia,serif;font-size:16px;font-weight:700;color:{TERRACOTTA};letter-spacing:0.5px;margin-bottom:4px;">
                Wanderly
              </div>
              <div style="font-family:'Inter',Arial,sans-serif;font-size:12px;color:{INK};opacity:0.55;font-style:italic;">
                Where every trip becomes a story.
              </div>
              <div style="margin-top:16px;font-family:'Inter',Arial,sans-serif;font-size:11px;color:{INK};opacity:0.45;">
                You received this invite from {organizer_name} via Wanderly. If this wasn't for you, feel free to ignore.
              </div>
            </td>
          </tr>

        </table>
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
        f"Hey {recipient_name},\n\n"
        f"{organizer_name} has invited you to a trip on Wanderly!\n\n"
        f"  Trip:        {trip_name}\n"
        f"  Destination: {destination}\n"
        f"  Dates:       {dates}\n"
        f"  Host:        {organizer_name}\n\n"
        f"Accept the invite: {accept_url}\n\n"
        f'"{quote}"\n\n'
        f"— Wanderly · Where every trip becomes a story."
    )


async def send_invite_email(
    to_email: str,
    recipient_name: str,
    trip_name: str,
    organizer_name: str,
    destination: str,
    dates: str,
) -> dict:
    """Send the invite email via Gmail SMTP over STARTTLS. Returns {'message_id': ...}."""
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
    msg["Subject"] = f"You're invited: {trip_name} \u2708\ufe0f"
    msg["Message-ID"] = make_msgid(domain="wanderly.app")
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    log.info(
        "SMTP: sending invite email to=%s trip=%s from_gmail_user=%s",
        to_email, trip_name, gmail_user,
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
