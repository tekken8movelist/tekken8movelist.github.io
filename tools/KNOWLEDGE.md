# 铁拳8 出招表 · 制作与转换知识库

面向未来跑新角色的任何 agent(Claude / Codex)。CLAUDE.md 讲流程,这里讲**约定、
陷阱与事故教训**。除非有意改设计,违反本文即是 bug。

## 1. 源 HTML 记法规范(手写基础 HTML 时必须遵守)

解析器(tools/pipeline.py)按以下约定断词;写错的记法会静默回退成文字或产生矮行。

- **回中必须大写 `N`**(`u/f, N, 4`)。小写 `n` 不在词表,整格作废。
  ▸ 事故:洛「升龙炮」写成 `u/f,n,4`,图形模式退化为 9px 小字,行高 25px,
  右栏整列错位 13px。
- **按住 = 方向大写**:`~F`、`B+1`、`D/F+1`、`U/B`。`f,f` 前冲写小写,
  匹配帧数据时管线自动升为 wavu 的 `f,F+`。
- **逗号三义**由上下文决定:方阵之间 = 接续(渲染 `›`);方向之间 = 连按(箭头
  相邻无分隔);`,N,` 中的回中会在帧匹配时剥离。
- **括号三义**:`(或 …)` = 备选,内部会被继续图形化;`(+53)` = 伤害标注,保留
  文字;含其他中文 = 条件注记,整段保留文字,但**帧匹配时视作接续逗号**
  (`f+2 (命中时) 1+2` → `f+2,1+2`)。
- **斜杠**:`d/f` 是方向;带空格的 ` / ` 是并列备选(帧数取第一个)。
- **状态/条件前缀写中文**,必须收录进该角色 config 的 `states`(供胶囊分词)和
  `prefix`(供帧匹配)。新词不收录 = 胶囊断错 + 帧 MISS。
- **杂散字母/数字守卫**:格内出现 BnB、H.2、i11、+5 之类,整格回退文字——这是
  特性不是 bug,别想着"修好它",标签格就该是文字。
- **十连放全宽区**(一条一行);窄表里超过 6 个方阵会自动回退文字。
- **列序统一**:打击技 `招式|指令|发生|伤害|判定`;投技 `招式|指令|发生|方向|
  伤害|挣脱`——**挣脱列是投技表的核心信息,不许省**(洛初版丢了,返工)。
- 连招表头带附注 `(T!=回旋 · ~F=按住前 · →=下一招)`;页首图例要解释该角色
  专属架势缩写(如 龙构=DSS)。

## 2. Wavu 抓取规范

- 必须真实浏览器(Anubis 反爬),加载后等 3~4 秒。
- **完整指令在 `.movedata` 卡片的 `id` 里**(`Law-df+2,3`),`.movedata-input`
  的 textContent 对连段只有尾段(前缀被洗白成独立节点),别用。
- **不要直接拼 `textContent` 读取多段字段**:Wavu 会把伤害、判定、发生帧拆成
  lead/tail 节点;节点边界本身不保证含逗号。逐个读取
  `.movedata-damageLead` / `.movedata-damage`(判定与发生帧同理),清理零宽字符,
  tail 无前导分隔符时主动补逗号。抓取后把三位以上的伤害 token 当硬错误拦截;
  `1523`、`3538` 这类通常是 `15,23`、`35,38` 被错误黏合。
- 发生帧取 `.movedata-startup`;清理零宽字符 `/[​‌‍﻿]/g`;
  结果超长必须存 window 变量分片输出(直接返回会被截断)。
- 存档格式 `input|startup` 每行,写入 `tools/wavu_{char}.txt`。
- **键名统一下划线式**:`Left_Throw`、`(Back_to_wall).`、`(Airborne).`,
  不要空格式(洛初版用空格式,与其他角色不一致,已返工)。查找端有小写兜底,
  但键格式仍应统一。
- `wavu_{char}.txt` 只保存指令和发生帧,**不会保存投技挣脱键**。方向/挣脱必须从
  Wavu 招式卡片的 notes 核对(`Throw break 1/2/1+2`、`Unbreakable`),不能从
  按键外观猜;通用正面投通常为 `1或2`,但角色指令投必须逐条确认。
- 说明卡片(含 "Input…Startup…" 长文)和超长行要过滤(`len<60`)。

## 3. 帧匹配约定(candidates/lookup)

