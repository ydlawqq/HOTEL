# 🤖 Telegram-бот для работы с PDF-документами

Бот, который умеет:

- 📝 **Общаться с LLM** — обычный диалог в режиме «болталки» (Mistral Large).
- 📄 **Принимать PDF-файлы** от пользователя, извлекать из них текст и индексировать в векторную базу Qdrant.
- 🔍 **Искать по загруженным документам** — RAG-поиск: запрос переписывается, делается семантический поиск по релевантным чанкам и LLM отвечает только на основе найденного контекста.

---

## 🚀 Стек технологий

| Слой              | Библиотеки                                                                 |
|-------------------|----------------------------------------------------------------------------|
| API / Webhook     | FastAPI, Uvicorn                                                           |
| Telegram Bot      | aiogram 3 (FSM-состояния)                                                   |
| Оркестрация       | LangGraph (граф с нодами и условными переходами)                            |
| LLM               | LangChain + Mistral AI (`mistral-small`, `mistral-large`), опционально Ollama |
| RAG               | LlamaIndex, Qdrant (векторная БД), SentenceSplitter                        |
| База данных       | PostgreSQL, SQLAlchemy (async)                                              |
| Распознавание PDF | pypdf                                                                      |

---

## 📁 Структура проекта

```
.
├── app/
│   ├── endpoint.py               # FastAPI приложение + webhook + обработчики aiogram
│   ├── graph_main.py             # Сборка графа LangGraph
│   ├── nodes/
│   │   ├── agents.py             # LLM и эмбеддинги (Mistral, Ollama)
│   │   └── node_funcs.py         # Ноды графа (инициализация, PDF, диалог, поиск)
│   └── utils/
│       ├── classes.py            # TypedDict состояния графа
│       ├── prompts.py            # Промпты
│       ├── some_attributs_for_bot.py  # Клавиатуры и FSM-состояния
│       └── support_functions.py  # Работа с PDF, ретривер чанков
├── Postgres/
│   ├── engine.py                # Async-подключение к PostgreSQL
│   ├── models.py                # ORM-модели (Users, Chat, Documents)
│   └── repos/                   # Репозитории (user, chat, documents)
├── llamaindex/
│   └── vectors_bd.py            # Векторная БД Qdrant: storage context и index
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Как это работает

Приложение поднимает FastAPI-сервер, который через **webhook** принимает обновления от Telegram. Сообщение обрабатывается диспетчером aiogram, а затем разные типы действий маршрутизируются через **граф LangGraph**:

```
get_user ──────→ write_in_vbd ──→ final     (загрузка PDF)
   │
   ├────────────  talk                        (обычный диалог)
   └────────────→ rewrite ──→ search          (поиск по документам)
```

1. **`init_user`** — находит пользователя в БД, подгружает его историю сообщений.
2. В зависимости от состояния FSM (`FileStates`):
   - **`waiting_for_file`** → нода **`write_in_vbd`**: скачивает PDF, извлекает текст, разбивает на чанки и добавляет в Qdrant. После — `final` с подтверждением.
   - **`talking`** → нода **`talk`**: обычное общение с LLM (Mistral Large) с учётом истории.
   - **`waiting_for_text_search`** → нода **`rewrite`** переписывает запрос под семантический поиск, далее нода **`search`** через ретривер MMR подбирает чанки и строит ответ исключительно по контексту.

---

## 🛠 Установка и запуск

### 1. Требования
- Python 3.11+
- PostgreSQL (пример запуска ниже)
- Qdrant (векторная БД) — запущен на `http://127.0.0.1:6333`

### 2. Переменные окружения

Создайте файл `.env` в корне проекта (он уже в `.gitignore`):

```bash
# Telegram
token_tg=123456:your-bot-token
WEBHOOK_URL=https://your-public-domain.com

# PostgreSQL
engine=postgresql+asyncpg://user:password@localhost:5432/ai_agent

# Mistral AI (https://console.mistral.ai)
mistral=your-mistral-api-key

# Qdrant (опционально)
QDRANT_URL=http://127.0.0.1:6333
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск

```bash
uvicorn app.endpoint:app --host 0.0.0.0 --port 8000
```

При старте приложение:
- регистрирует вебхук Telegram на `{WEBHOOK_URL}/webhook`;
- создаёт таблицы в PostgreSQL;
- создаёт коллекцию `docs` в Qdrant (если её нет).

### 5. Запуск через Docker

```bash
docker build -t tg-pdf-bot .
docker run --env-file .env -p 8000:8000 tg-pdf-bot
```

---

## 🧩 Использование бота

1. Отправьте боту команду `/start` — появится клавиатура.
2. Нажмите **«Загрузить документ»** и пришлите PDF — текст документа будет проиндексирован.
3. Нажмите **«Искать по вашим файлам»** и задайте вопрос — бот найдёт ответ в ваших документах.
4. В остальном просто общайтесь — бот отвечает как обычный ассистент.

> 🔒 Каждый пользователь ищет только по своим загруженным файлам: фильтры поиска учитывают `user_id`.

---

## 📌 Примечания

- Загрузка документов рассчитана на PDF (по интерфейсу, но жёсткая фильтрация по типу не реализована).
- По умолчанию используется **MMR**-ретривер с `k=3`.
- Поле `engine` — асинхронная строка подключения `postgresql+asyncpg://...`.
- `Dockerfile` основан на `python:3.11-slim`, но код совместим с Python 3.9+.

---

## 📄 Лицензия

Проект распространяется без явной лицензии. Используйте на свой страх и риск.