import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./locales/en.json";

/** Locales shipped with the OSS frontend build (dynamic import paths). */
export const SUPPORTED_LOCALES = new Set([
  "en",
  "ru",
  "de",
  "es",
  "fr",
  "ja",
  "pt",
  "zh-Hans",
]);

export function normalizeLanguage(lang: string): string {
  const code = lang.trim();
  if (!code || code === "en") return "en";
  if (SUPPORTED_LOCALES.has(code)) return code;
  if (code.startsWith("ru")) return "ru";
  if (code.startsWith("zh")) return "zh-Hans";
  const primary = code.split("-")[0];
  if (SUPPORTED_LOCALES.has(primary)) return primary;
  return "en";
}

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
  },
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export async function loadLanguage(lang: string): Promise<void> {
  const locale = normalizeLanguage(lang);
  if (locale === "en") {
    await i18n.changeLanguage("en");
    return;
  }
  if (i18n.hasResourceBundle(locale, "translation")) {
    await i18n.changeLanguage(locale);
    return;
  }
  try {
    const messages = await import(`./locales/${locale}.json`);
    i18n.addResourceBundle(locale, "translation", messages.default);
    await i18n.changeLanguage(locale);
  } catch {
    await i18n.changeLanguage("en");
  }
}

export default i18n;
