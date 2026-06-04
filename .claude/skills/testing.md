# 測試指南

## 執行測試

```bash
# 後端（從 src/backend/）
cd src/backend && python3 -m pytest -v
cd src/backend && python3 -m pytest tests/test_auth.py -v   # 單一模組

# 前端（從 src/frontend/）
cd src/frontend && npm test
```

## 後端：pytest-asyncio 0.24 規則

**`pytest.ini` 設定**（已設，不要動）：
```ini
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session
```

**每個含 async 測試的檔案頂端都必須有**：
```python
import pytest
pytestmark = pytest.mark.asyncio(loop_scope="session")
```
忘記加會導致「Future attached to a different loop」。

## 後端：DB Fixture 模式

`tests/conftest.py` 提供三個 fixture：

| Fixture | Scope | 用途 |
|---|---|---|
| `test_engine` | session | 建立 schema（create_all），一次 |
| `db` | function | **每個 test 各一個** NullPool engine + session，測試後 truncate 所有表 |
| `client` | function | AsyncClient（httpx）+ 注入 `db` 到 `get_session` |

**為什麼用 NullPool**：asyncpg 連線綁定特定 event loop。pytest-asyncio 0.24 的 session scope 讓所有 async test 共用同一個 loop，但 function-scoped fixture 若用 pool 會跨 loop 複用連線導致錯誤。NullPool 每次建新連線，避免此問題。

**不要用 SAVEPOINT 回滾模式**：asyncpg 的 SAVEPOINT 在 pytest-asyncio 0.24 多 loop 環境不可靠，已改為 truncate 隔離。

## 後端：WebSocket 測試模式

WebSocket 測試用 `starlette.testclient.TestClient`（同步）。要讓 TestClient 打測試 DB，需在測試前設：

```python
app.dependency_overrides[get_session] = _ws_test_session
```

其中 `_ws_test_session` 是一個 async generator，每次呼叫都建立新 NullPool engine（TestClient 有自己的 internal event loop，不能共用外部 pool）：

```python
async def _ws_test_session():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy.pool import NullPool
    eng = create_async_engine(RESOLVED_URL, poolclass=NullPool)
    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as session:
        yield session
    await eng.dispose()
```

sync test function 可以用 session-scoped async fixture 確保 schema 存在（`test_engine` 作為依賴），但 sync function 本身不需要 `pytestmark`。

## 前端：vitest 設定

```typescript
// vite.config.ts
test: {
  environment: "jsdom",
  globals: true,       // 讓 vi、expect、test 不需 import
  setupFiles: ["./src/setupTests.ts"],
}
```

`@testing-library/react` 16.x 已內建 jest-dom，但需要在 `setupTests.ts` 顯式 import 才能在 vitest 環境生效。