- **发生帧 = 首击冲击帧**:连段串在第一个按键后的逗号处截断再查
  (`d/f+2,3` 查 `df+2` 的 i14)。架势派生行(`龙构中 f+1`)查派生招自身
  (`DSS.f+1`),其接续帧(带前导逗号的 `,i22`)取首 token 显示。
- **空值穿透**:候选命中但值为空时必须继续尝试后续候选(found_empty 模式),
  全部为空/未命中才显示 `—`。
  ▸ 事故:洛「空翻虚招 u/b+3,4」首击截断得 `ub+3`(空,移动技)即返回 —,
  其实完整串 `ub+3,4|i15` 有值。
- 改空值穿透后必须审计**所有**渲染行,不能只修最初报告的招式。洛的同一次修复
  还让 `1+2+3+4,1+2*,2` 从空的蓄气前缀继续命中完整串 `i14`;因此最终真 `—`
  从预估 10 处变成 9 处。回归测试应逐行比较 `lookup()` 结果,并分别锁定
  `有帧 / 候选全空 / 完全未命中` 三种返回语义。
- 兜底链(按序):`ws+1+2↔ws1+2`、`f,F+ → f+`、`FC.↔hFC.`、首字母大写方向
  转小写(`B+1→b+1`)、`,n,` 剥离、`H.` 前缀剥离(热能强化串首击=原型串首击)。
- **中文条件词后截断**:`qcf+1 命中时 F` 匹配时只取 `qcf+1`。
- **序列前缀映射技巧**:找不到独立条目的架势,可把前缀映射成按键序列——
  卍旋踢中→`db+3,3,3,3,3,`、刈足中→`db+4,`、精准闪避成功后→`b+3,P,`、
  热能+凤凰中→`H.PHX.`(中文词间的 `+` 先删)。
- **当身/防反/架势进入/挑衅显示 `—` 是正确行为**;方向列为「防反」的行直接跳过
  匹配。迎击强化型映射 `CH.` 前缀(刹那驱中迎击时→`CH.SET.`)。
- 跑完必看 MISS 清单:真缺(当身/架势)放行,可修的(前缀缺映射、写法偏差)
  逐条处理。名字对得上才算修对——去 Wavu 卡片核 `movedata-name`
  (刈足·白露 ↔ "Kariashi Hakuro")。

## 4. 布局与渲染陷阱

- **inline-flex 基线陷阱**:`.tk-in` 的基线取决于首个子元素(方阵=首格数字
  基线,箭头=盒底边),同表混排会产生 ±2px 行高漂移,双栏累计错位。
  已在管线 CSS 固化:`td.cmd .tk-in{…;vertical-align:middle}`,别删。
- **双栏区(cols2 / 2列 lt)行高必须统一**,否则左右错位。数据行基准 38px;
  某区块需要更大行距时(如洛的龙构区 48px)**必须整区统一**,不能只有个别行高。
- 主出招表应沿用基准角色的**两张独立表格**并均分数据行。不要为强制同步行高改成
  单张 10 列表:洛曾因此让长指令跨过中线,并因 `min-width` 产生横向滚动。可靠做法是
  去掉表内方向分组标题、左右均分、固定同一行高、指令 `nowrap`,中间保留明确 gap。
- 折行是错位主因:长括号注记移出指令列、或减列宽压力;攻略页(tipsPage)的
  说明列允许折行(左右无需 1:1 对齐)。
- 固定行高不代表没有横向溢出。长伤害串(洛「天翔龙」
  `24,4,5,5,5,7 (50)`)曾侵入判定列;窄 `lt` 需要给伤害列足够宽度,并用文本边界
  与下一格起点做几何检查,不能只断言 CSS 里存在 `height:38px`。
- **回退格必须是裸文本**,不要包 `<span class="tk-in"><span class="tk-txt">`
  ——包裹后 gfx 模式字号变小、行高塌陷(升龙炮事故的另一半根因)。
  标签类起手格(「BnB 替代」「低段格挡 T!」)保持裸文本。
- 3+ 列的架势 lt 一律重排 2×2;奇数格最后一格独占整行。
- **先按 Wavu section 分区,再判断行属性**:属于架势 section 的招式(包括该架势
  内的投技)必须留在对应架势表;只有字面投技 section 才进入页首投技表。先按
  `is_throw` 抽行会破坏来源语义,并让架势攻略与招式脱节。
