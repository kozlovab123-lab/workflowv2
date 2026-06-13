import "./i18n";
import { loadLanguage, normalizeLanguage } from "./i18n";
import ReactDOM from "react-dom/client";
import reportWebVitals from "./reportWebVitals";

import "./style/classes.css";
// @ts-ignore
import "./style/index.css";
// @ts-ignore
import "./App.css";
import "./style/applies.css";

// @ts-ignore
import App from "./customization/custom-App";

const detectedLang = normalizeLanguage(
  localStorage.getItem("languagePreference") ||
    navigator.language ||
    "en",
);

function mountApp() {
  const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement,
  );
  root.render(<App />);
  reportWebVitals();
}

loadLanguage(detectedLang).then(mountApp).catch(mountApp);
