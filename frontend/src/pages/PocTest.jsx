import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TEMPLATES = [
  { value: "polaroid_scrapbook", label: "Polaroid Scrapbook" },
  { value: "magazine", label: "Magazine" },
  { value: "postcard", label: "Postcard" },
  { value: "filmstrip", label: "Filmstrip" },
  { value: "moodboard", label: "Moodboard" },
  { value: "film_photo", label: "Film Photo (vintage single)" },
];

function Section({ title, subtitle, children, testId }) {
  return (
    <div
      data-testid={testId}
      className="rounded-2xl p-6 sm:p-8 shadow-sm"
      style={{ background: "#ffffff", border: "1px dashed #E8D5B7" }}
    >
      <div className="mb-6">
        <div
          className="text-[11px] uppercase tracking-[0.3em] mb-2"
          style={{ color: "#C65D3A" }}
        >
          {title}
        </div>
        <div
          className="text-2xl sm:text-3xl"
          style={{ fontFamily: '"Playfair Display", Georgia, serif', color: "#2C2416" }}
        >
          {subtitle}
        </div>
      </div>
      {children}
    </div>
  );
}

function EmailSection() {
  const [form, setForm] = useState({
    to_email: "sayanbhatt2005@gmail.com",
    recipient_name: "Sayan",
    trip_name: "Goa Sunset Chase",
    organizer_name: "The Wanderly Crew",
    destination: "Goa, India",
    dates: "March 12 — March 16, 2026",
  });
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  const onSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setResult(null);
    try {
      const { data } = await axios.post(`${API}/test/send-invite-email`, form);
      setResult(data);
      toast.success("Invite sent — check inbox ✉️");
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || "Failed to send.";
      toast.error(msg);
      setResult({ error: msg });
    } finally {
      setBusy(false);
    }
  };

  const upd = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <Section
      testId="email-section"
      title="Section A"
      subtitle="Send test invite email"
    >
      <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="sm:col-span-2">
          <Label htmlFor="to_email">To email</Label>
          <Input
            id="to_email"
            data-testid="email-to-input"
            value={form.to_email}
            onChange={upd("to_email")}
            required
          />
        </div>
        <div>
          <Label htmlFor="recipient_name">Recipient name</Label>
          <Input
            id="recipient_name"
            data-testid="email-recipient-input"
            value={form.recipient_name}
            onChange={upd("recipient_name")}
            required
          />
        </div>
        <div>
          <Label htmlFor="organizer_name">Organizer</Label>
          <Input
            id="organizer_name"
            data-testid="email-organizer-input"
            value={form.organizer_name}
            onChange={upd("organizer_name")}
            required
          />
        </div>
        <div className="sm:col-span-2">
          <Label htmlFor="trip_name">Trip name</Label>
          <Input
            id="trip_name"
            data-testid="email-trip-input"
            value={form.trip_name}
            onChange={upd("trip_name")}
            required
          />
        </div>
        <div>
          <Label htmlFor="destination">Destination</Label>
          <Input
            id="destination"
            data-testid="email-destination-input"
            value={form.destination}
            onChange={upd("destination")}
            required
          />
        </div>
        <div>
          <Label htmlFor="dates">Dates</Label>
          <Input
            id="dates"
            data-testid="email-dates-input"
            value={form.dates}
            onChange={upd("dates")}
            required
          />
        </div>

        <div className="sm:col-span-2 flex items-center gap-3 mt-2">
          <Button
            type="submit"
            data-testid="email-send-button"
            disabled={busy}
            style={{ background: "#C65D3A", color: "#FAF3E7" }}
            className="rounded-full px-6"
          >
            {busy ? "Sending…" : "Send invite email"}
          </Button>
          {result?.message_id && (
            <span
              data-testid="email-success-msgid"
              className="text-xs opacity-70 truncate max-w-[380px]"
              title={result.message_id}
            >
              ✓ {result.message_id}
            </span>
          )}
          {result?.error && (
            <span data-testid="email-error-msg" className="text-xs" style={{ color: "#C65D3A" }}>
              {result.error}
            </span>
          )}
        </div>
      </form>
    </Section>
  );
}

