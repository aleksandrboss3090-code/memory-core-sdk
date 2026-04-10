# Changelog

All notable changes to Memory Core will be documented in this file.

## [0.5.0] — 2026-04-10

### Added
- **Soft Delete** — записи перемещаются в корзину вместо физического удаления
- `forget()` — мягкое удаление записи (хранится 30 дней в корзине)
- `trash()` — просмотр корзины с отсчётом дней до автоудаления
- `restore()` — восстановление записей из корзины
- `purge()` — физическое удаление (необратимо, только записи старше 30 дней)
- Автоочистка корзины через cron (05:00 UTC, записи старше 30 дней)
- Qdrant index на `is_deleted` для быстрой фильтрации
- Дедупликация v1.2 — исключает soft-deleted записи из проверки

### Changed
- `delete()` теперь выполняет soft delete (is_deleted=true) вместо физического удаления
- Все read/search/browse endpoints автоматически исключают удалённые записи
- `dedup_service.py` v1.2 — must_not filter для is_deleted

### Fixed
- Дедупликация больше не блокирует обновление фактов через workflow forget→upsert

### Security
- Физическое удаление требует явного вызова purge()
- 30-дневное окно восстановления защищает от случайной потери данных

## [0.4.2] — 2026-03-20

### Added
- `search()` — семантический поиск по памяти
- `delete()` — удаление записей
- `export_data()` — экспорт данных (GDPR/FZ-152)
- `import_data()` — импорт записей
- `usage()` — текущее использование API
- `regenerate_key()` — перегенерация API ключа
- TypeScript definitions (JS SDK)
- AsyncMemoryClient (Python SDK)

## [0.4.0] — 2026-03-15

### Added
- Базовые методы: upsert, context, summarize, profile, stats, health
- Удобные методы: remember, recall
- Sync + Async клиенты
- MIT лицензия
- Публикация на npm и PyPI
