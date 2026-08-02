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
  → experiment_plan.json
  → verification_report.json
  → claim_evidence.json
  → paper_state.json
```

`paper-figures-skill` 是独立仓库。写作技能可以生成 `figure-spec.json`，但不直接修改绘图仓库。

## Versioning（版本控制）

所有跨阶段文件都必须包含 `schema_version`、`project_id`、来源 ID、来源 revision 和 `updated_at`。想法机制发生实质变化时递增 `idea_contract.revision`；实验技能发现哈希或 revision 过期时，必须阻止新运行并发出 revision request。

## State index（状态索引）

`research_state.json` 只是索引，不存放完整证据。它记录当前阶段、活动想法、活动实验、论文状态路径和最新 revision。详细日志、指标和运行输出保存在各自实验目录。

## Handoff（交接）

- 写作技能可以提出 `experiment_request.json`，但不得启动实验。
- 实验技能可以提出 `idea_revision_request.json`，但不得直接修改想法契约。
- 写作技能只能把 `verified-scientific` 或明确标注限制的结果写入论文论断。
- 失败、负结果、缺失证据和阻塞项必须保留，不能为了论文故事删除。
