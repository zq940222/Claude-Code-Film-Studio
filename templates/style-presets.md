<!-- 风格预设库：由 /new-drama 技能读取（技能有插件根访问权），供用户选定"整体视频风格"。
     选定后，把对应预设的【STYLE LOCK】关键词块逐字写入项目的 03-design/style-bible.md（单一真源），
     此后美术出图、摄影写视频提示词、精剪调色都以 style-bible.md 为准，保证全剧风格一致。
     agent 不读本文件（agent 不知道插件根位置）——只读工作区的 style-bible.md。 -->

# 风格预设库（Style Presets）

风格一次选定、全剧锁定：像小云雀那样先定"整体画风"，之后所有镜头/所有集都保持一致。
按 **真人 / 2D / 3D** 三大类组织（对标小云雀风格库的分类）；不够用就选 `custom` 让美术现拟。

机制 = **每条图像/视频提示词都逐字前置同一段 STYLE LOCK 关键词**（写在 style-bible.md 里），
外加角色/场景设定图本身按此风格生成——两者合力锁住色调/光影/质感/画风。

**一致性的边界（对用户诚实）**：
- 含角色镜头（`multimodal2video`）靠 @引用的设定图承载主要风格信号，STYLE LOCK 是加固；
- 纯空镜（`text2video`）没有图锚点，**STYLE LOCK 是唯一的风格载体**，漂移风险最大——这类镜头尤其要原样前置；
- 设定图必须**按选定风格生成**，否则图与关键词打架。整体是"强一致"，非逐帧像素级一致。

选型建议：短剧/短片 → `真人` 类（默认 `cn-urban-realist`）；动漫 → `2D` 或 `3D` 类。
Seedance 无风格 LoRA/模型开关——所有风格都靠"提示词关键词 + 设定图画风"实现，不是切模型。

每个预设含：`id`、中文名、类别、适用形态、**STYLE LOCK（逐字复用的英文关键词块）**、调色意图（供精剪）、备注。

---

## 真人（live-action / photoreal）

### `cn-urban-realist` 国产都市写实
- 类别：真人；适用：short-drama（默认）/ short-film
- STYLE LOCK：`photorealistic contemporary Chinese urban drama, true-to-life skin and materials, natural cinematic lighting, shallow depth of field, 35mm look, clean neutral color, subtle film grain`
- 调色意图：自然写实、略暖肤色、对比适中
- 备注：都市逆袭/甜宠/职场等现代题材的稳妥底色（对标小云雀"国产都市写实"）

### `korean-soft` 韩剧都市柔光
- 类别：真人；适用：short-drama（甜宠/都市/虐恋）
- STYLE LOCK：`Korean urban drama aesthetic, clean cool tone, soft diffused daylight, pastel palette, gentle skin glow, high-key soft lighting, delicate bokeh`
- 调色意图：冷调清透、高调柔光、低饱和
- 备注：干净氛围感、偏女性向（对标"韩剧都市柔光"）

### `jp-slice-of-life` 日式生活自然
- 类别：真人；适用：short-film / short-drama（治愈/生活流）
- STYLE LOCK：`Japanese slice-of-life film aesthetic, natural window light, muted earthy palette, understated everyday realism, soft film grain, tender quiet atmosphere, gentle handheld feel`
- 调色意图：低饱和自然、柔和、留白呼吸
- 备注：治愈/生活流/文艺（对标"日式生活自然"）

### `cinematic-film` 电影质感（青橙）
- 类别：真人；适用：short-film / short-drama（高级感）
- STYLE LOCK：`cinematic film look, anamorphic widescreen feel, teal-and-orange grade, dramatic key light with soft shadows, rich contrast, 35mm film grain, shot on cinema camera`
- 调色意图：青橙电影感、高对比、冷暖分离
- 备注：想要通用"电影感"时选它

### `film-90s-realist` 90年代写实电影
- 类别：真人；适用：short-film / short-drama（怀旧/年代）
- STYLE LOCK：`1990s realist film look, Kodak film stock grain, naturalistic available light, slightly desaturated palette, documentary-like realism, period-accurate details`
- 调色意图：胶片颗粒、略去饱和、自然光
- 备注：年代感、纪实质感（对标"90年代写实电影风格"）

### `retro-narrative` 复古叙事电影
- 类别：真人；适用：short-film / short-drama
- STYLE LOCK：`retro narrative cinema, warm nostalgic 1970s-80s palette, soft golden light, gentle film grain, cozy storytelling mood, vintage lens rendering`
- 调色意图：暖怀旧、柔金光、颗粒
- 备注：温情叙事、复古（对标"复古叙事电影风格"）

### `hollywood-retro` 美式复古好莱坞
- 类别：真人；适用：short-film / short-drama
- STYLE LOCK：`classic American Hollywood cinema, glamorous studio lighting, rich warm tones, elegant high contrast, timeless silver-screen film look, cinematic sheen`
- 调色意图：暖调、优雅高对比、影棚光
- 备注：好莱坞黄金年代质感（对标"美式复古好莱坞"）

### `cn-rural-90s` 90年代中国农村电影
- 类别：真人；适用：short-film / short-drama（年代/乡土）
- STYLE LOCK：`1990s Chinese rural film aesthetic, earthy sun-baked palette, warm dusty light, naturalistic countryside realism, fifth-generation cinema mood, film grain`
- 调色意图：土黄暖尘、自然、颗粒
- 备注：乡土年代、第五代影调（对标"90年代中国农村电影风格"）

### `wuxia-realist` 武侠江湖写实
- 类别：真人；适用：short-drama / short-film（武侠/古装动作）
- STYLE LOCK：`realistic wuxia jianghu cinematography, gritty naturalistic light, earthy muted tones, atmospheric mist and dust, cinematic martial-arts realism, film texture`
- 调色意图：写实、雾尘氛围、低饱和
- 备注：写实武侠（非华丽古偶，对标"武侠江湖写实摄影风格"）

