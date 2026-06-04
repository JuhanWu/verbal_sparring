# Backend 開發指南

## 目錄結構

```
src/backend/
├── api/
│   ├── routes/          # auth.py  matches.py  leaderboard.py  replay.py
│   └── ws/              # battle_ws.py（WebSocket 端點）
├── core/
│   ├── config.py        # Settings（pydantic-settings，讀 .env）
│   └── database.py      # engine、SessionFactory、get_session、Base
├── models/              # Player  Match(MatchStatus)  GameRound  NpcMemory
├── schemas/             # Pydantic request/response（auth  match  leaderboard  replay）
├── services/
│   ├── auth.py          # hash_password  verify_password  create_access_token  decode_token  get_current_player
│   ├── game/room.py     # GameRoom dataclass + rooms dict（進程內多房間）
│   ├── referee/graph.py # run_referee(text, image_b64) -> dict
│   └── npc/agent.py     # run_npc_turn(...)  update_npc_memory(...)
├── alembic/             # 遷移腳本
├── tests/               # 見 testing.md
├── main.py              # FastAPI app + routers
├── pytest.ini
└── requirements.txt
```

## 啟動後端

```bash
cd src/backend
cp ../../.env.example .env   # 第一次：填入 DATABASE_URL、SECRET_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`--reload` 在開發時有用，但每次存檔都會重啟 app（不影響 PostgreSQL 連線）。

## 環境變數（`src/backend/.env`）

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/verbal_sparring
TEST_DATABASE_URL=postgresql+asyncpg://vsuser:vspass@localhost:5433/verbal_sparring_test
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:12b
SECRET_KEY=<隨機字串>
```

## 關鍵架構決策

- **async SQLAlchemy 2.0**：全部用 `AsyncSession`，`await db.execute(select(...))`
- **JWT**：`decode_token()` 永遠回傳 dict，不回傳 None。失敗時回 `{"_error": "expired"}` 或 `{"_error": "invalid"}`。WebSocket 端點用 `payload.get("_error")` 檢查，**不用** `not payload`
- **WebSocket auth**：token 放在 query param `?token=`，不用 Authorization header
- **NPC 對戰**：`match.player2_id = NULL` 表示 AI NPC。NPC 不透過 WebSocket 連線，`room.hp["NPC"] = 100` 需手動初始化
- **多房間**：`rooms: dict[str, GameRoom]` 在 `services/game/room.py` 以進程內 dict 管理，match_id 為 key