- Wavu 十连技常用同一串的渐进前缀逐行记录。页面只显示最长叶节点,避免重复九行,
  但生成 HTML 必须用 `data-covered-record-ids` 保留所有源记录覆盖,测试按覆盖 ID
  而不是可见行数做完整性断言。
- 主题合并结构:夜间覆盖块整体前缀 `html.dark`,`--tk-acc` 用页面自己的
  `--acc` 色;浅色走组件 `.light` 变量(墨色、关辉光)。

## 5. 校验清单(每个角色收尾必跑)

1. **行高探针**(headless `--dump-dom --virtual-time-budget=3000` + 注入):
   ```js
   // 每个 .cols2 与 movelist lt 的数据行高集合应各自只有一个值
   document.querySelectorAll('.cols2').forEach(c =>
     c.querySelectorAll(':scope > table').forEach(t =>
       console.log([...new Set([...t.querySelectorAll('tr')].slice(1)
         .map(r => Math.round(r.getBoundingClientRect().height)))])));
   ```
   页面有 `body{zoom:1.25}`,所以 38px CSS 行高在 `getBoundingClientRect()` 中是
   47.5px;应比较同区行高集合和缩放后的预期值,不要硬断言 DOM 高度为 38。
2. `<td class="fr">—</td>` 清点:剩余应全部能说出"为什么是 —"。
3. 杂散字母审计:`<span class="tk-txt">[^<]*[A-Za-z]` 的命中逐个确认是
   有意保留(字面括号/徽标/标签格)。
4. 截图矩阵:夜间/浅色 × 按键图/无数字/文字(切换用注入 click 的副本验证)。
   每种状态同时断言:容器/表格 `scrollWidth === clientWidth`,单元格内容边界不越过
   下一列起点,左右表实际 gap 大于 0。截图肉眼正常不等于没有 1~10px 重叠。
5. 幂等:重跑 `pipeline.py {char}` 应输出 already processed。

## 6. 审计自身的坑

- **正则要锚定整格**,子串会误伤:按 `空翻虚招` 搜会先撞上
  `左右拳转空翻虚招`,得出"帧错了"的假结论。用
  `<td class="name">空翻虚招</td>` 级别的锚点。
- 同名招式也会重复(洛有两个「云门」)。测试不能用跨行 `.*?` 从第一个名字一直吃到
  第二个指令;先按 `<tr>.*?</tr>` 切行,再同时匹配精确招式名和 `cmd-txt`。
- 当前管线是**一遍式转换器**:检测到 `tk-notation` 就直接跳过,不会从干净源重建已
  签入页面。对处理后 HTML 的手工修复必须有结构/数据回归测试;更理想的是保留未处理
  源 HTML,或把后处理写成可重复 transform,否则 `already processed` 只证明文件没变,
  不证明产物可再生。
- 连招页的占位内容不一定含 `here`;`Combo when ...`、`Combo Off-axis ...` 也会伪装成
  路线。结构化抓取后应过滤任何以 `Combo` 开头的 route,并在页面上明确显示实际
  保留下来的来源路线数量;没有有效路线时宁可显示来源缺失说明,也不要补写打法。
- 连招 section 名可能非连续重复。渲染时可以重复标题,但不能按标题全局归并，否则会
  把后段路线提前；DOM 测试应逐行对比快照中的起手与路线顺序。
- Wavu 的 `<sup>` 注记必须在结构化快照里保留词边界，例如 `f,n,df+2 (HARD)`、
  `df+2 (on lower hit)`。禁止把注记直接粘到指令末尾，并用负例 validator 锁定。
- 几何探针计算可见内容边界时必须排除 `.sr-only` 和 `aria-hidden` 节点；裁剪后的无障碍
  文本仍可能扩张 `Range.getBoundingClientRect()`,造成并不存在的跨格假阳性。
- Season 2 四角色以 `tools/source/` 的三份 JSON 快照为输入,由
  `tools/build_season2.py` 完整重建。修改后用 `pwsh -File tools\validate_season2.ps1`
  单一入口验证源记录 ID 覆盖、明确的 section→页面分区、DOM 结构、
  第二次构建字节不变,以及桌面/响应式共 40 状态的浏览器几何门禁;
  这比对生成后 HTML 做手工补丁更可审计。
- `<title>` 探针输出前先想编码;PowerShell 管道中文一律
  `sys.stdout.reconfigure(encoding='utf-8')`。
