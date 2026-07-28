---
name: seedance-prompt
description: Seedance 2.0（即梦）专业视频提示词规范：@引用役割语法、时间码多镜头切镜专章、运镜/景别/光影中英对照词汇、镜间衔接两端写法、短剧向模板库。摄影指导写视频生成提示词时必读；用户要优化提示词、切镜、运镜表达时使用。
---

# Seedance 2.0 专业提示词规范（插件内置）

## 运行时适配（跨 Agent 兼容）

- 本技能是**纯知识规范**（无流程、无 subagent 调度、无门禁）：任何运行时直接把本文当写作标准使用即可
- **无 Skill 工具的运行时**（OpenClaw 等）：直接读取本文件（插件 `skills/seedance-prompt/SKILL.md`）
- 本机若另装有社区版 `seedance-prompt-en` 技能，可作补充参考；两者冲突时以本文 + `dreamina <子命令> -h` 实测为准

## 定位

你写的每条提示词都是**导演视角的一段"拍摄+剪辑"指令**，不是场景描述作文。Seedance 2.0 有专业级的切镜与运镜执行力——
但它只执行你**明确写出**的镜头语言：不写切镜动词就一个机位拍到底，不写禁切句它也可能随机切。
**每条提示词都必须在"切镜"上做明确表态：要么时间码明切，要么禁切句明禁。**

提示词语言：正文推荐**英文**（与 STYLE LOCK 一致、镜头术语响应最稳），时间码前缀用 `0-3s:` 体例；
即梦对中文同样友好，但全剧统一一种语言，防风格漂移。

---

## 一、@ 引用役割语法

每个上传素材必须用 `@image1 / @video1 / @audio1`（或中文 `@图片1`）引用**并声明用途**——无归属的素材=浪费文件数配额（图≤9、视频≤3、音频≤3、总数≤12）：

| 用途 | 写法（英文示例） |
|---|---|
| 人物身份 | `the woman from @image1` |
| 场景/背景 | `in the living room from @image2` |
| 首帧 / 尾帧 | `@image1 as the first frame / @image2 as the last frame` |
| 服装/道具/产品 | `wearing the outfit from @image3` |
| 运镜复刻 | `replicate the camera movement from @video1` |
| 动作编排 | `mimic the choreography from @video1` |
| 特效/转场复刻 | `replicate the VFX and transitions from @video1` |
| 节奏/卡点 | `match the pacing and beat of @audio1` |
| 音色 | `voice timbre referenced from @audio1` |

**引用方式决策表**（哪种信息用哪种载体，别拿视频参考干文字能干的事）：

| 要素 | 最优载体 | 理由 |
|---|---|---|
| 人物身份、构图/首尾画面 | **图** | 视觉信息密度最高，文字描述不可靠 |
| 场景基底 | 图 + 文字改细节（天气/时段） | 图定底，文字微调 |
| **运镜、切镜、节奏、叙事逻辑** | **文字** | 镜头语言是标准化术语，文字最直接、零额外成本 |
| 简单动作 | 文字 | 可描述的动作写出来即可 |
| 复杂/独有动作、特效 | 参考视频 | 只有难以言传的才值得花一个视频位（且加价） |
| 音色、旋律 | 音频 | 生物特征/旋律不可文字化 |

---

## 二、提示词结构公式

```
[STYLE LOCK（逐字前置，勿改）]
+ [主体与场景：@引用 + 一句定位]
+ [时间码节拍序列：每拍 = 切镜动词 + 景别/机位 + 运镜 + 动作/表演 + （对白）]
+ [音频设计：环境音/音效/对白情绪]
+ [收束：氛围与质感修饰词]
```

短镜（4-6s 单节拍）可省时间码，但**景别+运镜+动作**三件套一个都不能少。

---

## 三、时间码切镜语法（核心专章——多镜头就是这么写出来的）

### 3.1 骨架

```
0-4s: Wide establishing shot, slow push-in — Lin Wan stands alone by the floor-to-ceiling window...
4-8s: Cut to medium close-up — she looks down at the divorce papers, knuckles tightening...
8-12s: Cut to a low-angle medium shot — the CEO steps out of the shadowed corridor behind her...
```

**每个节拍的第一个短语必须是"切镜信号"**：`Cut to <新景别/机位>`、`Whip cut to...`、`Reverse shot —`、
`Insert close-up of...`、`Cut back to...`。只换内容不换镜头语言 = 模型大概率同机位拍到底（产出"一个镜头一个画面"）。

