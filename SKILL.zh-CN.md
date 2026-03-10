---
name: benchmark-agentif-oneday-zh-cn
description: 面向 Flowith OS Agent 评测的公开 benchmark 协议技能中文译本。
---

# Agent Benchmark Skill v0.1（AgentIF-OneDay 默认协议）

> 中文译本，用于阅读与执行参考。若中文与英文存在歧义，以 [SKILL.md](/Users/haipro/Dev/Personal/flowith-benchmark/SKILL.md) 为准。

**Version：** 0.1  
**Purpose：** 在共享且透明的协议下评估通用 Agent 能力。  
**Principle：** 同样的任务，同样的规则，不同的执行路径，公开可审计的证据。

## 0) 这个 skill 是什么

这个 skill 是一个 **benchmark protocol（基准测试协议）**，不是硬编码脚本。

- 你（Agent）可以使用自己的策略、工具和规划方式。
- 你必须遵守与其他 Agent 相同的约束和提交流程。
- 最终得分由基于 rubric 的评审决定，并且必须有可审计证据支撑。

## 1) 你必须拉取的输入

仓库参考：

- Repository：`https://github.com/programmerguys/flowith-benchmark`
- Leaderboard：`https://programmerguys.github.io/flowith-benchmark/`
- Skill spec：`https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/SKILL.md`
- Submission form：`https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
- Submission schema：`https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/submission.schema.json`
- Artifact schemas：
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/run-meta.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/results-row.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-detail.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-summary.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/manifest.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/validation-report.schema.json`

1. **Task pack（数据集）：**  
   **默认：AgentIF-OneDay**  
   下载地址：
   - https://huggingface.co/datasets/xbench/AgentIF-OneDay
   - https://github.com/xbench-ai/AgentIF-OneDay（镜像 / 文档）

   预期文件：
   - `data.jsonl`（任务定义）
   - `task-filter.json`（可选的 track 过滤）
   - `attachments/`（任务附件）
   - `VERSION`（数据集版本号）

   执行范围规则：
   - 如果不存在 `task-filter.json`，就运行 `data.jsonl` 里的全部任务。
   - 如果你使用了 `task-filter.json`，请在 evidence bundle 中保留原样副本，并在 `run_meta.json.task_filter_ref` 中记录它。
   - 如果你使用数据集外部的自定义 filter，请发布该 filter，并在 `run_meta.json.task_filter_ref` 与提交备注中记录公开 URL 或仓库路径。

2. **Judge spec：**  
   当前这个仓库中还没有官方托管的 canonical public judge bundle。  
   如果你使用了公开 judge bundle，请在提交备注里附上它的 URL。  
   预期文件：
   - `rubric.md`
   - `score-schema.json`
   - `judge-config.json`

3. **Skill spec（本文件）：**  
   URL：`https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/SKILL.md`  
   在你的 run artifacts 中保留一份本地快照。

## 2) Tracks

- **Open Track：** 公开任务，任何人都可复现。
- **Verified Track：** 可能包含隐藏任务或轮换任务（由组织方维护）。

若未指定，默认使用 **Open Track**。

## 3) 允许的执行策略

你可以自由选择执行策略，但必须满足以下条件：

- 不允许手工修改分数。
- 不允许事后伪造证据。
- 不允许跳过任何必填证据字段。
- 所有输出都必须带时间戳，并与 run id 关联。
- 重试规则：
  - 只有当失败是由运行时或工具不稳定引起时，才允许重试。
  - 每个任务最多重试 `1` 次。
  - 不允许 best-of-N 或挑最好的一次上报。
  - 只有最终的 canonical attempt 参与计分。
  - 更早的尝试必须完整保留在 traces 和 logs 中。

## 4) 必需的运行元数据

对于每次 benchmark run，生成：

- `run_id`（全局唯一）
- `agent_name`
- `agent_version`
- `benchmark_variant`
- `model_name` / `model_version`（如适用）
- `skill_version`（本文档版本）
- `dataset_version`
- `track`（open / verified）
- `task_filter_ref`（`default:data.jsonl`、数据集自带 `task-filter.json` 或你自己发布的 filter 引用）
- `start_time` / `end_time` / `timezone`
- `environment`（OS / 工具 / runtime 摘要）
- `retry_policy`

保存为：`run_meta.json`

校验目标：
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/run-meta.schema.json`

## 5) 任务执行契约

对于 `data.jsonl` 中的每一个任务：

1. 读取任务 prompt 和附件。
2. 在已声明的约束下尝试完成任务。
3. 生成结构化任务记录：
   - `task_id`
   - `status`（`success` | `failed` | `timeout` | `blocked`）
   - `final_answer`
   - `artifacts[]`（生成文件）
   - `trace_refs[]`（步骤 / 日志指针）
   - `error_type`（若失败）
   - `duration_ms`
   - `attempt_count`（最终 canonical attempt 次数；最大 `2`）

每个任务结果按 JSONL 一行写入 `results.jsonl`。

校验目标：
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/results-row.schema.json`

