import { useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { loadLanguage } from "@/i18n";
import { Button } from "@/components/ui/button";
import { useTypesStore } from "@/stores/typesStore";
import { cn } from "@/utils/utils";

const UI_LANGUAGES = [
  { code: "en", label: "EN" },
  { code: "ru", label: "RU" },
] as const;

type LanguageToggleProps = {
  className?: string;
};

export function LanguageToggle({ className }: LanguageToggleProps) {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const setTypes = useTypesStore((state) => state.setTypes);

  const currentLanguage = i18n.language?.startsWith("ru") ? "ru" : "en";

  const handleChange = async (code: string) => {
    if (code === currentLanguage) return;
    await loadLanguage(code);
    i18n.changeLanguage(code);
    localStorage.setItem("languagePreference", code);
    setTypes({});
    queryClient.invalidateQueries({ queryKey: ["useGetTypes"] });
  };

  return (
    <div
      role="group"
      aria-label={t("settings.languageSelectAriaLabel")}
      className={cn(
        "flex items-center rounded-md border border-border bg-muted p-0.5 text-xs font-medium",
        className,
      )}
      data-testid="language-toggle"
    >
      {UI_LANGUAGES.map((lang) => (
        <Button
          key={lang.code}
          unstyled
          type="button"
          onClick={() => handleChange(lang.code)}
          className={cn(
            "rounded px-2 py-1 transition-colors",
            currentLanguage === lang.code
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
          data-testid={`language-toggle-${lang.code}`}
        >
          {lang.label}
        </Button>
      ))}
    </div>
  );
}

export default LanguageToggle;