- 脚本被 import 时不要包 stdout(TextIOWrapper 被 GC 会关掉底层流,
  guard 在 `if __name__ == "__main__"` 里)。

## 7. 批量制作 36 角色的教训(2026-07 全员补齐)

### 抓取管线(取代 §2 的单页手工流程)

- 同源批量:任一 wavu 页过 Anubis 后,同源 `fetch('/t/X_movelist')` +
  `DOMParser` 可抓任意页,无需逐页导航。每角色 2 次 fetch,间隔 ≥1.2s。
- 数据出口只有剪贴板可靠:localhost POST 被 Chrome 本地网络访问策略拦,
  第二次自动下载被多文件下载权限拦;注入按钮 + computer 工具真实点击 →
  `navigator.clipboard.writeText`(有用户激活)→ `Get-Clipboard` 落盘。
- **不要导航工作标签页**——window 上的提取器和已抓数据会全部丢失;每批抓完立即落盘。
- 提取器存档:scratchpad `tk8_injector.js`(会话目录,重要更新同步进去)。
- **wavu 3+ 段派生卡的 lead 本身就是黏连的**(`1210`=12,10,DOM 无分隔):
  damage/target 必须由父链重建(displayed_input 以 `,` 开头 → 父指令 =
  command 去掉尾段;逐级累加)。两位数黏连不会触发三位数报警,是隐性错误。
- section = 最近的 **h2 或 h3**(投技子分区 Regular/Command/Ground/Air Throws、
  DMD 等是 h3)。
- 十连技标题有 `10 Strings`/`10 strings`/`10 String`/`10 Hit Combo` 四种,
  partition 与提取都要同时匹配 "10 string" 和 "10 hit"。
- 部分页面十连技是 wikitable 而非渐进卡片:按 anna 形态合成渐进记录
  (逐击累计 damage/target,叶节点命名 "10 Hit Combo")。
- 空 id 卡(`Paul-`)与 `Generic-` 前缀卡是版面杂物:command 取 id 去前缀,
  空 command 的卡直接剔除。
- 连招页 textOf 必须剥 `https?://\S+`(视频 demo 链接会把裸 URL 混进路线文本,
  600px 不可断 literal 撑爆窄屏)。
- 同 id 多卡允许 name 不同(`1st Hit`/`(2)`/蓄力档);快照统一为首个非编号名,
  测试锁 name/command 每 id 唯一。

### 记法归一化(build_season2.expand_command)

- wavu 原文有 `ss2`(小写无点)、`BT3`/`BT+1`、`CD+1+2`、`,n,`/`,n+4` 小写回中、
  `d+1*(6)` 蓄力档、`df#2` just-frame、`b+1:ORB.1+2` 冒号接架势、
  `P.2`/`P:b+2` 防反追打——全部在 expand_command 归一化,图形化不丢按键图。
- id 级怪癖(`UT,2,1,2,1` 逗号前缀、`Back_Throw_1+3`、`FUFL/FUFR.`、
  `${justFrame}` 模板残留)登记 `COMMON_COMMAND_ALIASES`(只影响图形,
  cmd-txt 恒为原文)。
- King 连环投阶段码(AB1/MMD1-6/RAS/RSSB/SHH)、Steve TFA 等都要进 stance_names。

### 连招区渲染(2026-07 二轮 QC,combo-literal 572→~190 种)

- **句中架势过渡**:`~RFS.3`/`df+2~DCK~db`/`,ORB1:2`/`>LFS.4` 在 expand_command
  统一映射(stance_names + COMMON_PREFIXES;支持 `~`/`,`/`>` 后带点、裸码、
  裸码接数字三形态);`<`/`>` 在 normalize_combo_token 归一成逗号;括号和
  `[]` 一样保护空白,`(H.b+2)` 类指令组内部图形化并保留括号。
- **combo 键名别名** `COMBO_STANCE_ALIASES`(steve PKB→窥视架、eddy MD→曼丁加、
  alisa OG→OTG),只在 render_combos 合并,不进 zh json;heihachi WKG 存疑未映射。
- **parse_cmd 允许纯胶囊渲染**(无按键但有状态胶囊即可出图):孤立架势名
  (SNK/KNP/H.WRA/BOK.n)、`XXX.P` 防反行靠这个出胶囊;纯文字仍回退。
