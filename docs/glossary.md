# 术语表 / Glossary

本书译名的唯一真源：中文正文（X.zh.md）与英文正文（X.md）的术语对照以此为准。词条列给出 Title Case 与行文小写两种形态，视为同一译名；标题可用 Title Case，行文用小写。表按主题分组；释义标注「各册有异形」的词条，各册译形尚未统一，翻译时以本表所列形为准。练习档名（Tier 1/2/3 系列）各册按本册中文源形自译，不入本表；书名以各册 H1 为准。新术语候选先记入工作笔记，收口时并入本表。

| 中文 | English | 释义 |
|---|---|---|
| 认知锚点 | Cognitive Anchor (cognitive anchor) | 每章开头锚住你已有直觉、并把判断引到本章标准上的那句话。 |
| 直觉锚点 | Intuition Anchor (intuition anchor) | README 大纲里钩住读者直觉的那一行；与认知锚点分立不合并，另有直觉类比，三词三分。 |
| 直觉类比 | Intuitive Analogy (intuitive analogy) | 用类比引入概念的小节；标题形作「Intuitive Analogy: …」，不与两种锚点合并。 |
| 第一性原理 | First Principles (first principles) | 抛开类比与惯例，从不可再拆的前提重新推导结论的拆解法。 |
| 手把手 | Hands-on (hands-on) | 不跳步、逐步推演到你能照做的教学段落。 |
| 证伪 | Falsification (falsification) | 先问「什么证据能推翻它」，再给结论找反例的姿势。 |
| 取证 | Forensics (forensics) | 用可复跑的脚本与留存的证据复原「刚才发生了什么、为什么」。 |
| 质量门禁 | Quality Gate (quality gate) | 交付前必须通过的检查关卡；本书指时效指纹、权威信源、教学完整性三道。 |
| 门禁 | Gate (gate) | 裸用「门禁」（不带「质量」）一律 gate，如「三条最小门禁」= three minimal gates。 |
| 闸门 | Floodgate (floodgate) | 仅用于「门禁不是墙，是闸门」对照句；其余处「闸门」仍译 gate。 |
| 验收 | Acceptance (acceptance) | 按事先写死的可判定标准判定交付是否合格。 |
| 验收门禁 | Acceptance Gate (acceptance gate) | 把「做对了没有」判成通过/不通过的关卡，通过才叫验收。 |
| 验收判据 | Acceptance Criteria (acceptance criteria) | 写死的可判定判据清单，与「验收」配套使用。 |
| 自动放行 | Auto-allow (auto-allow) | 不等人工确认即放行的档位；各册有异形（册 3 评审档位语境作 auto-merge）。 |
| 口径 | Counting Basis (counting basis) | 统计/记账的口径，「口径提示」= counting-basis note；「口径边界」= scope boundary；各册有异形（册 1 提示作 scope note、册 3 作 basis note）。 |
| 档位 | Tier (tier) | 分级档位通称（如 risk tiering 风险分档、review tier 复核档）；练习档名各册自译，不入本表。 |
| 规格 | Spec (spec) | 动手前写死的：做什么、不做什么、怎么算做对。 |
| 幻觉依赖 | Hallucinated Dependency (hallucinated dependency) | 模型写出实际不存在的依赖；四类系统性失效之一。 |
| 模式化复制 | Pattern Completion (pattern completion) | 照语料里的教程级写法复制代码的失效；四类之一。各册有异形（册 3 作 patterned copying）。 |
| 缺失安全属性 | Absence of Requirement (absence of requirement) | 「没写」的属性不报错、也不消失的失效；四类之一。各册有异形（册 3 作 missing security properties）。 |
| 上下文坍缩 | Context Collapse (context collapse) | 前文被挤出注意力后「忘掉」已有约束的失效；四类之一。 |
| 认知债 | Cognitive Debt (cognitive debt) | 与技术债对举：省掉理解与核验欠下的债。 |
| 返工 | Rework (rework) | 因缺陷或偏离重做已有工作所付出的成本。 |
| 返工率 | Rework Rate (rework rate) | 交付中因缺陷或偏离重做的占比；各册有异形（册 2 作 rework ratio）。 |
| 首轮验收率 | First-Pass Acceptance Rate (first-pass acceptance rate) | 首次提交即通过验收的比例，首次出现给缩写 FPA。 |
| 逃逸率 | Escape Rate (escape rate) | 逃过门禁到达用户手里的缺陷占比；册 5 作「缺陷逃逸率」（defect escape rate）。 |
| 变异测试 | Mutation Testing (mutation testing) | 改动代码造出变异体、看测试能否杀死它，以衡量测试有效性。 |
| 幂等 | Idempotency (idempotency) | 同一操作重复执行不产生新副作用；幂等键 = idempotency key。 |
| 盲区 | Blind Spot (blind spot) | 检查与测试都覆盖不到的区域。 |
| 单位经济 | Unit Economics (unit economics) | 单个用户/单笔收入的成本与毛利账，用来判断这门生意是否成立。 |
| 上线包 | Release Package (release package) | 一次发布所需的检查单、记录与产物集合。 |
| 回滚 | Rollback (rollback) | 把系统退回上一个可用状态的机制与演练。 |
| 夹具 | Harness (harness) | 套在生成代码外的固定验证环境，把「凭感觉」变成「可判定」。 |
| 熔断 / 断路器 | Circuit Breaking / Circuit Breaker (circuit breaking / circuit breaker) | 动作=熔断 circuit breaking，器件=断路器 circuit breaker。 |
| 允许清单 | Allowlist (allowlist) | 明确列许的名单，如依赖允许清单 = dependency allowlist；一律用 allowlist，不用 whitelist。 |
| 特性开关 | Feature Flag (feature flag) | 用开关控制功能是否生效，配合灰度与回滚。 |
| 范围蔓延 | Scope Creep (scope creep) | 需求在交付过程中悄悄变大。 |
| 爆炸半径 | Blast Radius (blast radius) | 一次故障或滥用最坏能波及的范围。 |
| 攻击面 | Attack Surface (attack surface) | 可被触碰、滥用的入口总和；与「爆炸半径」成对（册 4 书名）。 |
| 事故 | Incident (incident) | 一律译 incident，不用 accident。 |
| slopsquatting | slopsquatting（原词保留） | 抢注模型幻觉出的依赖名；slop = AI 低质内容，squatting = 抢注，「抢注」= squatting。 |
| 《关得住》 | Contained (contained) | 册 4 书名；全称 Contained: The Attack Surface and Blast Radius of AI Systems，正文短称 *Contained*。 |
| 局部知识图谱 | Local Knowledge Map (local knowledge map) | 一章内概念与出处的最小对照图，教学完整性的检查项之一。 |
| 贯穿案例 | Running Case (running case) | 全书贯穿的同一案例（各册产品不同）；各册有异形（册 3 作 running example）。 |

