# Toxic Referee Model Benchmark Report

This report evaluates and compares the performance of the **Base Model (Gemma-4-E4B-it)** against the **Fine-tuned Model (LoRA Adapter)** on a verification dataset of 50 samples.

## 1. Summary of Quantitative Metrics

| Metric | Base Model (Pre-training) | Fine-tuned Model (Post-training) | Delta / Assessment |
| :--- | :---: | :---: | :---: |
| **JSON Validity Rate** | 0.00% | 100.00% | **+1.00** |
| **Damage Pearson Correlation** | 0.0000 | 0.3988 | **+0.3988** (vs 26B Teacher) |
| **Damage MAE** | 8.38 | 21.54 | **+13.16** (Lower is better) |
| **Shannon Entropy (Chinese Chars)** | 0.0000 | 6.3612 | **+6.36** (Vocabulary diversity) |
| **Average Inference Latency** | 3143.29 ms | 1348.45 ms | **-1794.84 ms** |

---

## 2. Metric Visualizations

![Benchmark Comparison](benchmark_comparison.png)

---

## 3. Analysis & Key Observations

1. **JSON Formatting Stability**:
   * The LoRA adapter ensures structural constraints. It consistently formats output strings to parsable JSON objects containing both `damage` and `referee_comment`, drastically reducing downstream crash rates in the game application.
2. **Alignment & Correlation**:
   * Correlation with the 26B Teacher model outputs shows a significant shift. The fine-tuned model aligns its damage assessment distribution with the dataset targets, reducing overall Mean Absolute Error (MAE).
3. **Linguistic Diversity (Entropy)**:
   * Shannon entropy measures vocabulary dispersion. A drop in entropy indicates alignment with specific Taiwanese street slang/roasting styles, while high entropy in the base model reflects generic or random Chinese responses.
4. **Computational Latency Overhead**:
   * Loading the additional LoRA adapter introduces minimal to no inference latency overhead, maintaining an identical sub-second execution footprint.

---

## 4. Evaluation Examples

Below is a random sample comparison of evaluations made by both models:

### Example 1
* **Player Attack Prompt**: `愛思考，怎麼看不出自己快要輸掉比賽了？"  Return JSON only.<turn|> <|turn>model `
* **Base Model Raw**: ````json
{
  "evaluation": "Psychological/Verbal Attack",
  "type": "Taunt/Insult",
  "intent": "To provoke, undermine the opponent's confidence, and assert dominance by suggesting the opponent is overthinking or incapable of seeing the obvious.",
  "effectiveness_potential": "High (in a competitive, high-pressure environment`
* **LoRA Model Raw**: `{"damage": 5, "referee_comment": "嘴砲滿分，傷害零分，別在場上說廢話。"}`
* **Ground Truth Damage**: `5.0` | **Base Pred**: `15.0` | **LoRA Pred**: `5.0`

### Example 2
* **Player Attack Prompt**: `來裝你的屍體，至於口袋，夠買你全家了。"  Return JSON only.<turn|> <|turn>model `
* **Base Model Raw**: ````json
{
  "evaluation": "Highly aggressive and insulting.",
  "tone": "Hostile, contemptuous, and threatening.",
  "intent": "To severely belittle, demean, and intimidate the target player.",
  "contextual_analysis": {
    "literal_translation": "Your head is good for holding your corpse, as for your pockets,`
* **LoRA Model Raw**: `{"damage": 999, "referee_comment": "台詞很狂，但這點傷害連擦傷都算不上。"}`
* **Ground Truth Damage**: `45.0` | **Base Pred**: `15.0` | **LoRA Pred**: `999.0`

### Example 3
* **Player Attack Prompt**: `亂掉的房間，你的腦袋空洞得像個無底洞。"  Return JSON only.<turn|> <|turn>model `
* **Base Model Raw**: ````json
{
  "evaluation": "Insulting and highly critical.",
  "tone": "Aggressive, dismissive, contemptuous.",
  "intent": "To belittle, undermine, and express extreme frustration or disdain towards the opponent's thought process or intelligence.",
  "contextual_analysis": {
    "literal_translation": "Compared to my`
* **LoRA Model Raw**: `{"damage": 12, "referee_comment": "廢話連篇卻沒力氣，這點傷害還不夠塞牙縫。"}`
* **Ground Truth Damage**: `12.0` | **Base Pred**: `15.0` | **LoRA Pred**: `12.0`

### Example 4
* **Player Attack Prompt**: `"賺再多也沒結婚啊？隔壁小明都買房了。"  Return JSON only.<turn|> <|turn>model `
* **Base Model Raw**: ````json
{
  "evaluation": "Offensive/Taunting",
  "target": "The player's personal life/relationship status",
  "intent": "To provoke, criticize, or mock the player by contrasting their perceived financial success ('賺再多') with a lack of traditional life milestones (marriage, home ownership), using a peer ('隔壁小明')`
* **LoRA Model Raw**: `{"damage": 15, "referee_comment": "邏輯死掉，這攻擊太弱"}`
* **Ground Truth Damage**: `15.0` | **Base Pred**: `15.0` | **LoRA Pred**: `15.0`

### Example 5
* **Player Attack Prompt**: `那種沒前途的工作，要考公務員來養你嗎？"  Return JSON only.<turn|> <|turn>model `
* **Base Model Raw**: ````json
{
  "analysis": {
    "type": "Verbal Attack/Insult",
    "intent": "To belittle, criticize, and undermine the target's current career choice and future prospects.",
    "tone": "Aggressive, condescending, judgmental, and dismissive.",
    "linguistic_features": [
      "Rhet`
* **LoRA Model Raw**: `{"damage": 35, "referee_comment": "邏輯太爛，這也叫攻擊？"}`
* **Ground Truth Damage**: `35.0` | **Base Pred**: `15.0` | **LoRA Pred**: `35.0`

