# 铁拳8 中文出招表项目 (Tekken 8 Chinese Movelist Sheets)

本项目为铁拳8角色制作**纯中文屏显出招表**,每角色一个自包含 HTML:
`{slug}_tk8_movelist.html`。页面内置三组即时切换(localStorage 记忆):

- **主题**:夜间(默认,`html.dark`)/ 浅色
- **记法**:按键图(图形化,默认)/ 无数字(纯方位)/ 文字(原始记法)
- 每招带**发生帧列**(首击冲击帧,依 Wavu)

> 2026-07 起废弃打印/PDF 流水线(A4 进阶版、weasyprint、夜间版注入均已删除)。
> 历史打印版如需恢复,参考 git/备份或按 `tools/jun_movelist_source_template.html` 的旧结构重做。

## 发布站点 docs/

`docs/` 是 GitHub Pages 的唯一发布根目录。`docs/index.html` 是角色选择画面风格的
导航主页（自包含单文件，无构建），实现定稿的 Movelist Hub 设计系统：
Saira/JetBrains Mono/Noto Sans SC 字体栈；分组小节布局（核心阵容 32 / 第1季 4 /
第2季 4 / 第3季 4，组头 = Saira kicker + 标题 + 计数）；卡片 = 顶部主题色条 +
头像区 + 字母徽标 + 名牌（中文名/英文名，无 → 箭头；无头像时显示斜体水印英文名）；S3 含 3 张
「即将上线」占位卡（鲍勃/罗杰Jr./范马勇次郎，虚线框、不可点、键盘导航跳过）；
图例条（月燕 d/f+2,3 按键图示例 + LP/RP/LK/RK）；搜索时隐藏空分组。
主页**固定夜间版**（2026-07-22 起移除夜/日切换，浅色下特效效果不佳；boot script
无条件加 `html.dark`，忽略 `tk-theme`）；仅与角色页共享 `tk-notation`（gfx/txt）偏好，
角色页自身的夜/日切换不受影响。
角色主题色以角色页实际 `--acc` 为准（设计稿中 jun/clive 两色有出入，未采用）。

主页特效 = **flux v3「电脉·框流」**（2026-07-22 定稿，spec:
`design/specs/2026-07-22-homepage-circuit-pulse-design.md`）：电弧沿卡框环游、
跳电接力到相邻角色（3 条领地链 + 小分区各 1 条），阵型雷击（横扫/纵劈/对角/
十字/外扩/风暴/连锁）每 5~9s 一次；旧色团呼吸降为近静态垫底；悬停光环保留。
QA：`workbench/qa/flux-check.mjs`（28 断言）+ `flux-perception.mjs`（多窗口帧差）；
原型演练场 `workbench/qa/flux-ladder.html`。改参数先动原型再移植，两个 QA 必须过。

- 头像（可选）：放 `avatars/{slug}.png`（slug 如 jin/kazuya/deviljin/armorking…见卡片
  `<img>` src）。加载成功自动加 `.hasimg` 隐藏水印与字母徽标（避免与人物图重叠）；
  失败 `onerror` 移除 `<img>`，回退为徽标+水印，页面始终完整。
- 新增角色：在对应分组 `.grid` 复制一张 `<a class="card" style="--acc:主题色"
  data-q="中文名 英文名">` 卡片并更新组头计数与搜索行总数；未上线角色用
  `<div class="card soon">` 占位（见 S3 示例）。

## 角色页标题带（2026-07-25 改版，Claude Design 方案 A「铭牌」）

41 页共用同一张标题带（spec 来源：Claude Design `Character Page · Avatar.dc.html`，
treatment A）：

- **头像编入标题带**：`header > .hero > img`，用横竖双向遮罩 `mask-composite: intersect`
  溶进渐变。选 A 而非 B（边栏）是因为实测——版心 1120px × `zoom:1.25` 后，
  1480px 视口只剩 64px 留白，B 承诺的「表格宽度不变」要 ≥1700px 才成立。
- **深色垫板**：`.hero::before` 是一块同样遮罩、`opacity:.5` 的 `#0a0d11`。头像是
  深底白描，只有 `mix-blend-mode: lighten` 才能抠掉黑底，而 lighten 只在深色背景上
  成立——熊猫/莉莉这类近白主题色下头像会整个消失。垫板让它无论主题色深浅都落在深底上。
