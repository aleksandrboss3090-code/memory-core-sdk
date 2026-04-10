# Memory Core SDK

Universal memory engine for AI bots. 3 layers: Redis (Hot) + Qdrant (Warm) + Neo4j (Cold).

**FZ-152 compliant** — all personal data stored in Russia.

## Quick Start

```bash
pip install memorycore-ai
```

```python
from memory_core import MemoryClient

memory = MemoryClient("mc_live_...")

# Bot remembers
memory.upsert(user_id="user_42", content="Люблю итальянскую кухню")

# Bot recalls
ctx = memory.context(user_id="user_42", query="что заказать на ужин?")
# → Hot: fresh messages
# → Warm: "итальянская кухня" (score: 0.82)
# → Cold: user knowledge graph
```

## Async (for aiogram, FastAPI)

```bash
pip install memorycore-ai[async]
```

```python
from memory_core import AsyncMemoryClient

memory = AsyncMemoryClient("mc_live_...", bot_id="my_bot")

await memory.upsert(user_id="user_42", content="Предпочитает SPA")
ctx = await memory.context(user_id="user_42", query="что предложить?")
```

## API Methods

### Core

| Method | Description |
|--------|-------------|
| `upsert(user_id, content)` | Save to memory (Hot+Warm+Cold) |
| `context(user_id, query)` | Retrieve relevant context |
| `remember(user_id, fact)` | Shortcut: save a fact |
| `recall(user_id, query)` | Shortcut: semantic search |
| `summarize(user_id)` | Summarize session into episode |
| `profile(user_id)` | Full user profile |
| `health()` | API health check |

### New in v0.5.0 (Soft Delete)

| Method | Description |
|--------|-------------|
| `forget(episode_id or user_id)` | Soft delete to trash (30-day retention) |
| `trash(user_id)` | View deleted records in trash |
| `restore(episode_ids or user_id)` | Restore from trash |
| `purge(user_id)` | Permanently delete (IRREVERSIBLE) |

### New in v0.4.2

| Method | Description |
|--------|-------------|
| `search(user_id, query)` | Semantic search with filters |
| `delete(user_id, memory_id)` | Delete memory entries |
| `usage()` | API usage & rate limits |
| `export_data(user_id)` | Export user data (GDPR/FZ-152) |
| `import_data(user_id, records)` | Bulk import records |
| `regenerate_key()` | Regenerate API key |

## Examples

### Semantic Search

```python
results = memory.search(
    user_id="user_42",
    query="итальянская еда",
    limit=5,
    memory_type="fact"
)
for item in results["results"]:
    print(f"{item['content']} (score: {item['score']:.2f})")
```

### Check Usage & Limits

```python
usage = memory.usage()
print(f"Plan: {usage['plan']}")
print(f"Used: {usage['used']}/{usage['limit']}")
print(f"Remaining: {usage['remaining']}")
```

### Delete Memory

```python
# Delete specific entry
memory.delete(user_id="user_42", memory_id="uuid-here")

# Delete all facts
memory.delete(user_id="user_42", memory_type="fact")

# Delete ALL user data
memory.delete(user_id="user_42", delete_all=True)
```

### Soft Delete (v0.5.0)

Soft Delete - safe deletion with 30-day recovery window.

```python
# Soft delete one record (move to trash for 30 days)
memory.forget(episode_id="uuid-record")

# Soft delete ALL user records (move to trash for 30 days)
memory.forget(user_id="user_42")

# View trash - see deleted records with remaining retention days
trash = memory.trash(user_id="user_42")
for item in trash["trash"]:
    print(f"ID: {item['id']}, Days left: {item['days_remaining']}")

# Restore from trash
memory.restore(episode_ids=["uuid1", "uuid2"])

# Restore ALL user records from trash
memory.restore(user_id="user_42")

# Permanently purge from trash (IRREVERSIBLE!)
memory.purge(user_id="user_42")  # Only records older than 30 days
memory.purge(user_id="user_42", force_all=True)  # ALL records (even fresh ones!)
```

### Export / Import (GDPR/FZ-152)

```python
# Export
data = memory.export_data("user_42", format="json")
print(f"Exported {data['total']} records")

# Import
memory.import_data("user_42", records=[
    {"content": "Loves Italian food", "memory_type": "fact"},
    {"content": "Prefers morning meetings", "memory_type": "preference"},
])
```

## Rate Limit Headers

Every API response includes these headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Monthly limit for your plan |
| `X-RateLimit-Remaining` | Requests remaining |
| `X-RateLimit-Used` | Requests used this month |
| `X-RateLimit-Reset` | Unix timestamp of reset |

## Plans

| Plan | Requests/month | Price |
|------|---------------|-------|
| Free | 1,000 | 0 ₽ |
| Starter | 10,000 | 990 ₽ |
| Pro | 50,000 | 4,900 ₽ |
| Business | 200,000 | 14,900 ₽ |

## Links

- **Landing**: https://memorycore.ru
- **API Docs**: https://api.memorycore.ru/docs
- **Dashboard**: https://memorycore.ru/dashboard
- **Cabinet**: https://memorycore.ru/cabinet/

## License

MIT - (c) 2025-2026 Otel Group