- **徽章**:token 级 `T!`/`W!`/`CH`/`!W`/`WS!`/`HWB!` 等(大小写归一)渲染
  tk-tbang;括号注释内的徽章保持文字。攻略区说明条自动附本页用到的
  场地/热能标记图例(`COMBO_MARKER_LEGEND` + `combo_marker_note`,
  如 WB!=破墙/弹墙 · WH!=墙壁机关 · HB!=热能爆发 · RA=怒气技)。
- **翻译词典** `COMBO_LITERAL_PHRASES` + `COMBO_CHAR_NAMES`:starter 与
  combo-literal 统一走 translate_combo_literal;**多词规则必须排在单词规则前**
  (chip damage/for damage/heat engager 先于 damage/heat),名字类 `\b` 定界。
  回退扫描:`tools/scan_gfx_fallbacks.py`(主表)、`tools/scan_combo_literals.py`
  (连招,不含别名合并,eddy MD 类属扫描误差)。
- 有意保留:Tromba/cd/FLE.ds/(Tackle_reverse) 主表文字;LKS(nina)/BBP/DLS(leo)/
  CL/HB 未考证缩写保持原文;`[s N]`/`[17; +12a (+1)]` 变体/帧数注记保留。

### 布局新机制

- `tk-cram`/`tk-cram2` 压缩级:按**渲染宽度权重**分档(方阵×1 + 箭头/N×0.5
  + 胶囊×2,实测 11px 基准下 px ≈ 43×weight):cram = 方阵 ≥5 或 weight ≥4.8
  (投技 4.0),cram2 = 方阵 ≥6 或 weight ≥5.8;>6 方阵窄表仍回退文字,
  白名单在测试 `EXPECTED_GFX_FALLBACKS`(bryan 嘲讽十连 5 行、king MMD6)。
  字号基准:表格指令 11px(对齐小羽页标准),move-table cram 9px / cram2 7.1px,
  throw-table cram 8.3px / cram2 6.4px,十连技表 cram 9.3px / cram2 8.3px
  (十连技表原本豁免压缩,11px 化后最长串会溢出,故补同档规则);
  指令列宽 move-table 37% / throw-table 34%(容 `df+1+3:qcf+2` 类一段内多变体)。
- 固定行高内允许 dmg/rng/fr/name 列换行(`overflow-wrap:anywhere`),
  注意这类规则必须 ≥ `section:not(.tipsPage) tr[data-record-id] td` 的特异性,
  否则被 nowrap 压住(fr 列曾因此失效)。
- 发生帧显示截断 `(` 后的蓄力变体(完整值在 title);十连技表行高可变,
  几何门禁的 uneven 检查已豁免 `.ten-string-table`。
- 连招 token(`.combo-token`)与其内部 `.tk-in` 都要 `flex-wrap:wrap`,
  且 token 须 `min-width:0`(flex 默认 min-width:auto 会阻止收缩,
  超长起手如 jack `db+3,4,3,4,3` 曾因此溢出起手列),防无空格超长路线撑宽画布。
- 投技挣脱注记的变体:`Throw break: 1`(带冒号)、`Throw Break: none`、
  `Throw cannot be broken` 都要识别;确无注记显示 `—`(title 说明),
  不再输出会撑爆列宽的「—（Wavu 未注明）」。

### 门禁与登记

- 每角色三处登记:`season2_config.py`(含 KNOWN_AGGREGATE_DAMAGE/
  KNOWN_BIG_DAMAGE)、`test_season2_pages.py`(CHARACTERS/EXPECTED_PARTITIONS/
  两个 KNOWN 表)、`validate_season2.mjs`(pages)。期望值一律脚本推导
  (分区/可见数/帧覆盖率),不手算。
- `tools/check_zh.py {key}`:翻译契约单点检查(ID 全覆盖、纯中文、
  stance 前缀完备、按键图零回退),子代理翻译的验收入口。
- 浏览器门禁 `$env:CHARACTERS='a,b'` 过滤;全量 360 状态约 4 分钟。
- 倒地方位码标准语义:FUFT=仰面**脚**朝对手、FUFA=仰面头朝对手(T=Feet
  Toward);曾在 armor_king/king 全部译反,已统一修正。
- 大伤害真值白名单:Gigaton Punch 满蓄 199、吉光斩月满蓄 200、
  f,F+1+4,F 60,185(致死判定)——三位数报警的合法例外,必须逐条对 notes 核实。
