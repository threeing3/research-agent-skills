# Shared Research Protocol

三个技能通过项目根目录下的 `research_state/` 交换结构化事实，不通过隐式上下文或互相修改对方的内部文件。

## Ownership（所有权）

- `research-idea-lab`：文献、想法池、创新性判断、想法契约。
- `research-experiment-lab`：实验计划、不可变运行、日志、统计和验证报告。
- `ai-research-writing-skill`：论文状态、论断、正文、引用、表格和写作交接。

任何技能只能写自己拥有的目录；跨阶段内容通过请求文件和事件追加表达，不能覆盖另一阶段的状态。

## Canonical flow（标准流转）

```text
idea_contract.yaml
  → idea_state_consistency.json
  → experiment_plan.json
  → verification_report.json
  → research_handoff.json
  → paper_state.json
```

`paper-figures-skill` 是独立仓库。写作技能可以生成 `figure-spec.json`，但不直接修改绘图仓库。

## Versioning（版本控制）

跨阶段文件必须包含 `schema_version`，并携带其协议规定的来源 ID、revision（修订号）和 SHA-256（内容哈希）。`project_id` 与 `updated_at` 只在对应 schema 要求时强制存在。想法机制发生实质变化时递增 `idea_contract.revision`；实验技能发现哈希、revision 或生命周期过期时，必须阻止新运行并发出 revision request。

## State index（状态索引）

`research_state.json` 只是索引，不存放完整证据。它记录当前阶段、活动想法、活动实验、关键路径和最新 revision。`phase` 允许项目使用更细粒度的非空阶段名。详细日志、指标和运行输出保存在各自目录。

## Handoff（交接）

- 写作技能可以提出 `experiment_request.json`，但不得启动实验。
- 实验技能可以提出 `idea_revision_request.json`，但不得直接修改想法契约。
- 新实验必须引用通过的 `research-idea/state-consistency-v2` 报告；契约不是 `active`、想法池不再是 `experiment-ready`，或任一哈希过期时禁止启动。
- 共享状态下的写作交接使用 `ai-research-writing/research-handoff-v2`，并核对活动 ID、契约与计划哈希、`paper-ready` 阶段及 v2 验证报告；仅字段存在不算完成交接。
- 非共享状态的独立写作项目可继续读取 v1 交接，但不能借此绕过共享状态核验。
- 失败、负结果、缺失证据和阻塞项必须保留，不能为了论文故事删除。
