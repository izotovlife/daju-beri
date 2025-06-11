//C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\frontend\src\index.js

// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import i18n from './i18n'; // импортировали файл i18n.js
import { I18nextProvider } from 'react-i18next'; // импортируем провайдера

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <I18nextProvider i18n={i18n}> {/* обернули наше приложение */ }
      <App />
    </I18nextProvider>
  </React.StrictMode>
);

// остальное остается неизменным
reportWebVitals();
