"""
Memory Core SDK — Python Client v0.4.2
Sync (requests) + Async (httpx) клиенты для Memory Core API.

Автор: Алита (Claude) для семьи Науменко
Продукт: ООО «Отель Групп»

Changelog v0.4.2:
  - search() — семантический поиск по памяти
  - delete() — удаление записей
  - export_data() — экспорт данных пользователя
  - import_data() — импорт данных пользователя
  - usage() — текущее использование API (rate limits)
  - regenerate_key() — перегенерация API ключа
"""

from typing import Optional, Any, List, Dict
import json


# === SYNC CLIENT (requests) ===

class MemoryClient:
    """
    Синхронный клиент Memory Core API.

    Использование:
        from memory_core import MemoryClient

        memory = MemoryClient("mc_live_...")

        # Сохранить
        memory.upsert(user_id="user_42", content="Люблю итальянскую кухню")

        # Вспомнить
        ctx = memory.context(user_id="user_42", query="что заказать на ужин?")
        print(ctx["warm_episodes"])

        # Семантический поиск (v0.4.2)
        results = memory.search(user_id="user_42", query="еда", limit=5)

        # Использование API (v0.4.2)
        usage = memory.usage()
        print(f"Использовано: {usage['used']}/{usage['limit']}")
    """

    DEFAULT_URL = "https://api.memorycore.ru/api/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        bot_id: str = "default",
        timeout: float = 15.0,
    ):
        """
        Args:
            api_key: API-ключ (получите на memorycore.ru)
            base_url: URL API (по умолчанию https://api.memorycore.ru/api/v1)
            bot_id: ID вашего бота (для разделения контекстов)
            timeout: таймаут запросов в секундах
        """
        try:
            import requests
        except ImportError:
            raise ImportError(
                "Для MemoryClient нужен пакет requests: pip install requests"
            )

        self._api_key = api_key
        self._base_url = (base_url or self.DEFAULT_URL).rstrip("/")
        self._bot_id = bot_id
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        })

    def _post(self, path: str, data: dict) -> dict:
        """POST запрос к API."""
        resp = self._session.post(
            f"{self._base_url}{path}",
            json=data,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str, params: dict = None) -> dict:
        """GET запрос к API."""
        resp = self._session.get(
            f"{self._base_url}{path}",
            params=params,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str, data: dict = None) -> dict:
        """DELETE запрос к API."""
        resp = self._session.delete(
            f"{self._base_url}{path}",
            json=data,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # === ОСНОВНЫЕ МЕТОДЫ ===

    def upsert(
        self,
        user_id: str,
        content: str,
        bot_id: str = None,
        memory_type: str = "message",
        session_id: str = None,
        metadata: dict = None,
        importance: float = 0.5,
    ) -> dict:
        """
        Сохранить запись в память.

        Args:
            user_id: ID пользователя (telegram_id, email, etc.)
            content: Текст для запоминания
            bot_id: ID бота (по умолчанию self.bot_id)
            memory_type: Тип записи (message, fact, episode, preference, entity)
            session_id: ID сессии (для группировки)
            metadata: Дополнительные данные
            importance: Важность 0-1

        Returns:
            {"status": "ok", "id": "uuid", "drums": {...}, "stored_in": [...]}
        """
        return self._post("/memory/upsert", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "content": content,
            "memory_type": memory_type,
            "session_id": session_id,
            "metadata": metadata or {},
            "importance": importance,
        })

    def context(
        self,
        user_id: str,
        query: str,
        bot_id: str = None,
        max_items: int = 10,
        include_hot: bool = True,
        include_warm: bool = True,
        include_cold: bool = False,
        min_similarity: float = 0.40,
    ) -> dict:
        """
        Получить контекст — релевантные воспоминания для бота.

        Args:
            user_id: ID пользователя
            query: Текущий запрос пользователя
            bot_id: ID бота
            max_items: Максимум результатов
            include_hot: Включить HOT (Redis, текущая сессия)
            include_warm: Включить WARM (Qdrant, семантический поиск)
            include_cold: Включить COLD (Neo4j, граф знаний)
            min_similarity: Минимальный score для WARM

        Returns:
            {
                "user_id": "...",
                "hot_messages": [...],
                "warm_episodes": [...],
                "cold_graph": {...},
                "drums": {...},
                "total_items": N
            }
        """
        return self._post("/memory/context", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "query": query,
            "max_items": max_items,
            "include_hot": include_hot,
            "include_warm": include_warm,
            "include_cold": include_cold,
            "min_similarity": min_similarity,
        })

    def search(
        self,
        user_id: str,
        query: str,
        bot_id: str = None,
        limit: int = 10,
        memory_type: str = None,
        min_score: float = 0.3,
    ) -> dict:
        """
        Семантический поиск по памяти пользователя (v0.4.2).

        Args:
            user_id: ID пользователя
            query: Поисковый запрос
            bot_id: ID бота
            limit: Максимум результатов
            memory_type: Фильтр по типу (message, fact, episode, preference)
            min_score: Минимальный score релевантности

        Returns:
            {"results": [...], "total": N, "query": "..."}
        """
        payload = {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "query": query,
            "limit": limit,
            "min_score": min_score,
        }
        if memory_type:
            payload["memory_type"] = memory_type
        return self._post("/memory/search", payload)

    def delete(
        self,
        user_id: str,
        memory_id: str = None,
        bot_id: str = None,
        memory_type: str = None,
        delete_all: bool = False,
    ) -> dict:
        """
        Удалить записи из памяти (v0.4.2).

        Args:
            user_id: ID пользователя
            memory_id: Конкретный ID записи (если нужно удалить одну)
            bot_id: ID бота
            memory_type: Удалить все записи этого типа
            delete_all: Удалить ВСЮ память пользователя (осторожно!)

        Returns:
            {"status": "deleted", "count": N}
        """
        payload = {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
        }
        if memory_id:
            payload["memory_id"] = memory_id
        if memory_type:
            payload["memory_type"] = memory_type
        if delete_all:
            payload["delete_all"] = True
        return self._delete("/memory/delete", payload)

    def summarize(
        self,
        user_id: str,
        bot_id: str = None,
        session_id: str = "default",
    ) -> dict:
        """
        Суммаризировать сессию — создать эпизод из сообщений.

        Args:
            user_id: ID пользователя
            bot_id: ID бота
            session_id: ID сессии для суммаризации

        Returns:
            {"status": "summarized", "episode_id": "...", "messages_count": N}
        """
        return self._post("/memory/summarize", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "session_id": session_id,
        })

    def profile(self, user_id: str) -> dict:
        """
        Профиль пользователя — агрегация всех знаний.

        Returns:
            {"user_id": "...", "facts": [...], "preferences": [...], "graph_summary": "..."}
        """
        return self._get(f"/memory/profile/{user_id}")

    def stats(self, user_id: str) -> dict:
        """Статистика по пользователю."""
        return self._get(f"/memory/stats/{user_id}")

    def health(self) -> dict:
        """Проверка здоровья API."""
        return self._get("/health")

    # === МЕТОДЫ v0.4.2 ===

    def usage(self) -> dict:
        """
        Текущее использование API — лимиты и расход (v0.4.2).

        Returns:
            {
                "tenant_id": "...",
                "plan": "free|starter|pro|business",
                "limit": 1000,
                "used": 42,
                "remaining": 958,
                "month": "2026-03",
                "reset_at": 1743465600
            }
        """
        return self._get("/account/usage")

    def export_data(self, user_id: str, format: str = "json") -> dict:
        """
        Экспорт данных пользователя (GDPR/FZ-152 compliance) (v0.4.2).

        Args:
            user_id: ID пользователя
            format: Формат экспорта (json, csv)

        Returns:
            {"user_id": "...", "records": [...], "total": N, "exported_at": "..."}
        """
        return self._get(f"/memory/export/{user_id}", params={"format": format})

    def import_data(self, user_id: str, records: List[dict], bot_id: str = None) -> dict:
        """
        Импорт данных пользователя (v0.4.2).

        Args:
            user_id: ID пользователя
            records: Список записей [{content, memory_type, metadata}, ...]
            bot_id: ID бота

        Returns:
            {"status": "imported", "count": N, "errors": [...]}
        """
        return self._post("/memory/import", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "records": records,
        })

    def regenerate_key(self) -> dict:
        """
        Перегенерация API ключа (v0.4.2).
        ВНИМАНИЕ: Старый ключ перестанет работать!

        Returns:
            {"api_key": "mc_live_...", "created_at": "..."}
        """
        result = self._post("/account/regenerate-key", {})
        # Обновляем ключ в текущей сессии
        if "api_key" in result:
            self._api_key = result["api_key"]
            self._session.headers["X-API-Key"] = result["api_key"]
        return result

    # === УДОБНЫЕ МЕТОДЫ ===

    def remember(self, user_id: str, fact: str, **kwargs) -> dict:
        """Короткий метод — запомнить факт."""
        return self.upsert(user_id=user_id, content=fact, memory_type="fact", **kwargs)

    def recall(self, user_id: str, query: str, **kwargs) -> list:
        """Короткий метод — вспомнить (только WARM результаты)."""
        ctx = self.context(user_id=user_id, query=query, **kwargs)
        return ctx.get("warm_episodes", [])

    def __repr__(self):
        masked_key = self._api_key[:12] + "..." if len(self._api_key) > 12 else "***"
        return f"MemoryClient(api_key='{masked_key}', bot_id='{self._bot_id}')"


