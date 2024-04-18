import i18next from "i18next";
import { createI18nStore } from "svelte-i18next";

import en from "./en";
import zhCN from "./zh-CN";

i18next.init({
  lng: "en",
  resources: {
    en: { translation: en },
    "zh-CN": { translation: zhCN },
  },
});

const supportedLanguages = [
  { display: "English", value: "en" },
  { display: "简体中文", value: "zh-CN" },
];

export default () => createI18nStore(i18next);

export { supportedLanguages };
