# Frontend 開發指南

## 目錄結構

```
src/frontend/
├── src/
│   ├── types/game.ts        # HPMap  AttackPayload  ServerMessage  LeaderboardEntry  RoundSnapshot
│   ├── hooks/
│   │   ├── useWebSocket.ts  # 原生 WebSocket，連 /ws/battle/{matchId}/{playerId}?token=
│   │   └── useGameState.ts  # hp  currentTurn  isMyTurn  chatLog  gameOver  handleMessage
│   ├── components/
│   │   ├── HPBar.tsx        # progressbar，hp > 50% 綠，> 20% 橙，≤ 20% 紅
│   │   ├── ChatLog.tsx      # 滾動聊天紀錄
│   │   └── AttackInput.tsx  # 文字輸入 + 圖片上傳
│   ├── pages/
│   │   ├── HomePage.tsx     # 登入/註冊/建立對局
│   │   ├── BattlePage.tsx   # 對戰主頁（WebSocket）
│   │   ├── LeaderboardPage.tsx
│   │   └── ReplayPage.tsx   # 時間軸滑桿逐幀回放
│   ├── App.tsx              # BrowserRouter + Routes
│   ├── main.tsx
│   └── setupTests.ts        # jest-dom matchers + scrollIntoView mock
├── index.html
├── package.json
├── vite.config.ts           # proxy /api → :8000，/ws → ws://:8000
├── tsconfig.json            # IDE 用（含測試檔）
└── tsconfig.build.json      # build 用（排除測試檔，避免 TS 報錯）
```

## 常用指令

```bash
cd src/frontend
npm run dev      # 開發伺服器 http://localhost:5173（自動 proxy 到後端）
npm test         # vitest run（一次性執行所有測試）
npm run build    # tsc -p tsconfig.build.json && vite build → dist/
```

## 重要設定細節

**兩個 tsconfig 的原因**：`tsconfig.json` 的 `types: ["vitest/globals"]` 讓測試檔可用 `vi`、`expect` 等全域，但這會讓 `global`（Node.js 型別）進入非測試檔，導致 `tsc` 在 build 時報錯。因此 `tsconfig.build.json` 繼承主設定但排除所有 `*.test.*` 檔。

**`setupTests.ts` 的兩個 mock**：
1. `import "@testing-library/jest-dom"` — 讓 `toBeInTheDocument()`、`toHaveStyle()` 可用
2. `window.HTMLElement.prototype.scrollIntoView = function () {}` — jsdom 不支援此 API，ChatLog 的 `scrollIntoView` 呼叫會報錯

**`import.meta.env` 變數**：
- `VITE_API_URL`：REST API base（預設 `http://localhost:8000`）
- `VITE_WS_URL`：WebSocket base（預設 `ws://localhost:8000`）
- 本地開發用 `.env.development`；Production 用 `.env.production` 或 Cloudflare Pages env vars
