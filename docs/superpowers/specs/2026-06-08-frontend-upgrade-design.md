# 唇槍舌戰 — 前端全面升級設計規格

**日期：** 2026-06-08
**狀態：** 已核准，待實作

---

## 1. 設計方向

### 視覺風格：C×E — 水墨武俠 × Brutalism

兩個風格融合的核心邏輯：

- **Brutalism（E）提供骨架**：Impact 大字體、黑底白字、直接衝擊的版面結構、無多餘裝飾
- **水墨江湖（C）提供靈魂**：深棕黑底色、朱紅印章裝飾、Georgia 斜體文言攻擊文字、漢字排名、裁判印章橫幅

整體氣質：文人持刀，一字見血。

---

## 2. 設計系統

### 2.1 色彩

| 角色 | 名稱 | Hex |
|---|---|---|
| 主背景 | Ink Black | `#0a0905` |
| 次要背景 | Deep Parchment | `#3a3020` |
| 邊框 / 分隔線 | Bamboo Shadow | `#2a2018` |
| 主強調色 | Vermillion 朱 | `#cc3300` |
| 強調高光 | Fire Seal 印 | `#ff4400` |
| 主文字 | Pure White | `#ffffff` |
| 次要文字 | Parchment 宣 | `#d4c5aa` |
| 輔助文字 | Aged Ink | `#886655` |
| 禁用 / 暗部 | Dark Bark | `#443322` |
| 特效 / 警示 | Ember 燼 | `#ff8800` |

HP 條三段色：
- 高血量（>50%）：`#336600` → `#66cc00`（綠）
- 中血量（20–50%）：`#885500` → `#ffaa00`（橙）
- 瀕死（<20%）：`#660000` → `#ff2200`（紅，加發光）

### 2.2 字型

| 用途 | 字型 | 大小 | 樣式 |
|---|---|---|---|
| 主標題 / 遊戲名稱 | Impact, Arial Black | 42–48px | 全大寫，letter-spacing 5px |
| 章節標題 / HP 數字 | Impact | 24–38px | 全大寫 |
| 攻擊文字 / 裁判評語 | Georgia | 11–13px | italic |
| 系統訊息 / 數據 | monospace | 9–10px | letter-spacing 2–3px |
| 傷害浮現數字 | Impact | 48–56px | 朱紅 + 發光陰影，動畫浮現 |

### 2.3 核心元件

**HPBar**
- 三段漸層色（依血量自動切換）
- 高度 7–10px，無圓角（brutalist 感）
- 受傷時：條寬 transition 0.4s，同步觸發傷害數字動畫

**裁判印章橫幅（RefereeStamp）**
- 兩端「判」「決」方框印章
- 中央評語文字 monospace，letter-spacing 3px
- 邊框用淡朱紅（`#cc330044`），不搶眼

**MessageBubble（聊天記錄條目）**
- 攻擊者名稱：Impact 13px 朱紅（NPC）或白（玩家）
- 攻擊文字：Georgia italic 11px `#d4c5aa`（Parchment 宣）
- 傷害標籤：右側小膠囊，`border: 1px solid #3a1800`

**按鈕三種**
- Primary outline：`border: 2px solid #cc3300`，`color: #cc3300`，發光陰影
- Primary solid：`background: #cc3300`，`color: #fff`
- Secondary：`border: 1px solid #2a2018`，`color: #443322`

**輸入框**
- 預設：`border: 1px solid #2a2018`
- 聚焦：底部 `border-bottom: 2px solid #cc3300` + 微發光
- Placeholder：Georgia italic，`#443322`

---

## 3. 動態特效規格（Framer Motion）

### 3.1 傷害數字浮現
- 觸發時機：每次 `attack` / `npc_attack` 訊息收到
- 動畫：`y: 0 → -60px`，`opacity: 1 → 0`，`scale: 1.2 → 0.8`
- 持續：800ms，`easeOut`
- 字型：Impact 56px，`#ff4400`，`text-shadow: 0 0 20px rgba(255,80,0,0.6)`

### 3.2 畫面震動（Screen Shake）
- 觸發時機：傷害 ≥ 20
- 動畫：`x: [0, -6, 6, -4, 4, 0]`，持續 400ms
- 作用範圍：戰鬥頁整個容器

### 3.3 HP 條受傷閃爍
- 觸發時機：HP 值下降時
- 動畫：`background` 短暫閃白（`#fff` 50ms）再回正常色
- 同步縮減 `width`（`transition: width 0.4s ease`）

### 3.4 裁判橫幅入場
- RefereeStamp 是聊天記錄的永久條目（不是浮動覆蓋層），緊接在對應攻擊訊息之後
- 每次新 RefereeStamp 入場：`y: -20px → 0`，`opacity: 0 → 1`，300ms
- 渲染為 ChatLog 內的獨立行，隨聊天記錄一起捲動

### 3.5 訊息淡入
- 每條新 ChatLog 條目：`opacity: 0 → 1`，`y: 10 → 0`，200ms