function CollageSection() {
  const [files, setFiles] = useState([]);
  const [template, setTemplate] = useState("polaroid_scrapbook");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [previewUrls, setPreviewUrls] = useState([]);

  const onFiles = (e) => {
    const list = Array.from(e.target.files || []);
    setFiles(list);
    setPreviewUrls(list.map((f) => URL.createObjectURL(f)));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (files.length < 3 || files.length > 5) {
      toast.error("Upload between 3 and 5 images.");
      return;
    }
    setBusy(true);
    setResult(null);
    try {
      const fd = new FormData();
      files.forEach((f) => fd.append("files", f));
      const { data } = await axios.post(
        `${API}/test/generate-collage?template=${encodeURIComponent(template)}`,
        fd,
        { headers: { "Content-Type": "multipart/form-data" }, timeout: 180000 },
      );
      setResult(data);
      toast.success(`Collage ready — vibe: ${data.vibe}`);
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || "Failed.";
      toast.error(msg);
      setResult({ error: msg });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section
      testId="collage-section"
      title="Section B"
      subtitle="Generate Vibe Lab collage"
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <Label htmlFor="files">Upload 3–5 photos (JPEG / PNG / WEBP)</Label>
          <Input
            id="files"
            data-testid="collage-file-input"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            multiple
            onChange={onFiles}
          />
          {previewUrls.length > 0 && (
            <div
              data-testid="collage-thumbs"
              className="flex flex-wrap gap-2 mt-3"
            >
              {previewUrls.map((u, i) => (
                <img
                  key={i}
                  src={u}
                  alt=""
                  className="w-16 h-16 object-cover rounded-md"
                  style={{ border: "1px solid #E8D5B7" }}
                />
              ))}
            </div>
          )}
        </div>

        <div>
          <Label>Template</Label>
          <Select value={template} onValueChange={setTemplate}>
            <SelectTrigger data-testid="collage-template-select" className="w-full sm:w-80">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {TEMPLATES.map((t) => (
                <SelectItem
                  key={t.value}
                  value={t.value}
                  data-testid={`collage-template-option-${t.value}`}
                >
                  {t.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <Button
            type="submit"
            data-testid="collage-generate-button"
            disabled={busy}
            style={{ background: "#2C2416", color: "#FAF3E7" }}
            className="rounded-full px-6"
          >
            {busy ? "Composing…" : "Generate collage"}
          </Button>
          {result?.error && (
            <span data-testid="collage-error-msg" className="text-xs" style={{ color: "#C65D3A" }}>
              {result.error}
            </span>
          )}
        </div>
      </form>

      {result?.collage_base64 && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6" data-testid="collage-result">
          <div>
            <img
              data-testid="collage-image"
              src={result.collage_base64}
              alt="Generated collage"
              className="w-full rounded-xl shadow-md"
              style={{ maxWidth: 540, border: "1px solid #E8D5B7" }}
            />
            {result.collage_url && (
              <div className="mt-2 text-xs opacity-70 break-all">
                <a
                  data-testid="collage-open-link"
                  href={
                    result.collage_url.startsWith("http")
                      ? result.collage_url
                      : `${BACKEND_URL}${result.collage_url}`
                  }
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: "#C65D3A" }}
                >
                  Open PNG in new tab ↗
                </a>
              </div>
            )}
          </div>
          <div className="space-y-3">
            <div>
              <div className="text-[11px] uppercase tracking-[0.3em] opacity-60">Vibe</div>
              <div
                data-testid="collage-vibe"
                className="text-xl"
                style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
              >
                {result.vibe}
              </div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.3em] opacity-60">Caption</div>
              <div
                data-testid="collage-caption"
                className="text-lg"
                style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
              >
                “{result.caption}”
              </div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.3em] opacity-60">Quote</div>
              <div
                data-testid="collage-quote"
                className="text-base italic opacity-80"
              >
                {result.quote}
              </div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.3em] opacity-60">Dominant colors</div>
              <div className="flex gap-2 mt-2" data-testid="collage-colors">
                {(result.dominant_colors || []).map((c) => (
                  <div
                    key={c}
                    title={c}
                    className="w-8 h-8 rounded-md"
                    style={{ background: c, border: "1px solid rgba(0,0,0,0.08)" }}
                  />
                ))}
              </div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.3em] opacity-60">Template</div>
              <div data-testid="collage-template-used" className="text-sm">
                {result.template_used}
              </div>
            </div>
          </div>
        </div>
      )}
    </Section>
  );
}

export default function PocTest() {
  return (
    <div
      data-testid="poc-test-page"
      className="min-h-screen"
      style={{ background: "#FAF3E7", color: "#2C2416" }}
    >
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
        <div className="mb-10">
          <div
            className="text-[11px] uppercase tracking-[0.35em] mb-2"
            style={{ color: "#C65D3A" }}
          >
            Wanderly · POC
          </div>
          <h1
            className="text-4xl sm:text-5xl"
            style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            data-testid="poc-heading"
          >
            Phase 0 — <span className="italic" style={{ color: "#C65D3A" }}>de-risking</span>
          </h1>
          <p className="mt-3 opacity-70 text-sm sm:text-base max-w-xl">
            Test the two critical integrations before we build the app: Gmail invite emails and Vibe Lab collages.
          </p>
        </div>

        <div className="space-y-8">
          <EmailSection />
          <CollageSection />
        </div>

        <div className="mt-14 text-center text-xs opacity-50">
          Wanderly — Where every trip becomes a story.
        </div>
      </div>
    </div>
  );
}