- **切换上移**：主题/记法两组切换进入 `.hdrtop` 右侧，与返回面包屑同行。
- **官方档案行** `dl.hdrbio`：国家 · 拳法 · 架势。前两项来自 tekken.com 官方 fighter
  页（`fetch_official_profiles.py` 抓取 → `official_profile_zh.py` 译），架势由
  `stance_sections` + `{key}_zh.json` 的 `section_names` 推导。**不写「定位/打法评价」**
  ——那是主观内容，与「不补写未经来源验证」相抵触。
- **图例按记法切换**（2026-07-25 起 41 页统一，真值 `tools/legend_card.css`）：
  `.legend > .lgtop`（判定/发生，讲的是表格列，恒显）+ `.lgsub.gfx-only`（按键图/无数字）
  与 `.lgsub.txt-only`（文字）互斥。分隔线颜色两家不同，经 `--lg-line` 中转，各自
  在 `.legend` 上绑定一次。管线页原本是逐角色手写的单行「指令说明」，两种记法下都常驻；
  改造时其**专属尾巴原样保留**（凌晓雨的架势表、克莱夫/国光二世的 `qcf`·`~F` 记号、
  洛的 `龙构=龙构架势(DSS)`），登记在 `patch_legacy_pages.py` 的 `LEGEND_EXTRA`——
  那是针对页面手写的内容，无法从任何快照重新生成。
  `page-intro` 从标题带移到页脚。

## 角色页 → 主页 返回导航

2026-07-24 起 41 页统一带两个回主页入口（spec:
`design/specs/2026-07-24-movelist-back-navigation-design.md`，来源 Claude Design 方案 1a + 2b）：

- **面包屑**：`header#top` 内第一个子元素 `.homerow > a.home`，独占一行，沿用 `.ntgl .seg`
  的白色描边胶囊。纯 `<a href="index.html">`，断 JS 仍可用，是保底入口。
- **上滑浮现顶栏**：`nav.revealbar`（`<body>` 首个子元素），`position:fixed` 默认收在视口外，
  **仅在向上滚动且已离开 banner 时**滑出。收起时同时切 `visibility` —— 只用 `transform`
  位移的元素仍会被 Tab 聚焦。是否"已离开 banner"用 `IntersectionObserver` 观察 `#top` 判定，
  比像素阈值更可靠（`body` 有 `zoom:1.25`，像素常量在两套坐标系间含义不稳）。
- **智能返回**：`[data-home]` 若来源是同源同目录的 `index.html` 则走 `history.back()`，
  保住主页滚动位与搜索词；带修饰键的点击一律放行。

CSS/JS 唯一真值在 `tools/back_nav.css` / `back_nav.js`，**两套页面逐字共用**；因此只依赖
两家都成立的东西（`color: inherit`、写死的 `--bg` 实值），强调色经 `--bn-accent` 中转，
由各自样式块赋值一次。改动后：生成器页重建，管线页跑 `python tools/patch_legacy_back_nav.py`。

## 三语构建（2026-07-26）

站点出三份：简体 `docs/`（`zh-CN`，**URL 一寸不动**，持有现有排名）、繁體
`docs/zh-Hant/`（`zh-Hant`）、英文 `docs/en/`（`en`）。语系表与三列 chrome 文案的
唯一真值是 `tools/locales.py`；`build_season2.py --locale` 可单独构建一支。

- **繁體在构建期转换**，不产生第三份快照。`tools/opencc/` 逐字签入 OpenCC 的四个
  词典，`tools/zh_hant.py` 自己走 s2twp 的三段链——构建因此仍是离线、零依赖、
  逐字节可复现。等价性由 `tools/verify_zh_hant.py` 对真 OpenCC 全语料对拍
  （6924 条 0 不一致），换词典后必须重跑。逐 move id 的例外写 `zh_hant_overrides.json`，
  陈旧条目会让 `check_zh.py` 失败。
- **「简体专用字」的判定有两个条件**：该字不在自己的 STCharacters 候选里（否则
  香格里拉的 `里`、征服者的 `征`、背后的 `后` 会被误杀），**且**整条链真的会改它
  （否则 `峰→峯→峰`、`秘→祕→秘` 这类回环会被误杀）。
- **chrome 文案手写三列**，不机器转换：`记法→記法` 是机械的，但 `数据→資料`
  是台湾用词。语料（招式/分区/架势名）走转换器。
- **英文招式名只来自 Wavu**。Wavu 未命名的招式显示斜体中文 + `ZH` 标，
  **绝不回译**；逐角色数量锁在 `season2_config.EXPECTED_ZH_FALLBACKS`
  （全站 1128 条，约五分之一），静默上涨即回归。
