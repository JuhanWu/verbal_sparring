# 資料庫指南（SQLAlchemy + Alembic）

## Schema 概覽

| 表 | 說明 |
|---|---|
| `players` | 帳號、stats（wins / losses / total_damage）|
| `matches` | 對局記錄，`player2_id = NULL` 表示 AI NPC |
| `game_rounds` | 每回合記錄，`hp_snapshot JSONB` 存雙方 HP 快照 |
| `npc_memory` | NPC 對各玩家的記憶（`attack_patterns JSONB`、`weaknesses JSONB`）|

**`MatchStatus` enum**：`pending`、`ongoing`、`finished`（PostgreSQL native enum）

## SQLAlchemy 2.0 Mapped 風格

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from src.backend.core.database import Base

class Player(Base):
    __tablename__ = "players"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
```

## Alembic 工作流

```bash
cd src/backend

# 套用遷移到最新
alembic upgrade head

# 產生新的遷移（改 models 後）
alembic revision --autogenerate -m "描述"

# 回滾一步
alembic downgrade -1
```

**注意**：`alembic/env.py` 用同步 engine（`DATABASE_URL` 去掉 `+asyncpg`），不用 async engine。

**PostgreSQL enum 的 downgrade 必須手動清除**：

```python
# 遷移的 downgrade() 裡加：
op.execute("DROP TYPE IF EXISTS matchstatus")
```

否則再次 upgrade 會因 enum 已存在而失敗。

## FK 與 flush 順序

`NpcMemory.opponent_id` → `Player.id` 有 FK 約束。若在同一個 session 同時 `db.add(player)` 和 `db.add(memory)`，SQLAlchemy 的 Unit of Work 需要 `relationship()` 才能推斷正確的 flush 順序：

```python
# npc_memory.py
opponent: Mapped["Player"] = relationship("Player", foreign_keys=[opponent_id])
```

缺少此 relationship 會導致 `NpcMemory` 先於 `Player` INSERT → FK violation。

## 取得 DB Session（FastAPI）

```python
from src.backend.core.database import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/example")
async def handler(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Player))
    ...
```

測試中透過 `app.dependency_overrides[get_session]` 替換為測試 DB session（詳見 testing.md）。
