"use client";

import { useI18n } from "@/lib/i18n";

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();

  return (
    <div className="flex items-center gap-0">
      <button
        onClick={() => setLocale("en")}
        className="px-2.5 py-1 transition-all duration-200"
        style={{
          fontSize: "14px",
          fontFamily: "'Cinzel', Georgia, serif",
          textTransform: "uppercase" as const,
          letterSpacing: "2px",
          fontWeight: 600,
          color: locale === "en" ? "#E6EDF3" : "rgba(255,255,255,0.35)",
          borderBottom: locale === "en" ? "2px solid rgba(194,58,46,0.6)" : "2px solid transparent",
          background: "transparent",
        }}
        onMouseEnter={(e) => {
          if (locale !== "en") (e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.6)";
        }}
        onMouseLeave={(e) => {
          if (locale !== "en") (e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.35)";
        }}
      >
        EN
      </button>
      <span style={{ color: "rgba(255,255,255,0.1)", fontSize: "14px" }}>/</span>
      <button
        onClick={() => setLocale("ru")}
        className="px-2.5 py-1 transition-all duration-200"
        style={{
          fontSize: "14px",
          fontFamily: "'Cinzel', Georgia, serif",
          textTransform: "uppercase" as const,
          letterSpacing: "2px",
          fontWeight: 600,
          color: locale === "ru" ? "#E6EDF3" : "rgba(255,255,255,0.35)",
          borderBottom: locale === "ru" ? "2px solid rgba(194,58,46,0.6)" : "2px solid transparent",
          background: "transparent",
        }}
        onMouseEnter={(e) => {
          if (locale !== "ru") (e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.6)";
        }}
        onMouseLeave={(e) => {
          if (locale !== "ru") (e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.35)";
        }}
      >
        RU
      </button>
    </div>
  );
}
