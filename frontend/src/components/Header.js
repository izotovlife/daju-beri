// src/components/Header.js
import React from 'react';
import { useTranslation } from 'react-i18next';

function Header() {
  const { t } = useTranslation(); // получаем функцию перевода

  return (
    <header>
      <h1>{t('welcome')} - {t('home')}</h1>
    </header>
  );
}

export default Header;