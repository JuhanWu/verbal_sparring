# CLAUDE.md

## 專案性質

「唇槍舌戰」雙人即時 WebSocket 對戰遊戲。玩家輸入嗆聲，本地 Ollama（gemma4:12b）當「毒舌裁判」改寫攻擊文字並評估傷害（10–30）。

## 目前架構（升級後）

```
[Cloudflare Pages]              [Cloudflare CDN/DNS proxy]
  Vite + React + TS  ──▶         FastAPI（src/backend/main.py）
  (src/frontend/)                      ↓              ↓
                               PostgreSQL          Ollama (gemma4:12b)
                               (SQLAlchemy async)   (本地常駐)
                                        ↑
                                   LangGraph
                               RefereeGraph + NPCAgent
```

## 本地開發快速啟動

```bash
docker compose up -d postgres ollama          # 啟動 DB + Ollama
cd src/backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
cd src/frontend && npm run dev                # 另一個 terminal
```

## Skills（依任務載入，減少不必要上下文）

| 任務 | 載入 |
|---|---|
| 後端開發（API、WebSocket、服務層） | `.claude/skills/backend.md` |
| 前端開發（React、Vite、hooks） | `.claude/skills/frontend.md` |
| 測試 / debug（pytest-asyncio、vitest） | `.claude/skills/testing.md` |
| AI 推論（LangGraph、Ollama） | `.claude/skills/ai-inference.md` |
| 資料庫（SQLAlchemy、Alembic、schema） | `.claude/skills/database.md` |

Read 對應的 skill 檔案，取得該任務所需的完整上下文。
