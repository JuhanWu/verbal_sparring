# AI 推論指南（LangGraph + Ollama）

## LangGraph Node 規則

**Node 函數必須回傳 partial dict，不能回傳整個 state：**

```python
# 正確
async def _node_call_ollama(state: RefereeState) -> dict:
    raw = await _call_ollama(msgs)
    return {"raw_response": raw}

# 錯誤（會 bypass reducer，checpointing/streaming 時有潛在問題）
async def _node_call_ollama(state: RefereeState) -> RefereeState:
    state["raw_response"] = await _call_ollama(msgs)
    return state
```

## RefereeGraph（`src/backend/services/referee/graph.py`）

**設計原則：只打一次 Ollama，其餘節點為純 Python。**

```
call_ollama → parse_response → validate_clamp
```

- `call_ollama`：async，httpx POST `{OLLAMA_URL}/api/chat`，回傳 `{"raw_response": str}`
- `parse_response`：純 Python，`_extract_json()` 解析，失敗回傳 `{"damage": 10, "comment": "裁判嘴瓢了", "display_text": original_text}`
- `validate_clamp`：純 Python，damage 夾在 10–30，comment 截斷 40 字

**公開介面**：
```python
result = await run_referee(text, image_b64)
# result: {"damage": int, "comment": str, "display_text": str}
```

## NPC Agent（`src/backend/services/npc/agent.py`）

**架構：單一 LangGraph node（call_ollama），ReAct 邏輯在 prompt 內完成。**

```
get_opponent_memory（純 Python + DB） → call_ollama → 回傳 attack_text
```

- 每回合開始：從 `npc_memory` 表讀取對此玩家的歷史記憶（attack_patterns、weaknesses）
- LLM prompt 包含記憶摘要 + 當前戰況（HP、回合數、最近 3 次對手攻擊）
- 局後非同步更新記憶：`update_npc_memory(db, opponent_id, new_pattern, damage_received)`

**公開介面**：
```python
attack_text = await run_npc_turn(
    db=db,
    match_id=match_id,
    opponent_id=player_uuid_str,
    my_hp=100,
    opponent_hp=80,
    round_number=3,
    recent_opponent_attacks=["攻擊1", "攻擊2"],
)
```

## Ollama 設定

- 模型：`gemma4:12b`（`settings.ollama_model`）
- 端點：`{settings.ollama_url}/api/chat`（預設 `http://localhost:11434`）
- 呼叫格式：`{"model": ..., "messages": [...], "stream": false, "options": {"temperature": 0.8}}`
- 回應取值：`resp.json()["message"]["content"].strip()`

## 啟動 Ollama（本地）

```bash
# Docker（推薦，含 GPU）
docker compose up -d ollama
docker compose exec ollama ollama pull gemma4:12b

# 或直接安裝 Ollama 後
ollama pull gemma4:12b
ollama serve
```
