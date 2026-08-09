import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div
      data-testid="home-page"
      className="min-h-screen flex items-center justify-center px-6"
      style={{ background: "#FAF3E7", color: "#2C2416" }}
    >
      <div className="text-center max-w-xl">
        <div
          className="text-xs uppercase tracking-[0.35em] mb-5"
          style={{ color: "#C65D3A" }}
          data-testid="home-brand-eyebrow"
        >
          Wanderly
        </div>
        <h1
          className="text-4xl sm:text-5xl lg:text-6xl leading-[1.05] mb-6"
          style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
          data-testid="home-heading"
        >
          <span className="italic" style={{ color: "#C65D3A" }}>Under construction</span>
          <br />
          Something wander-ful is on the way.
        </h1>
        <p className="text-base sm:text-lg mb-10 opacity-70">
          A Pinterest-aesthetic travel super-app. Currently in Phase 0 — POC de-risking.
        </p>
        <Link
          to="/poc-test"
          data-testid="home-poc-link"
          className="inline-block px-8 py-3 rounded-full text-sm font-medium"
          style={{ background: "#C65D3A", color: "#FAF3E7" }}
        >
          Open POC Test Page →
        </Link>
      </div>
    </div>
  );
}
