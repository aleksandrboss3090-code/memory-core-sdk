"""
Memory Core SDK — Универсальный движок памяти для AI-ботов.

Подключите за 3 строки:
    from memory_core import MemoryClient
    memory = MemoryClient("mc_live_...")
    memory.upsert(user_id="user_42", content="Люблю итальянскую кухню")

Docs: https://api.memorycore.ru/docs
Site: https://memorycore.ru
"""

from memory_core.client import MemoryClient, AsyncMemoryClient

__version__ = "0.3.3"
__all__ = ["MemoryClient", "AsyncMemoryClient"]
