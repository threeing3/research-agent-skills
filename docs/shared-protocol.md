# Shared Research Protocol

三个技能通过项目根目录下的 `research_state/` 交换结构化事实，不通过隐式上下文或互相修改对方的内部文件。

## Ownership（所有权）

- `research-idea-lab`：文献、想法池、创新性判断、想法契约。
- `research-experiment-lab`：实验计划、不可变运行、日志、统计和验证报告。
- `ai-research-writing-skill`：论文状态、论断、正文、引用、表格和写作交接。

任何技能只能写自己拥有的目录；跨阶段内容通过请求文件和事件追加表达，不能覆盖另一阶段的状态。

## Canonical flow（标准流转）

探索性验证流：

```text
validation-alignment.yaml
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

跨阶段文件必须包含 `schema_version`，并携带其协议规定的来源 ID、revision（修订号）和 SHA-256（内容哈希）。`project_id` 与 `updated_at` 只在对应 schema 要求时强制存在。只修复代码、接口、训练或测量时递增实现修订；因果机制发生实质变化时递增想法修订；核心失败解释或解决原理改变时建立有关联的新想法 ID。实验技能发现哈希、revision 或生命周期过期时，必须阻止新运行并发出 revision request。

## State index（状态索引）

`research_state.json` 只是索引，不存放完整证据。它记录当前阶段、活动想法、活动实验、关键路径和最新 revision。`phase` 允许项目使用更细粒度的非空阶段名。详细日志、指标和运行输出保存在各自目录。

一致性报告的新写入规范名是 `research_state/ideas/state_consistency.json`。读取器暂时兼容旧索引显式引用的 `idea_state_consistency.json`，但不再生成旧名字，也不自动删除旧文件。

## Handoff（交接）

- 写作技能可以提出 `experiment_request.json`，但不得启动实验。
- 实验技能可以提出 `idea_revision_request.json`，但不得直接修改想法契约。
- 探索性验证必须引用用户批准的 `validation-alignment-v1` 及其哈希；正式新实验必须引用通过的 `research-idea/state-consistency-v2` 报告。契约不是 `active`、想法池不再是 `experiment-ready`，或任一哈希过期时禁止正式启动。
- 每一轮探索性验证都需要新的用户对齐；在已批准的 100 元、24 小时范围内可以按冻结任务图执行，超出范围重新批准。
- 探索性验证先判断程序是否真的实现并启用了设想机制，再区分实现未确认、测量不明确、机制反证和支持性信号。
- 共享状态下的写作交接使用 `ai-research-writing/research-handoff-v2`，并核对活动 ID、契约与计划哈希、`paper-ready` 阶段及 v2 验证报告；仅字段存在不算完成交接。
- 非共享状态的独立写作项目可继续读取 v1 交接，但不能借此绕过共享状态核验。
- 失败、负结果、缺失证据和阻塞项必须保留，不能为了论文故事删除。
