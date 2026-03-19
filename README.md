# Memory Core SDK

Universal memory engine for AI bots. 3 layers: Redis (Hot) + Qdrant (Warm) + Neo4j (Cold).

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

## API

| Method | Description |
|--------|-------------|
| `upsert(user_id, content)` | Save to memory (Hot+Warm+Cold) |
| `context(user_id, query)` | Retrieve relevant context |
| `remember(user_id, fact)` | Shortcut: save a fact |
| `recall(user_id, query)` | Shortcut: semantic search |
| `summarize(user_id)` | Summarize session into episode |
| `profile(user_id)` | Full user profile |
| `health()` | API health check |

## Links

- **Landing**: https://memorycore.ru
- **API Docs**: https://api.memorycore.ru/docs
- **Dashboard**: https://memorycore.ru/dashboard

## License

MIT - (c) 2025-2026 Otel Group
