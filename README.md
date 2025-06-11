# Daju Beri 🎁

Веб-платформа для сбора и отображения акционных товаров с маркетплейсов (Ozon, Wildberries, Lamoda).

## 🚀 Технологии

- Python 3.11+
- Django
- Django REST Framework
- PostgreSQL
- Celery + Redis
- Playwright (для парсинга)
- React (фронтенд)

## ⚙️ Установка

```bash
git clone https://github.com/ТВОЙ_ЛОГИН/daju-beri.git
cd daju-beri/backend
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # Создай .env файл на основе примера
python manage.py migrate
python manage.py runserver
