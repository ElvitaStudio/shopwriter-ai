# ShopWriter AI — Claude Code Spec

## Обзор проекта

**Продукт:** ShopWriter AI — Telegram Mini App + бот для генерации карточек товаров с помощью AI  
**Аудитория:** Продавцы на маркетплейсах (Rozetka, Prom.ua, Wildberries, Etsy)  
**Языки:** RU / UA / EN  
**Монетизация:** Токенная модель + Telegram Stars + Monobank  
**Стек:** Next.js 14 App Router + TypeScript + Tailwind + FastAPI + SQLite + aiogram + Claude API  
**Деплой:** VPS 185.219.83.199, PM2 + Nginx  
**Порты:** Frontend — 3008, Backend — 8008  

---

## Структура проекта

```
shopwriter/
├── frontend/          # Next.js 14 Mini App
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Главная / выбор платформы
│   │   ├── generate/page.tsx     # Генератор карточки
│   │   ├── history/page.tsx      # История карточек
│   │   ├── profile/page.tsx      # Профиль + баланс
│   │   ├── tokens/page.tsx       # Купить токены
│   │   ├── referral/page.tsx     # Партнёрка
│   │   └── globals.css
│   ├── components/
│   │   ├── PlatformSelector.tsx
│   │   ├── CardForm.tsx
│   │   ├── CardResult.tsx
│   │   ├── TokenBalance.tsx
│   │   ├── LanguageSwitcher.tsx
│   │   └── ui/
│   ├── lib/
│   │   ├── api.ts
│   │   ├── telegram.ts           # Telegram WebApp SDK
│   │   └── i18n.ts               # Переводы RU/UA/EN
│   └── public/
│
├── backend/           # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py           # SQLite + SQLAlchemy
│   │   ├── models.py
│   │   ├── routers/
│   │   │   ├── cards.py          # Генерация карточек
│   │   │   ├── users.py          # Профиль, баланс
│   │   │   ├── tokens.py         # Покупка токенов
│   │   │   └── referral.py       # Партнёрка
│   │   ├── services/
│   │   │   ├── claude_service.py # Claude API
│   │   │   └── payment_service.py
│   │   └── config.py
│   ├── .env
│   └── requirements.txt
│
└── bot/               # aiogram
    ├── bot.py
    ├── handlers/
    │   ├── start.py
    │   ├── menu.py
    │   ├── support.py
    │   └── admin.py
    └── keyboards/
        └── main_menu.py
```

---

## База данных (SQLite)

### Таблица users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    language TEXT DEFAULT 'ru',  -- ru / ua / en
    tokens INTEGER DEFAULT 5,    -- 5 бесплатных на старте
    referral_code TEXT UNIQUE,
    referred_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица cards
```sql
CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,       -- rozetka/prom/wildberries/etsy/universal
    input_text TEXT,
    image_path TEXT,
    result_title TEXT,
    result_description TEXT,
    result_characteristics TEXT,
    result_tags TEXT,
    tokens_spent INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Таблица transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,           -- purchase/referral/bonus/spend
    amount INTEGER NOT NULL,      -- токены
    description TEXT,
    payment_method TEXT,          -- stars/monobank
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Backend API (FastAPI)

### POST /api/cards/generate
Генерация карточки товара

**Request:**
```json
{
    "telegram_id": 123456,
    "platform": "rozetka",
    "product_name": "Кроссовки Nike Air Max",
    "category": "Обувь",
    "key_features": "белые, размер 42, кожа",
    "language": "ru",
    "image_base64": "..."  // опционально
}
```

**Response:**
```json
{
    "card_id": 1,
    "title": "...",
    "description": "...",
    "characteristics": [...],
    "seo_tags": [...],
    "tokens_left": 4
}
```

**Логика:**
1. Проверить баланс токенов (минимум 1)
2. Если есть фото — описать через Claude Vision
3. Сгенерировать карточку через Claude API
4. Списать 1 токен
5. Сохранить в БД
6. Вернуть результат

### GET /api/users/{telegram_id}
Профиль пользователя + баланс

### GET /api/cards/history/{telegram_id}
История карточек пользователя (последние 20)

### POST /api/tokens/purchase
Покупка токенов (Telegram Stars)

### GET /api/referral/{telegram_id}
Реферальная ссылка + статистика

### POST /api/referral/activate
Активация реферального кода при /start

---

## Claude API — промпты

### Системный промпт (claude_service.py)

```python
SYSTEM_PROMPTS = {
    "ru": """Ты эксперт по написанию продающих карточек товаров для маркетплейсов.
Отвечай ТОЛЬКО в формате JSON без markdown и лишних символов.
Пиши убедительно, с выгодами для покупателя, SEO-оптимизированно.""",

    "ua": """Ти експерт з написання продаючих карток товарів для маркетплейсів.
Відповідай ТІЛЬКИ у форматі JSON без markdown та зайвих символів.
Пиши переконливо, з вигодами для покупця, SEO-оптимізовано.""",

    "en": """You are an expert in writing high-converting product listings for marketplaces.
Reply ONLY in JSON format without markdown or extra characters.
Write persuasively, focusing on buyer benefits, SEO-optimized."""
}