### 3.6 入場動畫（頁面載入）
- 戰鬥頁：HP 區從上滑入（`y: -30 → 0`），輸入區從下滑入（`y: 30 → 0`），各 400ms，錯開 100ms
- 首頁：Logo 從中央 `scale: 0.8 → 1` + `opacity: 0 → 1`，500ms

### 3.7 墨水濺射（Ink Splash）
- 觸發時機：攻擊命中時（每次 `attack` / `npc_attack`）
- 實作：Framer Motion `radial burst`，8 個小粒子從命中點向外擴散，顏色 `#cc3300`，持續 600ms

---

## 4. 頁面規格

### 4.1 首頁 `/`

**未登入狀態**
- 中央 Logo（唇槍 白 / 舌戰 朱紅）
- 登入 / 註冊 Tab 切換
- 用戶名 + 密碼輸入框（monospace 風格）
- 錯誤訊息：左側朱紅邊框小橫條
- CTA：「進入戰場」Primary outline 按鈕

**已登入狀態**
- 頂部 Navbar：遊戲名稱 + 排行榜連結 + 我的戰績連結 + 登出按鈕
- 歡迎區：用戶名大字 + 迷你三格戰績（勝 / 敗 / 累積傷害）
- 對戰設定卡：AI NPC / 人類對手切換 Tab + 輸入對手用戶名 + 「開戰！」按鈕

**API 呼叫：**
- `POST /api/auth/login` — 登入
- `POST /api/auth/register` — 註冊
- `POST /api/matches` — 建立對局，成功後 `navigate('/battle/:matchId')`

---

### 4.2 戰鬥頁 `/battle/:matchId`

**版面（上到下）**
1. **Navbar**：遊戲名 + 回合數 + 返回按鈕
2. **HP 區**：左（我方）/ 中（對 字 + 紅點）/ 右（對手），各含名稱、大數字、HP 條
3. **聊天記錄**：`flex: 1 overflow-y: auto`，條目含攻擊者名稱、文言攻擊文字、傷害標籤；裁判評語用 RefereeStamp 橫幅
4. **回合指示器橫條**：`#3a3020` 背景，「⚔ 輪到你出招！⚔」or「等待對手...」
5. **輸入區**：筆▶前綴 + 輸入框 + 📷按鈕 + 出手按鈕

**WebSocket 訊息處理：**

| type | 動作 |
|---|---|
| `system` | 更新 HP、currentTurn；系統訊息加入 ChatLog（半透明） |
| `attack` | 更新 HP、currentTurn；新增 MessageBubble；觸發傷害數字 + 震動（若 ≥20） |
| `npc_attack` | 同上，攻擊者標記為 NPC |
| `game_over` | 顯示勝負 Modal（大字 + 「查看回放」+「再戰一局」按鈕） |
| `turn_error` | 輸入框短暫紅色邊框閃爍 |

**遊戲結束 Modal：**
- 黑底半透明遮罩
- 「你贏了！」（白）or「你輸了...」（`#886655`）
- 按鈕：
  - 「查看回放 ▶」（Primary outline）→ `navigate('/replay/:matchId')`
  - 「再戰一局」（Primary solid）→ `navigate('/')` 返回首頁重新建立對局
  - 「回首頁」（Secondary）→ `navigate('/')`

---

### 4.3 武林排行 `/leaderboard`

- 標題：「武林 排行」Impact 雙色
- 底部朱紅 3px 邊框分隔
- 表頭：位 / 俠士 / 傷害 / 勝 / 敗（monospace 小字）
- 第 1 名：`border-left: 3px solid #cc3300`，`background: #1a0d00`，名稱 Impact 白
- 第 2 名：`border-left: 3px solid #662200`，`background: #0f0a05`
- 第 3 名：`border-left: 3px solid #331100`
- 4 名以下：無特殊背景
- 漢字排名（一二三四...），4 名後改阿拉伯數字
- 底部裝飾文字：「⸺ 以筆傷人，武林稱霸 ⸺」

---

### 4.4 個人頁 `/profile`

- 頭像圓框：`border: 2px solid #cc3300`，中央為用戶名首字 Impact 大字
- 用戶名：Impact + 「武林高手」等稱號副標（依勝場數決定）
- 三格戰績：勝場（白）/ 敗場（`#664433`）/ 累積傷害（朱紅）
- 最近五場對戰列表：
  - 勝：`border-left: 2px solid #cc3300`
  - 敗：`border-left: 2px solid #443322`
  - 每行含：勝/敗標籤 + 對手名 + 累積傷害 + 「回放 ▶」連結（若有 matchId）

**資料來源：**
- 戰績（勝/敗/累積傷害）：`GET /api/leaderboard`，篩出 `username === currentUser`
- 最近五場對戰：localStorage `matchHistory` 陣列，格式 `[{ matchId, opponent, result, damage, roundCount }]`；每次 `game_over` 訊息收到時寫入；ProfilePage 讀取後顯示，各行附「回放 ▶」連結

---

### 4.5 對戰紀錄頁 `/history`

