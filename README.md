# tg_bot_nails

## English

Telegram bot for nail studio booking with two roles:
- client: create/cancel booking, view own bookings
- master: manage schedule, see upcoming bookings, receive notifications

### Features

- booking flow: service -> date -> time -> master -> confirmation
- available times are calculated from real DB bookings
- fully booked days are hidden in calendar (empty cell, like weekend)
- booking confirmation stores data in both client and master booking tables
- clickable Telegram contact links (`@username` or `tg://user?id=...` fallback)
- client cancellation flow with inline confirmation buttons
- cancellation removes booking from both client and master tables
- master receives notification when a client creates or cancels booking
- master menu: work days, weekends, schedule, upcoming bookings

### Commands

General:
- `/start` - start bot
- `/info` - bot info

Client:
- `/new_entry` - create new booking
- `/list_of_entries` - show upcoming client bookings
- `/cancellation` - cancel selected booking

Master:
- `/master_info` - open master menu
- `/add_m` - add current user as master
- `/rem_m` - remove current master from DB

### Project structure

- `tg_bot/main_bot.py` - entry point, commands, router registration
- `tg_bot/new_entry_hendlers/` - client booking handlers and keyboards
- `tg_bot/users_handlers/` - client list/cancellation handlers
- `tg_bot/master_nails_handlers/` - master menu, schedule, client list
- `tg_bot/database/` - SQLAlchemy models and DB operations

### Tech stack

- Python 3.11+
- aiogram 3
- SQLAlchemy 2 (async)
- asyncpg
- PostgreSQL
- python-dotenv

### Setup

1. Clone repo and create virtual environment.
2. Install dependencies:

```bash
pip install aiogram sqlalchemy asyncpg greenlet python-dotenv
```

3. Create `.env` in project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db_name
```

4. Run bot:

```bash
python -m tg_bot.main_bot
```

On startup bot will:
- create DB tables if they do not exist
- add default services if `services` table is empty

### Notes

- If Telegram username is missing, contact link fallback uses `tg://user?id=...`.
- For master notifications to work, master should start chat with bot at least once.

---

## Русский

Telegram-бот для записи в nail-студию с двумя ролями:
- клиент: создать/отменить запись, посмотреть свои записи
- мастер: управлять графиком, смотреть будущие записи, получать уведомления

### Возможности

- сценарий записи: услуга -> дата -> время -> мастер -> подтверждение
- доступное время считается по реальным броням в БД
- полностью занятые дни скрываются в календаре (пустая ячейка, как выходной)
- при подтверждении запись сохраняется и в таблицу клиента, и в таблицу мастера
- кликабельные ссылки для связи (`@username` или fallback `tg://user?id=...`)
- сценарий отмены записи клиентом через inline-кнопки с подтверждением
- при отмене запись удаляется у клиента и у мастера
- мастер получает уведомления о новой записи и об отмене
- меню мастера: рабочие дни, выходные, график, будущие записи

### Команды

Общие:
- `/start` - запуск
- `/info` - информация о боте

Клиент:
- `/new_entry` - новая запись
- `/list_of_entries` - показать будущие записи клиента
- `/cancellation` - отмена выбранной записи

Мастер:
- `/master_info` - открыть меню мастера
- `/add_m` - добавить текущего пользователя как мастера
- `/rem_m` - удалить мастера из БД

### Структура проекта

- `tg_bot/main_bot.py` - точка входа, команды, регистрация роутеров
- `tg_bot/new_entry_hendlers/` - клиентские хендлеры записи и клавиатуры
- `tg_bot/users_handlers/` - хендлеры просмотра/отмены записей клиента
- `tg_bot/master_nails_handlers/` - меню мастера, график, список клиентов
- `tg_bot/database/` - модели SQLAlchemy и операции с БД

### Технологии

- Python 3.11+
- aiogram 3
- SQLAlchemy 2 (async)
- asyncpg
- PostgreSQL
- python-dotenv

### Запуск

1. Склонировать проект и создать виртуальное окружение.
2. Установить зависимости:

```bash
pip install aiogram sqlalchemy asyncpg greenlet python-dotenv
```

3. Создать `.env` в корне проекта:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db_name
```

4. Запустить бота:

```bash
python -m tg_bot.main_bot
```

При старте бот:
- создаст таблицы, если их еще нет
- добавит базовые услуги, если таблица `services` пустая

### Примечания

- Если у пользователя нет username, используется ссылка `tg://user?id=...`.
- Чтобы мастер получал уведомления, он должен хотя бы один раз написать боту.