- **指令列不翻译**，只有 `.tk-state` 胶囊本地化，英文用 Wavu 码（背身时→BT）。
  胶囊词汇有四个来源，全部经 `locales.notation()`：`COMMON_PREFIXES`、
  `expand_command` 的回退默认值、`COMMON_COMMAND_ALIASES`、以及
  `pipeline.parse_cmd` 的 `STANCE_ABBR`。
- **判定列**：英文 1~3 段拼写全称（High/Mid/Low），超过 3 段改用缩写——
  勒罗伊七段连拳拼全称是四行、撑爆行高，十连技十七段更是撑爆整张表；全称留在 title。
- **行高按语系**：中文 38px、英文 46px（`html.loc-en`）。英文靠行高而非列宽换空间，
  指令列在两张表里都保持中文的宽度份额（主表 37%、投技表 34%）——规格把投技表压到
  28% 是错的，实测溢出。
- **主页**：`docs/index.html` 仍手写，另两份由 `tools/build_hub.py` 派生；
  `augment_hub.py` 负责语言控件与 `data-q` 的繁體检索词（三语共用同一份检索索引）。
- `docs/sitemap.xml` 由 `tools/build_sitemap.py` 按磁盘实际页面生成（116 条 URL），
  只给真实存在的语系发 `xhtml:link`。
- **5 个管线页只有简体**，暂不在语系契约内（见
  `design/plans/2026-07-26-pipeline-page-migration.md`）。

## 已完成角色

**全员到齐**：基础 32 人 + S1 DLC 4 人 + S2 DLC 4 人，共 41 页（2026-07）。

一次式管线角色（tools/pipeline.py，勿重跑转换）：

| 角色 | 页面主题色 --acc | 帧数据 |
|------|------------|--------|
| 风间准 (Jun) | #7ed6b8 | tools/wavu_jun.txt (125/129) |
| 凌晓雨 (Xiaoyu) | #ff9fce | tools/wavu_xiaoyu.txt (132/136) |
| 国光二世 (Kunimitsu II) | #ff93a6 | tools/wavu_kunimitsu.txt (122/122) |
| 克莱夫 (Clive) | #9db9ff | tools/wavu_clive.txt (95/96) |
| 马歇尔·洛 (Law) | #ffe07a | tools/wavu_law.txt (159/170) |

可重复生成器角色（tools/build_season2.py，源快照在 tools/source/）：

