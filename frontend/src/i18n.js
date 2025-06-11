// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  lng: 'en', // Язык по умолчанию
  fallbackLng: 'en', // Язык резервного копирования
  resources: {
    en: {
      translation: {
        welcome: 'Welcome!',
        home: 'Home Page',
        login: 'Login',
        logout: 'Logout',
      },
    },
    ru: {
      translation: {
        welcome: 'Добро пожаловать!',
        home: 'Главная страница',
        login: 'Войти',
        logout: 'Выйти',
      },
    },
  },
});

export default i18n;