PLATFORM_PROMPTS = {
    "rozetka": "Формат для Rozetka: название до 100 символов, описание 500-1000 символов, 5-10 характеристик, 10-15 SEO-тегов на русском/украинском",
    "prom": "Формат для Prom.ua: название до 120 символов, описание 300-800 символов, характеристики таблицей, теги через запятую",
    "wildberries": "Формат для Wildberries: название с ключевыми словами до 100 символов, описание 1000-2000 символов, 30 тегов",
    "etsy": "Format for Etsy: title up to 140 chars with keywords, description 500-1500 chars with story, 13 tags in English",
    "universal": "Универсальный формат: краткое название, развернутое описание, характеристики, теги"
}

USER_PROMPT_TEMPLATE = """
Платформа: {platform}
Товар: {product_name}
Категория: {category}
Особенности: {key_features}
{image_description}

Верни JSON:
{{
    "title": "название товара",
    "description": "описание товара",
    "characteristics": [
        {{"name": "Материал", "value": "Кожа"}},
        ...
    ],
    "seo_tags": ["тег1", "тег2", ...]
}}
"""
```

---

## Токенная модель

| Действие | Токены |
|----------|--------|
| Регистрация | +5 |
| Подписка на канал | +10 |
| Реферал (пригласил друга) | +3 |
| Реферал (был приглашён) | +3 |
| Генерация карточки (обычная) | -1 |
| Генерация с фото (Vision) | -2 |

### Пакеты токенов (Telegram Stars)

| Пакет | Токены | Stars | Цена ~USD |
|-------|--------|-------|-----------|
| Старт | 20 | 50 | $1 |
| Базовый | 100 | 200 | $4 |
| Про | 500 | 800 | $16 |
| Бизнес | 1000 | 1400 | $28 |

---

## aiogram Бот

### /start handler
```python
async def start_handler(message: Message):
    # 1. Проверить реферальный код в deep link (?start=REF_CODE)
    # 2. Зарегистрировать пользователя в БД
    # 3. Начислить токены рефереру и новому юзеру если есть реферал
    # 4. Показать приветствие с кнопкой открыть Mini App
    # 5. Показать главное меню