| 角色 | 页面主题色 --acc | 帧数据 |
|------|------------|--------|
| 风间仁 (Jin Kazama) | #6fb3ff | tools/wavu_jin.txt (133/144) |
| 安娜·威廉斯 (Anna Williams) | #e07a8f | tools/wavu_anna.txt (169/183) |
| 法昆拉姆 (Fahkumram) | #6fe0c9 | tools/wavu_fahkumram.txt (142/147) |
| 铠甲王 (Armor King) | #7f8fb3 | tools/wavu_armor_king.txt (169/182) |
| 米亚莉·佐 (Miary Zo) | #c9e896 | tools/wavu_miary_zo.txt (115/130) |
| 三岛一八 (Kazuya Mishima) | #b18cff | tools/wavu_kazuya.txt (136/160) |
| 保罗 (Paul Phoenix) | #ff8087 | tools/wavu_paul.txt (141/177) |
| 金 (King) | #e8a04c | tools/wavu_king.txt (213/255) |
| 拉斯 (Lars Alexandersson) | #8fa8ff | tools/wavu_lars.txt (130/140) |
| 杰克-8 (Jack-8) | #a9cf74 | tools/wavu_jack8.txt (220/229) |
| 妮娜·威廉斯 (Nina Williams) | #d8a9ff | tools/wavu_nina.txt (186/211) |
| 勒罗伊 (Leroy Smith) | #9db4c9 | tools/wavu_leroy.txt (138/147) |
| 风间飞鸟 (Asuka Kazama) | #7fc4e8 | tools/wavu_asuka.txt (156/163) |
| 莉莉 (Lili) | #cdd6e0 | tools/wavu_lili.txt (142/156) |
| 布莱恩 (Bryan Fury) | #9ad0c2 | tools/wavu_bryan.txt (168/175) |
| 花郎 (Hwoarang) | #ff8f4d | tools/wavu_hwoarang.txt (210/225) |
| 克劳迪奥 (Claudio Serafino) | #bcd4ff | tools/wavu_claudio.txt (103/117) |
| 阿苏塞娜 (Azucena) | #d9a878 | tools/wavu_azucena.txt (138/165) |
| 雷文 (Raven) | #9f86d9 | tools/wavu_raven.txt (172/195) |
| 雷欧 (Leo) | #e0c187 | tools/wavu_leo.txt (139/148) |
| 史蒂夫 (Steve Fox) | #84a9e0 | tools/wavu_steve.txt (165/189) |
| 熊 (Kuma) | #c99b6e | tools/wavu_kuma.txt (141/150) |
| 熊猫 (Panda) | #e6e9ee | tools/wavu_panda.txt (134/144) |
| 吉光 (Yoshimitsu) | #7fd6a8 | tools/wavu_yoshimitsu.txt (330/376) |
| 沙欣 (Shaheen) | #e8cf9a | tools/wavu_shaheen.txt (101/106) |
| 德拉古诺夫 (Sergei Dragunov) | #aab6c2 | tools/wavu_dragunov.txt (153/165) |
| 冯威 (Feng Wei) | #b5d98a | tools/wavu_feng.txt (155/168) |
| 李超狼 (Lee Chaolan) | #c39bff | tools/wavu_lee.txt (162/174) |
| 阿丽莎 (Alisa Bosconovitch) | #ffb3c6 | tools/wavu_alisa.txt (172/197) |
| 扎菲娜 (Zafina) | #c98fd0 | tools/wavu_zafina.txt (150/164) |
| 恶魔仁 (Devil Jin) | #a17fe0 | tools/wavu_devil_jin.txt (149/160) |
| 维克多 (Victor Chevalier) | #de9fe6 | tools/wavu_victor.txt (131/139) |
| 蕾娜 (Reina) | #cf9ef0 | tools/wavu_reina.txt (168/192) |
| 艾迪 (Eddy Gordo) | #9fd97f | tools/wavu_eddy.txt (163/176) |
| 莉迪亚 (Lidia Sobieska) | #ffb0a6 | tools/wavu_lidia.txt (151/174) |
| 三岛平八 (Heihachi Mishima) | #ffcf66 | tools/wavu_heihachi.txt (139/152) |

`—` 表示 Wavu 快照未给出可用的首击发生帧;常见于当身/防反、架势进入和纯移动
动作,不应凭招式动画推测补值。

## 图形记法组件(设计定稿)

来源:`design/notation-wireframe/`(README + demo.html + tekken-input-notation.css,
生产级 CSS 直接内联进各 HTML)。核心约定:

- 2×2 单色按键方阵 `.tk-b`(1左上 2右上 3左下 4右下;按下 `.on` 实心,未按幽灵格)。
  页面额外规则:指令格里未按键**不显示数字**;「无数字」模式按下键也隐藏数字。
- 方向 = clip-path 粗箭头 `.tk-dir f|b|u|d|df|db|uf|ub`,按住(大写)加 `.hold` 套圈;
  `qcf` 渲染为 d·df·f 三箭头;N = `.tk-n`。
- 状态/条件前缀 = 主题色胶囊 `.tk-state`(背身时/凤凰中/WS→起身中…);
  按键图与箭头恒单色,主题色只用于胶囊与标签(`--tk-acc`,每角色一色)。
- 分隔:`›` 接续 · `+` 方向+键 · `~` 紧接 · `＊` 蓄力 · `→` 下一招(连招);
  `T!`/`CH`/`SWL` 等标记 = `.tk-tbang` 橙色徽标。
- 双 span 结构:`<span class="cmd-gfx">图形</span><span class="cmd-txt">原文</span>`,
  记法切换纯 CSS(body class),断 JS 仍可读。
- 解析守卫:含杂散字母/数字(BnB、H.2、+5)或纯文字的格整格回退原文;
  连招/十连所在全宽区不限方阵数,窄表超 6 个方阵回退文字。

## 新角色流程

1. **数据**:Wavu Wiki 唯一数据源(fandom 已弃用,错误多)。有 Anubis 反爬,
   必须真实浏览器(Claude in Chrome),加载后等 3~4 秒:
   - 出招表 `wavu.wiki/t/{Char}_movelist`:`.movedata` 卡片;**完整指令在卡片 `id`**
     (`{Char}-df+2,3`),`.movedata-startup` 为发生帧;输出含零宽字符需清理,
     结果超长需分片(存 window 变量再 slice)。存为 `tools/wavu_{char}.txt`(`input|startup` 每行)。
   - 连招 `wavu.wiki/t/{Char}_combos`。