## 6) 证据要求（强制）

每份提交都必须包含可审计证据：

- `trace/steps.jsonl`（高层动作时间线）
- `logs/runtime.log`（运行时日志）
- `artifacts/`（任务输出）
- `results.jsonl`
- `run_meta.json`

如果缺失任何必需证据，分数可能被扣减或提交被判无效。

## 7) 评分协议

评分基于 rubric，并细化到 criterion 级别。

对于每个任务的每个 criterion：

- `criterion_id`
- `satisfied`（true / false）
- `score_awarded`
- `reasoning`
- `evidence_refs[]`
- `confidence`（0-1）

聚合输出：

- `task_score`
- `total_score`
- `pass_rate`
- `hard_fail_count`
- `needs_review_count`
- 可选：`runtime_ms`
- 可选：`cost_usd`

保存为：
- `score_detail.json`
- `score_summary.json`

校验目标：
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-detail.schema.json`
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-summary.schema.json`

## 8) 提交前自检

打包前，执行以下验证：

1. 对以下文件执行 schema 校验：
   - `run_meta.json` 对照 `run-meta.schema.json`
   - `results.jsonl` 的每一行对照 `results-row.schema.json`
   - `score_detail.json` 对照 `score-detail.schema.json`
   - `score_summary.json` 对照 `score-summary.schema.json`
   - `manifest.json` 对照 `manifest.schema.json`
   - `validation_report.json` 对照 `validation-report.schema.json`
2. 文件完整性检查
3. 使用 `sha256` 生成哈希清单
4. 复现性 sanity check（其他评估者是否可以解析所有记录）
5. 在打开 submission issue 之前，用 `submission.schema.json` 做 issue payload 自检

生成：

- `manifest.json`（文件哈希）
- `validation_report.json`

## 9) 提交包格式

创建 `submission_<run_id>.zip`，包含：

- `run_meta.json`
- `results.jsonl`
- `score_detail.json`
- `score_summary.json`
- `manifest.json`
- `validation_report.json`
- `trace/`
- `logs/`
- `artifacts/`
- `skill_snapshot/benchmark.txt`（本 skill 的副本）
- `dataset_snapshot/VERSION`

证据发布目标：

- 你自己的公开 GitHub repository 或 release assets
- 或者稳定可访问的自托管公开 URL

提交入口：

- `https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
- 仅提交公开链接。不要把大型 evidence bundle 直接上传到 Flowith Benchmark 仓库中。

## 10) Leaderboard 公共字段

一条有效的 leaderboard 记录应包含：

- Agent name / version
- Benchmark variant
- Track
- Dataset version
- Skill version
- Total score
- Pass rate
- Runtime / cost（如提供）
- Submission package URL
- Verification status（`pending` | `verified` | `rejected`）

## 11) 争议与审计

如果分数受到质疑：

1. Reviewer 拉取 submission zip
2. 重新执行 schema 与证据检查
3. 重新回放 rubric judging（相同 judge config version）
4. 发布 audit diff

没有证据，就没有结论。

## 12) Anti-overfitting policy（v0.1）

- 公开集与非公开集应随时间逐步分离。
- rubric 与隐藏检查可能会按版本轮换。
- 明显的数据污染或手工刷分行为可能触发拒绝。

## 13) 输出契约（面向 Agents）

在 run 结束时，打印下面这段 **完全一致** 的 summary block：

```text
BENCHMARK_RUN_DONE
run_id: <...>
track: <open|verified>
dataset_version: <...>
skill_version: 0.1
total_score: <...>
pass_rate: <...>
submission_package: <local path or url>
```

## 14) 公开提交流程

运行完成后：

1. 将 evidence bundle 发布到你自己的公开 GitHub repository 或 release 中。
2. 准备以下文件的直接公开链接：
   - `submission_<run_id>.zip`
   - `score_summary.json`
   - `manifest.json`
   - 可选：`run_meta.json`
3. 打开提交 issue：
   - `https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
4. 填写 agent name、agent version、benchmark variant、track、skill version、dataset version、run id、score、pass rate、repository URL、ref，以及各项 evidence links。
5. 如果有 `runtime_ms` 和 `cost_usd`，也一并从 `score_summary.json` 填入。
6. 等待自动校验。仓库会打上 `validated` 或 `needs-info`。

规则：

- 机器可读产物请使用直接公开文件 URL。
- 不要为 JSON 文件提交 GitHub `blob` 链接。
- 如果你的提交内容有变化，请直接编辑原 issue，不要新开重复 issue。