- 標題：「對戰紀錄」
- 篩選 Tab：全部 / 勝場 / 敗場（切換高亮）
- 每行對戰卡片（`border: 1px solid #2a2018`）：
  - 對手名 Impact + 勝/敗標籤（右）
  - 回合數 + 累積傷害 + 「看回放 ▶」連結
  - 勝場：`background: #3a3020`；敗場：無特殊背景
- 無限滾動 or 分頁（初版分頁，每頁 20 筆）

**資料來源：** 目前後端無 `/api/history` 端點。初版以 `GET /api/leaderboard` + localStorage 暫存對局 ID 實作；記錄 matchId 列表，每行提供「看回放」連結至 `/replay/:matchId`

---

### 4.6 對戰回放頁 `/replay/:matchId`

- 標題：「回放 · ROUND X/N」
- HP 快照（當前回合後的狀態）：雙方各一條 HP 條
- 回合卡片：
  - 攻擊者名稱（朱紅）
  - 攻擊原文 + 改寫後文字（`display_text`，Georgia italic）
  - 傷害數值 + 裁判短評
- 導覽：上一回合 ◀ + 進度條滑桿 + 下一回合 ▶
- 進度條：`background: #cc3300`，拖動時即時更新 HP 快照 + 回合卡片

**API：** `GET /api/replay/:matchId` → `{ rounds: RoundSnapshot[] }`

---

## 5. 新增頁面路由表

```
/                   → HomePage（已有，重設計）
/battle/:matchId    → BattlePage（已有，重設計）
/leaderboard        → LeaderboardPage（已有，重設計）
/replay/:matchId    → ReplayPage（已有，重設計）
/profile            → ProfilePage（新增）
/history            → HistoryPage（新增）
```

---

## 6. Tech Stack 變更

| 項目 | 現況 | 升級後 |
|---|---|---|
| CSS | 純 inline styles | Tailwind CSS v3 |
| 動畫 | 無 | Framer Motion v11 |
| 路由 | react-router-dom v6 | 不變 |
| 字型 | 系統字型 | Impact（系統內建）+ Georgia（系統內建）+ monospace（系統內建）|
| 狀態管理 | useState + localStorage | 不變（不引入 Redux/Zustand，現有規模不需要）|

### 新增依賴

```bash
npm install framer-motion
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Tailwind 設定重點

```js
// tailwind.config.js
theme: {
  extend: {
    colors: {
      'ink': '#0a0905',
      'parchment': '#3a3020',
      'bamboo': '#2a2018',
      'vermillion': '#cc3300',
      'fire': '#ff4400',
      'aged': '#886655',
      'bark': '#443322',
      'ember': '#ff8800',
    },
    fontFamily: {
      'display': ['Impact', 'Arial Black', 'sans-serif'],
      'body': ['Georgia', 'serif'],
      'mono': ['Courier New', 'monospace'],
    }
  }
}
```

---

## 7. 元件樹

```
App
├── Layout（Navbar + 子頁面）
│   ├── Navbar
│   └── Outlet
├── HomePage
│   ├── AuthForm（LoginForm / RegisterForm）
│   └── MatchSetup（NPC / 人類切換 + 開戰按鈕）
├── BattlePage
│   ├── HPSection（HPBar × 2）
│   ├── ChatLog
│   │   ├── MessageBubble
│   │   ├── SystemMessage
│   │   └── RefereeStamp
│   ├── TurnIndicator
│   ├── AttackInput
│   ├── DamageNumber（動畫浮現，portal 渲染）
│   └── GameOverModal
├── LeaderboardPage
│   └── LeaderboardTable
├── ProfilePage
│   ├── AvatarBadge
│   ├── StatsGrid
│   └── RecentMatchList
├── HistoryPage
│   ├── FilterTabs
│   └── MatchCard × N
└── ReplayPage
    ├── HPSnapshot
    ├── RoundCard
    └── ReplayScrubber
```

---

## 8. 功能對齊後端清單

| 後端功能 | 前端現況 | 升級後 |
|---|---|---|
| POST /api/auth/register | ✅ 有 | 重設計 |
| POST /api/auth/login | ✅ 有 | 重設計 |
| 登出（清除 token） | ❌ 無 | ✅ Navbar 登出按鈕 |
| POST /api/matches（NPC） | ✅ 有 | 重設計 |
| POST /api/matches（人類） | ⚠️ 有但 UX 差 | ✅ 改善選對手流程 |
| WS attack / npc_attack | ✅ 有 | ✅ 加動畫特效 |
| WS game_over | ✅ 有 | ✅ 加 Modal + 回放連結 |
| WS turn_error | ✅ 有 | ✅ 加輸入框閃爍回饋 |
| GET /api/leaderboard | ✅ 有 | 重設計 |
| GET /api/replay/:matchId | ✅ 有 | 重設計（加進度條 + HP 快照） |
| 個人戰績顯示 | ❌ 無 | ✅ ProfilePage（新增） |
| 對戰紀錄列表 | ❌ 無 | ✅ HistoryPage（新增，暫用 localStorage） |

---

## 9. 不在本次範圍內

- 後端新增 API 端點（`/api/profile`、`/api/history`）
- 手機版響應式設計（桌機優先，行動版為後續迭代）
- 多語系（目前維持中文介面）
- 音效系統