2. **基础 HTML**:按 `tools/jun_movelist_source_template.html` 的结构手工制作
   (header/legend/投技/打击技 cols2/架势 lt 表/热能/十连技/tipsPage 攻略区,
   含夜间覆盖 `<style>` 块与 zoom 1.25 注入;翻译准则见下节)。
3. **跑管线**:在 `tools/pipeline.py` 的 CONFIG 加角色条目——
   `acc/acc_ink`(页面主题色/深色变体)、`states`(中文状态词,供胶囊分词)、
   `prefix`(中文前缀→Wavu 记法前缀,如 背身时→BT.、凤凰中→AOP.;
   当身类映射为 "" 或对应序列,查不到自动显示 —)。然后
   `python tools/pipeline.py {char}`(幂等,含 tk-notation 即跳过)。
   管线自动完成:指令图形化、连招表全宽一行一条、3 列架势区改 2×2、
   发生帧列、主题合并与三组切换注入、标题去「夜间版」。
4. **校验**:headless Chrome 全页截图逐段读图
   (`chrome --headless=new --screenshot=... --window-size=1480,6600`),
   另用注入 click 的副本验证 浅色/无数字/文字 三种模式;帧 MISS 列表逐条核对
   (真缺=当身/架势进入,可修=前缀映射缺失)。

### 可重复生成流程（通用，36 角色）

除上述 5 个管线角色外，全部角色（jin + S2 四人 + 2026-07 批量的 31 人）都由
`tools/build_season2.py` 从结构化源数据生成，不走一次式 `pipeline.py` 转换：

1. 每角色源快照位于 `tools/source/{key}.json`、`{key}_zh.json`、
   `{key}_combos.json`；对应发生帧索引保存在 `tools/wavu_{key}.txt`。
2. 新角色接入顺序：抓取（见 KNOWLEDGE §7 批量管线）→ 写 `{key}_zh.json`
   （`python tools/check_zh.py {key}` 校验契约：全 ID 覆盖、纯中文、
   stance 前缀完备、按键图零回退）→ 在 `season2_config.py`、
   `test_season2_pages.py`、`validate_season2.mjs` 三处登记
   （期望值用分区/覆盖率脚本推导，勿手算）→ 构建 → 门禁。
3. 运行 `pwsh -File tools\validate_season2.ps1`：单一入口会重建全部自包含 HTML，
   执行生成器与 Law 回归，并用 Playwright 按每角色 10 状态（桌面 6 + 响应式 4）
   校验 UI、几何、裁切、状态恢复与 console 错误（36 角色共 360 状态），另跑 5 个管线页
   × 3 记法共 15 状态的图例可见性检查（这 5 页不在 360 状态门禁内），并检查
   `docs/` 发布边界、主页链接、头像清单、免责声明与本地资源完整性。
   仅做非浏览器快速检查时可加 `-SkipBrowser`；最终交付不应跳过浏览器门禁。
   `$env:CHARACTERS='jin,king'` 可过滤角色，`$env:SCREENSHOT_DIR` 保留全页截图。
4. 设计内文字回退（>6 方阵窄表）登记在测试的 `EXPECTED_GFX_FALLBACKS`；
   已核实的超大伤害真值（如 Gigaton Punch 199）登记在 `KNOWN_BIG_DAMAGE`。

这些页面有修改时应改源快照或生成器后重建，不要直接手改生成的 HTML。

## 翻译准则(纯中文招式名)

- 日文技名用对应汉字直取:月读、天丛云、白拍子、时雨、彼岸花…
- 神话/FF等专有名词用通行中文译名:审判之雷、十亿核爆、日珥、斩铁剑、昆古尼尔…
- 英文描述性技名意译:White Heron Dance→白鹭之舞、Dragon Wheel Kick→龙车踢。
- 指令保留通用记号:f/b/u/d、d/f、WS、FC、SS、qcf、+、~F;架势名在指令列用中文。
- 判定:High=上、Mid=中、Low=下、Throw=投、!=不可防御;
  Wavu target 列 sl/sm=特下/特中、大写=可击中倒地。
- 页脚署名:`数据来源:Wavu Wiki (wavu.wiki/t/{X}_movelist · {X}_combos) · 打法参考:{来源} · 招式名为中文意译,供参考`

## 排版与主题要点