# === ASYNC CLIENT (httpx) ===

class AsyncMemoryClient:
    """
    Асинхронный клиент Memory Core API (для aiogram, FastAPI, asyncio).

    Использование:
        from memory_core import AsyncMemoryClient

        memory = AsyncMemoryClient("mc_live_...")

        # В async функции:
        await memory.upsert(user_id="user_42", content="Люблю SPA")
        ctx = await memory.context(user_id="user_42", query="что предложить?")

        # Новое в v0.4.2:
        results = await memory.search(user_id="user_42", query="еда")
        usage = await memory.usage()
    """

    DEFAULT_URL = "https://api.memorycore.ru/api/v1"

    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        bot_id: str = "default",
        timeout: float = 15.0,
    ):
        try:
            import httpx
        except ImportError:
            raise ImportError(
                "Для AsyncMemoryClient нужен пакет httpx: pip install httpx"
            )

        self._api_key = api_key
        self._base_url = (base_url or self.DEFAULT_URL).rstrip("/")
        self._bot_id = bot_id
        self._timeout = timeout
        self._client = None

    async def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(
                headers={
                    "X-API-Key": self._api_key,
                    "Content-Type": "application/json",
                },
                timeout=self._timeout,
            )
        return self._client

    async def _post(self, path: str, data: dict) -> dict:
        client = await self._get_client()
        resp = await client.post(f"{self._base_url}{path}", json=data)
        resp.raise_for_status()
        return resp.json()

    async def _get(self, path: str, params: dict = None) -> dict:
        client = await self._get_client()
        resp = await client.get(f"{self._base_url}{path}", params=params)
        resp.raise_for_status()
        return resp.json()

    async def _delete(self, path: str, data: dict = None) -> dict:
        client = await self._get_client()
        resp = await client.request("DELETE", f"{self._base_url}{path}", json=data)
        resp.raise_for_status()
        return resp.json()

    # === ОСНОВНЫЕ МЕТОДЫ ===

    async def upsert(self, user_id: str, content: str, bot_id: str = None,
                      memory_type: str = "message", session_id: str = None,
                      metadata: dict = None, importance: float = 0.5) -> dict:
        """Сохранить запись в память (async)."""
        return await self._post("/memory/upsert", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "content": content,
            "memory_type": memory_type,
            "session_id": session_id,
            "metadata": metadata or {},
            "importance": importance,
        })

    async def context(self, user_id: str, query: str, bot_id: str = None,
                       max_items: int = 10, include_hot: bool = True,
                       include_warm: bool = True, include_cold: bool = False,
                       min_similarity: float = 0.40) -> dict:
        """Получить контекст (async)."""
        return await self._post("/memory/context", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "query": query,
            "max_items": max_items,
            "include_hot": include_hot,
            "include_warm": include_warm,
            "include_cold": include_cold,
            "min_similarity": min_similarity,
        })

    async def search(self, user_id: str, query: str, bot_id: str = None,
                      limit: int = 10, memory_type: str = None,
                      min_score: float = 0.3) -> dict:
        """Семантический поиск по памяти (async, v0.4.2)."""
        payload = {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "query": query,
            "limit": limit,
            "min_score": min_score,
        }
        if memory_type:
            payload["memory_type"] = memory_type
        return await self._post("/memory/search", payload)

    async def delete(self, user_id: str, memory_id: str = None,
                      bot_id: str = None, memory_type: str = None,
                      delete_all: bool = False) -> dict:
        """Удалить записи из памяти (async, v0.4.2)."""
        payload = {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
        }
        if memory_id:
            payload["memory_id"] = memory_id
        if memory_type:
            payload["memory_type"] = memory_type
        if delete_all:
            payload["delete_all"] = True
        return await self._delete("/memory/delete", payload)

    async def summarize(self, user_id: str, bot_id: str = None,
                         session_id: str = "default") -> dict:
        """Суммаризировать сессию (async)."""
        return await self._post("/memory/summarize", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "session_id": session_id,
        })

    async def profile(self, user_id: str) -> dict:
        """Профиль пользователя (async)."""
        return await self._get(f"/memory/profile/{user_id}")

    async def stats(self, user_id: str) -> dict:
        """Статистика (async)."""
        return await self._get(f"/memory/stats/{user_id}")

    async def health(self) -> dict:
        """Health check (async)."""
        return await self._get("/health")

    # === МЕТОДЫ v0.4.2 ===

    async def usage(self) -> dict:
        """Текущее использование API (async, v0.4.2)."""
        return await self._get("/account/usage")

    async def export_data(self, user_id: str, format: str = "json") -> dict:
        """Экспорт данных пользователя (async, v0.4.2)."""
        return await self._get(f"/memory/export/{user_id}", params={"format": format})

    async def import_data(self, user_id: str, records: list, bot_id: str = None) -> dict:
        """Импорт данных пользователя (async, v0.4.2)."""
        return await self._post("/memory/import", {
            "user_id": user_id,
            "bot_id": bot_id or self._bot_id,
            "records": records,
        })

    async def regenerate_key(self) -> dict:
        """Перегенерация API ключа (async, v0.4.2). Старый ключ перестанет работать!"""
        result = await self._post("/account/regenerate-key", {})
        if "api_key" in result:
            self._api_key = result["api_key"]
            # Обновляем заголовок в httpx клиенте
            if self._client:
                self._client.headers["X-API-Key"] = result["api_key"]
        return result

    # === УДОБНЫЕ МЕТОДЫ ===

    async def remember(self, user_id: str, fact: str, **kwargs) -> dict:
        """Запомнить факт (async)."""
        return await self.upsert(user_id=user_id, content=fact, memory_type="fact", **kwargs)

    async def recall(self, user_id: str, query: str, **kwargs) -> list:
        """Вспомнить (async)."""
        ctx = await self.context(user_id=user_id, query=query, **kwargs)
        return ctx.get("warm_episodes", [])

    async def close(self):
        """Закрыть HTTP клиент."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def __repr__(self):
        masked_key = self._api_key[:12] + "..." if len(self._api_key) > 12 else "***"
        return f"AsyncMemoryClient(api_key='{masked_key}', bot_id='{self._bot_id}')"