### 3.2 切镜动词表（中英对照）

| 中文 | 英文（提示词用） | 用途 |
|---|---|---|
| 切至特写/近景 | cut to close-up / cut to medium close-up | 常规景别推进 |
| 快切 | quick cut / whip cut to... | 动作戏、紧张节奏 |
| 反打 | reverse shot / cut to the reverse angle | 对话正反打 |
| 切回 | cut back to... | 回到主机位 |
| 插入镜 | insert shot of <物件> | 关键道具特写 |
| 反应镜 | cut to <人物>'s reaction | 情绪句后接听者反应 |
| 切换低角度仰拍 | cut to a low-angle shot | 力量感/压迫感 |
| 俯拍切入 | cut to an overhead / bird's-eye view | 全局态势 |
| 切空镜 | cutaway to <环境细节> | 呼吸、过渡 |
| 匹配剪辑 | match cut to... | 形状/动作呼应转场 |

### 3.3 节拍规则

- **每拍一件事**：一个动作 / 一句台词 / 一个情绪转折；别在一拍里塞连续复杂动作
- **拍数与时长匹配**：4-6s→1 拍；6-9s→2 拍；9-12s→2-3 拍；12-15s→3-4 拍。**≥8s 必须 ≥2 拍**（分镜标【一镜到底】除外）
- 节拍间可以换景别、换机位、换角度，但**不换场景**——换场景是分镜层面另开一行镜号的事
- 对白写法：`she says: "..."`（带情绪副词，如 coldly / voice trembling）；**内心独白/旁白绝不入提示词**（后期配音）

### 3.4 对话戏正反打模板（切镜最常用场景）

```
0-4s: Medium shot over B's shoulder — A speaks, eye-line to frame right: "..."
4-7s: Reverse shot, medium close-up of B listening, eye-line to frame left; B replies: "..."
7-10s: Cut back to A, closer now (medium close-up) — the line lands, her expression hardens.
```

要点：**轴线一致**（A 永远看画右、B 永远看画左）；反打逐拍收紧景别做情绪递进；
第三拍可换成 `Insert shot`（关键物件）或 `cut to B's reaction`（无声反应），比干聊更有戏。

### 3.5 一镜到底（不切就要明禁）

分镜标【一镜到底】时，末尾必须显式：
`One continuous take, no cuts, no editing throughout.`（中文即"全程不要切镜头，一镜到底"）
一镜到底允许**场景内空间转移**（跟拍穿过走廊上屋顶），运镜写成连续链：`the camera follows... then tilts up... finally cranes over...`

### 3.6 镜间衔接的两端写法（片段之间的切镜思路）

分镜"衔接"列决定相邻两条提示词的**结尾句和开头句**（详细翻译表见 cinematographer 规范）：

- `硬切·动接动`：上一镜结尾 `ends mid-stride, hand reaching the door handle` → 本镜开头 `opens mid-action: she pushes the door open, continuing the motion`
- `视线引导`：上一镜结尾 `her gaze shifts off-screen right` → 本镜开场给被看之物（方向一致）
- `无缝衔接`：不靠文字，走 `first_from_prev` 尾帧抽帧
- 所有衔接：相邻两镜的**光线、色调、时段**描述必须一致，否则拼起来跳戏

---

## 四、运镜词汇表（中英对照，按 AI 稳定性排序）

### 稳定优先（默认池）

| 中文 | 英文 |
|---|---|
| 固定镜头 | static shot / locked-off camera |
| 缓推 | slow push-in / slow dolly in |
| 缓拉 | slow pull-back / dolly out |
| 左/右平移 | truck left / right |
| 左/右摇 | pan left / right |
| 上/下摇 | tilt up / down |
| 跟拍 | tracking shot / the camera follows |
| 手持感 | handheld camera, subtle shake |

### 进阶（情绪重镜使用，写清楚就稳）

| 中文 | 英文 |
|---|---|
| 环绕 | orbit shot / arc around the subject |
| 升降 | crane up / crane down |
| 低角度仰拍 | low-angle shot |
| 鸟瞰 | bird's-eye view / overhead shot |
| 希区柯克变焦 | dolly zoom (vertigo effect) |
| 荷兰角 | dutch angle |
| 第一人称 | first-person POV |
| 甩镜 | whip pan |
| 慢动作 | slow motion |
| 升格定格 | freeze frame at the end |

