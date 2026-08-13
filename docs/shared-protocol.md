# Shared Research Protocol

三个技能通过项目根目录下的 `research_state/` 交换结构化事实，不通过隐式上下文或互相修改对方的内部文件。

## Ownership（所有权）

- `research-idea-lab`：文献、问题卡、瓶颈与独到动机、问题—想法谱系、想法池、创新性判断和想法契约。
- `research-experiment-lab`：实验计划、不可变运行、日志、统计和验证报告。
- `ai-research-writing-skill`：论文状态、论断、正文、引用、表格和写作交接。

任何技能只能写自己拥有的目录；跨阶段内容通过请求文件和事件追加表达，不能覆盖另一阶段的状态。

## Canonical flow（标准流转）

探索性验证流：

```text
problem_card.yaml
  → validation-alignment.yaml
  → exploratory-validation experiment_plan.json
  → validation_alignment_check.json
  → immutable run records
  → verified-diagnostic
```

正式论文证据流：

```text
idea_contract.yaml
  → state_consistency.json
  → experiment_plan.json
  → verification_report.json
  → research_handoff.json
  → paper_state.json
```

探索性验证不能直接跳入 `research_handoff.json`。出现有潜力的信号后，先回到想法技能完成严格目标领域新颖性核查和正式契约，再建立正式实验计划。

`paper-figures-skill` 是独立仓库。写作技能可以生成 `figure-spec.json`，但不直接修改绘图仓库。

## Versioning（版本控制）

跨阶段文件必须包含 `schema_version`，并携带其协议规定的来源 ID 和 revision（修订号）。本地交接优先使用稳定 ID、正整数修订号、项目相对路径、时间和 Git 提交，不再强制生成通用 SHA-256（内容哈希）；旧哈希字段可继续读取。远程下载、不可变快照、官方模板包或外部系统明确要求时仍保留加密摘要。`project_id` 与 `updated_at` 只在对应 schema 要求时强制存在。只修复代码、接口、训练或测量时递增实现修订；因果机制发生实质变化时递增想法修订；核心失败解释或解决原理改变时建立有关联的新想法 ID。

## State index（状态索引）

`research_state.json` 只是索引，不存放完整证据。它记录当前阶段、活动想法、活动实验、关键路径和最新 revision。`phase` 允许项目使用更细粒度的非空阶段名。详细日志、指标和运行输出保存在各自目录。

一致性报告的新写入规范名是 `research_state/ideas/state_consistency.json`。读取器暂时兼容旧索引显式引用的 `idea_state_consistency.json`，但不再生成旧名字，也不自动删除旧文件。

## Handoff（交接）

- 写作技能可以提出 `experiment_request.json`，但不得启动实验。
- 实验技能可以提出 `idea_revision_request.json`，但不得直接修改想法契约。
- 新的探索性验证必须引用父问题卡以及用户批准的
  `validation-alignment-v3`；历史 v1/v2 对齐卡仅可读，启动前必须迁移。正式新实验必须引用
  通过的 `research-idea/state-consistency-v2` 报告。契约不是 `active`、想法池
  不再是 `experiment-ready`，或身份与修订过期时禁止正式启动。
- 新的 `research-idea/v4` 正式契约必须使用 `problem-led/v1`；谱系检查会读取
  真实问题卡并核对问题 ID、修订、成熟度、状态、结构和语义。旧契约只读，
  缺失、关闭或过期的问题卡不能进入实验交接。
- 每一轮探索性验证都需要新的用户对齐；在已批准的 100 元、24 小时范围内可以按冻结任务图执行，超出范围重新批准。
- 探索性验证先判断程序是否真的实现并启用了设想机制，再区分实现未确认、测量不明确、机制反证和支持性信号。
- 论文级正式实验必须同时具备机制、定量和定性三类证据义务；定性案例要
  预先声明选择协议并包含失败案例，不能只挑成功样例。
- 共享状态下的写作交接使用 `ai-research-writing/research-handoff-v2`，并核对活动 ID、想法与计划修订、`paper-ready` 阶段、完整方法身份及 v3 验证报告；验证报告中的检查项、三类证据义务、逐项结果和实际文件必须完全对应，不能依赖手填计数。旧哈希存在时可额外核验，但不再是新交接必需字段。

跨技能统一遵循 `research-quality-controls.md`：默认部分确认；判断性风险只警告、不自动写入产物；探索深度与研究阶段分离；各技能读取广泛但只写自己拥有的产物。
- 非共享状态的独立写作项目可继续读取 v1 交接，但不能借此绕过共享状态核验。
- 失败、负结果、缺失证据和阻塞项必须保留，不能为了论文故事删除。