### `ancient-ornate` 古装华丽（古偶）
- 类别：真人；适用：short-drama / short-film（古偶/宫廷/仙侠）
- STYLE LOCK：`lavish Chinese period costume drama, ornate silk and embroidery detail, palace and ancient architecture, warm golden-hour or candlelight, rich saturated jewel tones, cinematic`
- 调色意图：暖金、饱和宝石色、华丽
- 备注：古偶/宫斗/仙侠（华丽向，与写实武侠区分）

### `hk-retro` 港风复古
- 类别：真人；适用：short-drama / short-film
- STYLE LOCK：`1990s Hong Kong cinema style, nostalgic neon and tungsten lighting, warm-green tint, grainy retro film stock, moody urban night, practical light sources`
- 调色意图：怀旧霓虹、暖绿偏色、颗粒
- 备注：复古港片、江湖、暧昧夜戏

### `cyberpunk-neon` 霓虹赛博电影
- 类别：真人；适用：short-film / 科幻题材
- STYLE LOCK：`cyberpunk cinema aesthetic, neon-drenched rainy megacity, holographic signage, high-contrast magenta-cyan lighting, wet reflective surfaces, futuristic sci-fi`
- 调色意图：霓虹紫青、高对比、湿反光
- 备注：科幻/未来/赛博（对标"霓虹赛博电影风格"）

### `guofeng-ink` 国风水墨
- 类别：真人（写意）；适用：short-film / 古装题材
- STYLE LOCK：`Chinese ink-wash aesthetic, guofeng, elegant negative space, muted ink tones with occasional vermilion accent, soft mist, poetic composition, rice-paper texture`
- 调色意图：水墨淡雅、留白、朱砂点缀
- 备注：写意、诗意空镜出彩

## 2D（动画 / 手绘 / 插画）

### `anime-2d` 日系动漫（2D 手绘）
- 类别：2D；适用：anime
- STYLE LOCK：`modern Japanese anime style, 2D cel shading, clean line art, vibrant flat colors, expressive large eyes, detailed anime background art, key-frame quality`
- 调色意图：鲜明平涂、动漫感、干净线条
- 备注：**动漫番剧首选**；即原"锁定二次元流派逐字复用"的预设化

### `anime-retro-90s` 90年代复古动漫
- 类别：2D；适用：anime
- STYLE LOCK：`1990s retro anime style, hand-painted cels, warm nostalgic color, visible film grain, retro linework, vintage OVA aesthetic`
- 调色意图：怀旧暖色、手绘颗粒
- 备注：复古赛璐璐/OVA 味

### `donghua-guofeng` 国漫国风
- 类别：2D；适用：anime / short-film
- STYLE LOCK：`Chinese donghua guofeng animation, elegant ink-and-color blend, flowing traditional aesthetics, vivid guofeng palette, detailed oriental art`
- 调色意图：国风重彩/水墨融合
- 备注：仙侠/国风动画

### `painterly-2d` 厚涂插画 / 油画
- 类别：2D；适用：short-film / anime（艺术向）
- STYLE LOCK：`painterly illustration style, thick oil-paint brushstrokes, storybook art, rich textured color, dramatic painted lighting, concept-art quality`
- 调色意图：厚涂笔触、绘本质感、戏剧光
- 备注：艺术短片/概念感

## 3D（三维 / CG）

### `cartoon-3d` 3D 卡通（皮克斯感）
- 类别：3D；适用：anime / short-drama（轻喜/亲子）
- STYLE LOCK：`3D cartoon render, Pixar-like stylized characters, soft global illumination, rounded appealing shapes, vivid colors, subsurface skin, polished CGI`
- 调色意图：明快、柔和全局光、CG 质感
- 备注：3D 动画质感

### `cg-realistic-3d` 3D 写实 CG
- 类别：3D；适用：short-film / 科幻奇幻
- STYLE LOCK：`photoreal 3D CG render, physically based materials, cinematic global illumination, realistic detail and textures, high-fidelity CGI, filmic tone`
- 调色意图：写实 CG、影级布光
- 备注：科幻/奇幻/特效向

## 自定义

### `custom` 自定义
- 类别：任意；适用：全部
- 由美术指导按用户描述**现拟一段 STYLE LOCK**（同样是英文关键词块，写进 style-bible.md），此后同样逐字复用锁定。
- 用户想"复刻某个参考视频/影片风格"时选它，把参考要素翻译成关键词；如手上有参考视频，摄影可另用 `multimodal2video --video` 做风格参考（进阶，见 seedance-prompt-en）。

---

## 用法（/new-drama 与各 agent 遵循）

1. `/new-drama` 建项时按 medium/类别推荐并让用户选一个 `id`（含 `custom`）；写入 `project.json` 的 `format.style`。
2. `/new-drama` 把该预设的 **STYLE LOCK 块逐字**写入 `03-design/style-bible.md` 的固定标题区 `## 风格锁 STYLE LOCK（逐字复用，勿改）`（由 /new-drama 建桩，美术/摄影/精剪都按这行标题定位）。
3. `/design` 起、在美术出图前，可让用户确认或改风格（改风格 = 已出的设定图/视频作废需重来，同 ratio 约束）。
4. 美术指导按 STYLE LOCK 生成设定图，并保留该块逐字不改；摄影每条视频提示词逐字前置 STYLE LOCK；精剪按"调色意图"选一个校验过的剪映滤镜。

> 风格库随需扩充：新增预设＝在对应类别下加一段（`id`+中文名+类别+适用形态+STYLE LOCK+调色意图），无需改任何 agent。