```

### Главное меню (Reply Keyboard — 8 кнопок)
```
[ ✍️ Создать карточку ]  [ 🖼 Загрузить фото ]
[ 💡 Примеры карточек ]  [ 📦 Мои карточки  ]
[ 👤 Мой профиль      ]  [ ⚡️ Купить токены ]
[ 🤝 Партнёрка        ]  [ 🆘 Поддержка     ]
```

Локализация кнопок по языку пользователя (RU/UA/EN).

### Handlers
- **✍️ Создать карточку** → открывает Mini App на /generate
- **🖼 Загрузить фото** → просит отправить фото, затем Mini App
- **💡 Примеры** → показывает 3 примера карточек для разных платформ
- **📦 Мои карточки** → открывает Mini App на /history
- **👤 Мой профиль** → баланс токенов + статистика
- **⚡️ Купить токены** → открывает Mini App на /tokens
- **🤝 Партнёрка** → реферальная ссылка + сколько заработал
- **🆘 Поддержка** → кнопка ссылка на @support или личку

---

## Frontend Mini App (Next.js 14)

### layout.tsx
```tsx
// Инициализация Telegram WebApp SDK
// Применение темы Telegram (dark/light)
// Глобальные стили под Telegram
```

### Главная страница (/)
- Логотип + название ShopWriter AI
- Баланс токенов (из API)
- 5 кнопок платформ: Rozetka / Prom / Wildberries / Etsy / Universal
- При выборе → переход на /generate?platform=rozetka

### Страница генератора (/generate)
1. Шаг 1: Название товара (input)
2. Шаг 2: Категория (select или input)
3. Шаг 3: Ключевые особенности (textarea)
4. Шаг 4: Фото товара (опционально, upload)
5. Кнопка "Создать карточку" → POST /api/cards/generate
6. Лоадер во время генерации
7. Результат: title / description / characteristics / tags
8. Кнопки: "Копировать всё" / "Скопировать описание" / "Скачать TXT"

### История (/history)
- Список карточек с датой и платформой
- Клик → разворачивает карточку
- Кнопка копировать

### Профиль (/profile)
- Аватар + имя из Telegram
- Баланс токенов
- Количество созданных карточек
- Выбор языка (RU/UA/EN)
- Дата регистрации

### Токены (/tokens)
- Текущий баланс
- 4 пакета с кнопками
- Оплата через Telegram Stars (invokePayment)
- История транзакций

### Партнёрка (/referral)
- Реферальная ссылка с кнопкой "Поделиться"
- Количество приглашённых
- Заработано токенов
- Условия: +3 токена за каждого приглашённого

---

## i18n (lib/i18n.ts)

```typescript
const translations = {
  ru: {
    title: "ShopWriter AI",
    generate: "Создать карточку",
    platform_select: "Выберите платформу",
    product_name: "Название товара",
    category: "Категория",
    features: "Ключевые особенности",
    photo: "Фото товара (необязательно)",
    create_btn: "Создать карточку",
    copy_all: "Копировать всё",
    tokens_left: "Токенов осталось",
    // ...
  },
  ua: { /* украинские переводы */ },
  en: { /* английские переводы */ }
}
```

---

## Nginx конфиг

```nginx
# /etc/nginx/sites-available/shopwriter

server {
    server_name shopwriter.botapps.pro;

    location / {
        proxy_pass http://localhost:3008;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://localhost:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## PM2 (ecosystem.config.js)

```javascript
module.exports = {
  apps: [
    {
      name: 'shopwriter-frontend',
      cwd: '/root/shopwriter/frontend',
      script: 'npm',
      args: 'start',
      env: { PORT: 3008, NODE_ENV: 'production' }
    },
    {
      name: 'shopwriter-backend',
      cwd: '/root/shopwriter/backend',
      script: '.venv/bin/python',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8008',
      env: { PYTHONPATH: '/root/shopwriter/backend' }
    },
    {
      name: 'shopwriter-bot',
      cwd: '/root/shopwriter/bot',
      script: '.venv/bin/python',
      args: 'bot.py'
    }
  ]
}
```

---

## .env (backend)

```
TELEGRAM_BOT_TOKEN=
CLAUDE_API_KEY=
DATABASE_URL=sqlite:///./shopwriter.db
MINI_APP_URL=https://shopwriter.botapps.pro
SUPPORT_USERNAME=@your_support
CHANNEL_USERNAME=@shopwriter_hub
ADMIN_TELEGRAM_ID=
```

---

## MVP Scope (Phase 1)

**Включить:**
- [ ] Регистрация + токены на старте
- [ ] Генерация карточки по тексту (без фото)
- [ ] 5 платформ
- [ ] 3 языка
- [ ] Покупка токенов (Telegram Stars)
- [ ] История карточек
- [ ] Реферальная система
- [ ] Меню бота (8 кнопок)

**Отложить на Phase 2:**
- [ ] Генерация с фото (Vision)
- [ ] Monobank оплата
- [ ] Массовая генерация (загрузить Excel → получить все карточки)
- [ ] API для интеграции в сторонние сервисы
- [ ] Админ-панель

---

## Команды деплоя

```bash
# Frontend
cd /root/shopwriter/frontend
npm install
npm run build
pm2 restart shopwriter-frontend

# Backend
cd /root/shopwriter/backend
pip install -r requirements.txt --break-system-packages
pm2 restart shopwriter-backend

# Bot
pm2 restart shopwriter-bot

# Nginx
certbot --nginx -d shopwriter.botapps.pro
nginx -t && systemctl reload nginx
```
