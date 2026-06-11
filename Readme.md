# Comments SPA

SPA-застосунок для коментарів з підтримкою вкладених відповідей, real-time оновлень через WebSocket та завантаження файлів.

## Стек

- **Backend:** Django 5, Django REST Framework, Django Channels
- **Database:** PostgreSQL 16
- **Cache / Queue:** Redis 7 + Celery
- **Frontend:** Vanilla JS (без фреймворків)
- **Інфра:** Docker, Docker Compose

## Функціонал

- Додавання коментарів з валідацією на клієнті та сервері
- Вкладені відповіді (необмежена глибина)
- Сортування за іменем, email, датою
- Пагінація — 25 коментарів на сторінку, LIFO за замовчуванням
- CAPTCHA для захисту від ботів
- Завантаження зображень (JPG, GIF, PNG, макс. 320×240) та TXT файлів (макс. 100 КБ)
- Lightbox для перегляду зображень
- Тулбар для вставки HTML тегів (`<i>`, `<strong>`, `<code>`, `<a>`)
- Прев'ю коментаря без перезавантаження
- Real-time оновлення через WebSocket
- XSS захист через bleach
- JWT аутентифікація

## Структура проекту

```
comments_spa/
├── backend/
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── comments/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── consumers.py
│   │   └── tasks.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## Запуск

### 1. Клонування репозиторію

```bash
git clone <repo-url>
cd comments_spa
```

### 2. Налаштування змінних середовища

```bash
cp .env.example .env
```

За необхідності відредагуй `.env`.

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

Застосунок буде доступний на `http://localhost:8000`.

### 4. Локальний запуск (без Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запусти PostgreSQL і Redis локально, потім:
python manage.py migrate
python manage.py runserver

# В окремому терміналі:
celery -A config worker -l info
```

## API

| Метод | URL | Опис |
|---|---|---|
| GET | `/api/comments/` | Список кореневих коментарів |
| POST | `/api/comments/` | Створити коментар |
| GET | `/api/comments/<id>/` | Коментар з деревом відповідей |
| GET | `/api/comments/<id>/replies/` | Відповіді на коментар |

### Параметри запиту

```
GET /api/comments/?ordering=-created_at&page=2
```

Допустимі значення `ordering`: `user__username`, `-user__username`, `user__email`, `-user__email`, `created_at`, `-created_at`.

### WebSocket

```
ws://localhost:8000/ws/comments/
```

## Схема БД

```
User
  id, username, email, home_page, ip_address, user_agent, created_at

Comment
  id, user_id (FK → User), parent_id (FK → Comment), text, image, txt_file, created_at
```