- 单文件、内联 CSS;字体 "Noto Sans SC"/"Microsoft YaHei",记法组件用等宽栈。
- 夜间样式全部作用域于 `html.dark`(由 head 内 boot script 依 localStorage 先行打标,
  防白闪);浅色 = 无 .dark 时的基础样式 + `.tk-in` light 变量(墨色、关辉光)。
- 屏显缩放:`@media screen { body { zoom: 1.25 } }`(4K 250% 第二屏用)。
- 跨列大区块用布局表格 `table.lt > td.ltc`;架势区超过 2 列会在管线里改 2×2。
- 连招表 `table.cb`:全宽、一条一行、加大行距、起手列右分隔线。
- **白字不压原始主题色**(2026-07-25):41 个 `--accent` 是按"深色页上的点缀"选的,
  都很浅,白字压上去从 3.2:1 一路掉到熊猫的 1.2:1(等于看不见)。凡是白字压角色色的
  表面——分区标题 `h2`、标题带渐变亮端(`--hc-accent`)——一律改用 **`--accent-band`**:
  由 `tools/accent_contrast.py` 把 `--accent` 朝 `--accent-ink` 压深,**逐角色**取
  仍能让白字过 WCAG AA(4.5:1)的最大主题色比例,构建时算成字面 hex 写进页面
  (生成器写 `<body style>`,管线页写注入的 `legacy-chrome` 块)。深色主题色角色因此
  几乎不变,近白色角色让出大部分。**不要给这些表面上的文字加 `opacity`**——band 是按
  不透明白字标定的,`h2 .en` 原来的 `.75` 会把 4.5 打回 3.2。
  门禁两道:`test_site_publication` 逐页算 `--accent-band` 对比度并检查引用,
  浏览器门禁按计算样式实测 `h2` / `h2 .en`(360 生成器状态 + 15 管线状态)。

## tools/ 目录

- `KNOWLEDGE.md` — **约定/陷阱/事故教训知识库,新角色动工前必读**
- `pipeline.py` — 一次式转换管线(旧 5 角色;解析器 parse_cmd 被生成器复用)
- `build_season2.py` / `season2_config.py` / `season2_page.css` / `season2_page.js` — 全部生成器角色(36)的可重复页面生成器、配置与前端资源
- `header_card.css` / `legend_card.css` / `back_nav.css` / `back_nav.js` — **41 页共用**的
  标题带（头像 + 标题 + 官方档案行）、按记法切换的图例、返回导航（面包屑 + 上滑浮现顶栏）
  唯一真值,由生成器拼进 PAGE_CSS/PAGE_SCRIPT,也由管线页补丁脚本注入;改这里后两边都要
  重新产出
- `patch_legacy_pages.py` — 给 5 个管线页注入同一套标题带、图例与返回导航的幂等补丁脚本;
  `--check` 模式已接入门禁,页面与共享资源脱节即失败
- `fetch_official_profiles.py` / `source/official_profiles.json` — 从
  tekken.com 官方 fighter 页抓取 称号/国家/拳法 的抓取器与快照(离线构建)
- `official_profile_zh.py` — 官方英文档案 → 中文的对照表;遇到未登记词条直接报错,
  绝不让英文漏进纯中文页面
- `accent_contrast.py` — WCAG 对比度与 `band_color()`:把主题色朝其 ink 压深到白字过 AA
  为止,**两套页面共用**,保证是构建期可断言的,而不是 CSS 里赌一把
- `check_zh.py` — 单角色翻译契约检查(ID 覆盖/纯中文/stance 前缀/按键图回退)
- `scan_gfx_fallbacks.py` — 扫描 41 页 td.cmd 未图形化格子（主表回退快查）
- `scan_combo_literals.py` — 连招区 combo-literal 回退清单（分类统计英文残句/架势码/伤害标注；不含 COMBO_STANCE_ALIASES 合并，eddy 的 MD 类别名在构建页生效）
- `test_season2_pages.py` — 数据、分区、DOM 与幂等回归测试(36 角色)
- `validate_season2.ps1` / `validate_season2.mjs` — 重建、回归测试与 360 状态 Playwright 几何门禁的单一入口(支持 CHARACTERS 过滤)
- `source/{key}.json` / `{key}_zh.json` / `{key}_combos.json` — 结构化源快照
- `wavu_{char}.txt` — 各角色 input|startup 帧数据(浏览器抓取存档)
- `jun_movelist_source_template.html` — 管线处理前的 Jun 基础 HTML 结构示例