## 备查

一次性长尾词条，留档备查，不强约束各册收口。

| 中文 | English | 释义 |
|---|---|---|
| 时效指纹 | Freshness Fingerprint (freshness fingerprint) | 质量门禁三道之一：内容是否踩在时效上（版本、日期不过期）。 |
| 权威信源 | Authoritative Sources (authoritative sources) | 质量门禁三道之一：引文是否指向权威出处。 |
| 教学完整性 | Teaching Completeness (teaching completeness) | 质量门禁三道之一：教学材料是否齐、零基础读者是否跟得上。 |
| 可判定性 | Decidability (decidability) | 能在有限步骤内判成通过/不通过的性质（册 2）。 |
| 最小自主性 | Least Agency (least agency) | 册 4 核心概念：自主度只给到刚好够用。 |
| 混淆代理人 | Confused Deputy (confused deputy) | 安全界既有术语：代理凭自身权限替他人行事反被利用（册 4）。 |
| 超发 | Oversell (oversell) | 超出可用量继续承诺（册 3 优惠券案例）；单轮最大超发 = max oversell per round。 |
| 第二现场 | Second Crime Scene (second crime scene) | 取证语境（册 4）；待裁，备选 secondary scene。 |
| 「纪要」 | "Minutes" (the "Minutes" assistant) | 册 5 贯穿案例产品名「会议纪要助手」；待裁，备选 Meeting Minutes Assistant。 |
