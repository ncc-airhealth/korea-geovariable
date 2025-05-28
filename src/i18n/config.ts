
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import enTranslation from './en/translation';
import koTranslation from './ko/translation';

// Define a more compatible namespace type
declare module 'react-i18next' {
  interface CustomTypeOptions {
    // custom namespace type if you changed it
    defaultNS: 'translation';
    // custom resources type
    resources: {
      translation: typeof enTranslation;
    };
    // Make sure we can use any React node as children
    ReactNode: React.ReactNode;
  }
}

const resources = {
  en: {
    translation: enTranslation
  },
  ko: {
    translation: koTranslation
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'en', // Default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already escapes by default
    }
  });

export default i18n;