原则：**一拍一种运镜**；甩镜/快速环绕等高风险运镜只在有参考视频复刻（`@video`）或动作戏快切节拍里用。

---

## 五、景别与构图（与分镜"景别"列硬对齐）

| 分镜景别 | 提示词 |
|---|---|
| 远景/定场 | wide establishing shot, full environment |
| 全景 | full shot, full body in environment |
| 中景 | medium shot, waist-up, environment visible |
| 中近景 | medium close-up, chest-up |
| 近景 | close shot |
| 特写 | close-up（仅分镜明确标注时） |
| 极特写 | extreme close-up of <eyes/hands/object> |

构图增强词（非特写镜头默认带）：`cinematic composition, foreground and background layers, depth of field,
rule of thirds, subject off-center, negative space`；过肩 `over-the-shoulder`；剪影 `backlit silhouette`；
竖屏 `vertical cinematic framing, subject with headroom and environment`。

## 六、光影与氛围词

`golden hour warm light` 黄金时刻 ／ `backlit silhouette` 逆光剪影 ／ `hard light, high contrast` 硬光高反差 ／
`soft diffused window light` 柔和窗光 ／ `neon glow, cold-warm contrast` 霓虹冷暖 ／ `volumetric light rays` 体积光 ／
`practical lights only, moody low-key` 低调暗部 ／ `overcast flat light` 阴天平光。
光影词**每镜都写**且与相邻镜一致（衔接不跳戏的关键之一）。

## 七、音频设计句式（即梦自带音轨，写了才有）

- 环境音逐拍带：`ambient room tone, distant traffic`、`rain against the window`
- 动作音效点名：`footsteps on marble, fabric rustle, door creak`
- 对白：`she says coldly: "..."`（对白数量 ≤ 节拍数；一拍一句）
- 情绪收束：`sound fades to a low heartbeat at the end`
- 全长镜通用兜底：`keep natural ambient sound throughout`

## 八、按模式的提示词形态

| 模式 | 提示词形态 |
|---|---|
| `multimodal2video` | 完整结构公式（@引用 + 时间码切镜），本规范主战场 |
| `text2video` | 同上但无 @引用——STYLE LOCK 是唯一风格载体，逐字前置，光影/构图词写满 |
| `image2video` | 单拍句式：首帧是什么 + 怎么动 + 运镜一种 + 音效 |
| `frames2video` | 一句话讲"从首帧到尾帧的运镜/演变"：`From the doorway silhouette (first frame), the camera slowly dollies right as she walks to the window (last frame)` |
| `multiframe2video` | 每段 transition-prompt = 一次切镜：`<切镜动词> + 从 kfN 到 kfN+1 的动作演变`，STYLE LOCK 前置到每段 |

## 九、避坑清单（每条提示词交付前自查）

1. 切镜表态了吗？——时间码明切 或 禁切句明禁，二选一，不许裸奔
2. 每个 @引用都声明用途了吗？
3. 同一拍里有没有冲突指令（既 static 又 orbit）？
4. 节拍数与时长匹配吗？4-5 秒里塞不下三个场面
5. 景别是否忠实于分镜（没擅自拉近成特写）？
6. 对白是否只有【对白】（独白/旁白绝不入提示词）？
7. 音频设计写了吗？
8. 光影/时段与相邻镜一致吗（衔接不跳戏）？
9. STYLE LOCK 逐字在最前吗？
10. 引用的图路径真实存在吗（Glob 自查，别烧积分）？

## 十、整镜示例（短剧对峙戏，12s 三拍，multimodal2video）

```
[STYLE LOCK: photorealistic contemporary chinese urban drama, natural skin texture,
cinematic soft key light, teal-orange grade, 9:16 vertical framing]
The woman from @image1 in the mansion living room from @image2.
0-4s: Wide establishing shot, slow push-in — she stands alone by the floor-to-ceiling window,
warm late-afternoon light cutting across scattered documents in the foreground; ambient room tone.
4-8s: Cut to medium close-up — she looks down at the divorce papers, knuckles slowly tightening;
paper crinkle, distant clock ticking.
8-12s: Cut to a low-angle medium shot — the man from @image3 steps out of the shadowed corridor
behind her, deep-focus composition, he says coldly: "三年前你就该认出我。"
Keep natural ambient sound throughout; cinematic composition, shallow depth of field.
```

三拍三个机位三个景别——这才叫"用满即梦的切镜能力"。
