# Post-training 推理链路与资源归因：一手证据底稿

核验日：2026-09-26。范围：语言模型的 SFT、偏好优化、在线强化学习及多轮 agent 训练；本页只记录公开论文、平台一手文档和由其推出的条件判断。来源状态按仓库 `.agents/PUBLIC-SOURCE-POLICY.md`。`PUBLIC_PAGE_VALIDATE` 表示本次实际打开、但动态文档可能随后变动。所有文档均在核验日无需登录即可读取；没有公开数据的数字标 `SOURCE_UNAVAILABLE`。

## 先给结论

1. **post-training 不是单一工作负载。** SFT 对固定答案做监督梯度更新；DPO 对离线偏好对做优化，原论文明确指出训练时无需从当前模型持续采样；在线 RL/RFT 才有反复「生成候选 → 验证/评分 → 更新权重」的循环。DeepSeek-R1 公开了 SFT、两阶段 RL、拒绝采样与蒸馏的组合，证明同一模型项目也可跨这些路径。[S01][S02][S03][S04]
2. **在线 RL 的模型生成和权重更新通常占用 GPU/TPU 等加速器；CPU 主要承担控制面与环境面。** Hugging Face TRL 明确把生成列为在线训练的常见瓶颈，并支持 vLLM 与训练 GPU 共置或使用独立 GPU。NVIDIA NeMo Gym 的一个实现将 agent/工具/环境及验证器放在 CPU-only 服务，将 vLLM 推理留在 GPU 服务。这里说的是公开实现的资源分工，不是任何厂商通用的 CPU:GPU 配比。[S05][S06]
3. **CPU 增量取决于被训练的任务。** 数学答案匹配与格式检查可很轻；运行生成代码、测试、编译、数据库、浏览器或多轮工具链可消耗较多 CPU、内存、沙箱和文件句柄；用另一模型评分又把部分负载移回加速器。NVIDIA 文档特别要求给执行类验证器设置并发、超时和进程限制。[S05][S07]
4. **公开商业证据支持「已有产品化」，尚不支持「市场规模／INTC 份额已知」。** AWS 在 2026-02 公布 Nova RFT 的 Bedrock、SageMaker、HyperPod 和 Nova Forge 路径；Google 2026-09-15 公布 Gemini RL fine-tuning 控制台预览；但 OpenAI 同年收紧并计划结束其自助 fine-tuning 新训练。三者并存，不能把产品发布数换算为训练量、CPU 采购量或 Intel 收入。[S09][S10][S11]

## 1. 分清训练方法与推理活动

| 路径 | 训练时的输入及循环 | 资源归因 | 边界 |
|---|---|---|---|
| SFT | 固定 `(prompt, completion)`，对目标 token 计算交叉熵并更新模型。 | 模型前向/反向主要在加速器；CPU 用于数据读取、预处理、tokenization、作业管理；数据与 checkpoint 需要存储。 | 数据可能由此前的教师模型推理产生，但**该生成不是 SFT 梯度步骤的必需在线环节**。[S01] |
| DPO／离线偏好优化 | 固定 `prompt, chosen, rejected` 对，比较偏好与拒绝输出的相对概率并训练。 | 加速器用于模型训练与可能的参考模型计算；CPU/存储承担偏好数据、作业管理。 | 原始 DPO 方法训练时不要求在线 rollout；此前收集偏好对可能已消耗生成算力，需单列。[S02][S04] |
| 在线 RL／RLVR／RFT | 每步对 prompt 采多个候选；验证或奖励模型打分；估计优势／损失；训练策略并把新权重同步到生成端。 | 生成推理和训练是两个加速器工作池，可共置也可分开；验证器和环境可能使用 CPU，也可能调用另一个模型；跨池权重与样本流需要网络。[S05][S06][S08] | 算法和部署可异步化，不能把「rollout 使用 GPU」理解成只有训练 GPU 或全程 CPU。 |
| 多轮 agent RL | 模型和环境交替多次；每轮可能执行工具并产生状态、轨迹与最终奖励。 | 模型调用在加速器；agent 服务、状态、工具、沙箱、验证器用 CPU／存储，若 LLM judge 则再用加速器。[S06][S07] | 任务难度、每回合工具数、环境隔离及评测方法决定 CPU 负载；没有统一每 GPU CPU 核数。 |

OpenAI 2024 年 o1 发布材料展示：强化学习训练与测试时更长思考、更多候选采样均可提高某些任务成绩；其 AIME 多样本／重排实验是**测试时扩展**，不能当作训练集群 CPU 配置或客户需求数据。DeepSeek-R1 论文的「从 RL checkpoint 拒绝采样成新的 SFT 数据、再蒸馏小模型」说明教师推理会增加生成负载，但不自动增加执行类 CPU 验证器。[S03][S12]

## 2. 一个可核验的在线 RL 工作流

```text
prompt/任务数据 → 生成端模型采样多个答案或多轮轨迹（加速器，权重/KV cache 在显存）
             → 环境/工具/验证器产出 reward（CPU 规则/执行沙箱，或加速器上的 judge）
             → 轨迹、logprob、reward 入队/存储（内存、磁盘/对象存储、网络）
             → 策略训练更新（加速器，optimizer/activation/checkpoint）
             → 新权重传回生成端（互连/网络），下一批 rollout
```

这不是自行发明的通用软件拓扑：TRL 文档写明 vLLM 可以与 trainer 共用 GPU 或用独立 GPU；NeMo Gym 文档写明 CPU-only 环境通过 HTTP 请求 vLLM；ECHO-2 论文把分布式 RL 拆成 rollout、学习和数据三个平面，并讨论权重传播与广域网通信。[S05][S06][S08] 但三者仅证明这些实现**可行且被维护／研究**，不证明所有大模型厂商都按此部署。

### 资源类型及一手证据

| 资源 | 已知负载 | 对 CPU 行业判断的意义 |
|---|---|---|
| 加速器算力与 HBM | 生成 rollout、策略梯度更新、模型 judge；模型权重与随生成长度增长的 KV cache 占显存。vLLM 原论文研究了 KV cache 对并发吞吐的限制。[S05][S13] | post-training 扩张首先仍是加速器容量、显存与利用率命题。不能用 CPU 需求替代这部分。 |
| 主机 CPU 与内存 | 调度、数据准备、HTTP agent 服务、任务状态与日志；执行类验证器可能需要进程、沙箱、数据库或编译器。NeMo Gym 的 CPU-only 环境是清楚的实例。[S06][S07] | CPU 可能成为瓶颈，但要看任务构成和资源配额；纯规则打分的每条轨迹 CPU 成本可能很低。 |
| 持久存储 | 数据集、完整轨迹、评测结果与模型 checkpoint。Google RLFT 文档要求 JSONL 数据集置于 Cloud Storage，并支持中间 checkpoint；AWS Bedrock 使用上传的训练数据。[S14][S17] | 存储消耗与轨迹保留政策、checkpoint 周期有关，不能直接归给 CPU 收入。 |
| 网络／互连 | 分离的训练与生成集群之间传权重，agent 与模型／环境间调用，轨迹回传。ECHO-2 的分布式设计与 NeMo RL 权重同步说明这些通路是实际系统问题。[S08][S15] | 网络容量也可能限制扩张；更多 CPU 机器不一定解决生成端等待或权重同步。 |

有研究把 GPU 训练集群和 CPU 基准测试集群连接，直接以生成代码在真机运行的速度作奖励；这是「某些高强度验证任务可形成独立 CPU 集群」的**个案证明**，不是典型 RL 作业配比。[S16]

## 3. 市场采用、可观测指标和缺口

| 证据层 | 当前公开可证 | 不可推出 |
|---|---|---|
| 技术存在 | o1、DeepSeek-R1 公开说明强化学习推理模型训练；DPO、TRL、NeMo RL/Gym 和 ECHO-2 提供论文或可复核实现。[S02][S03][S05][S06][S08][S12] | 全行业采用同一种算法、流程或硬件拓扑。 |
| 产品化 | AWS Nova RFT 可配置任务及 Lambda 奖励；Google Gemini RLFT 在控制台为 Preview，文档标 Pre-GA。[S09][S10][S14] | 产品已经广泛付费使用；谷歌预览版达到正式 GA。 |
| 逆向信号 | OpenAI 官方 2026-05/07 通知停止新组织的自助 fine-tuning，2026-07-02 对不活跃组织进一步收紧，计划 2027-01-06 停止现有活跃客户创建新作业。[S11] | OpenAI 停止内部 post-training 研发，或整个行业需求下降。公开资料只说明这一自助产品的生命周期。 |
| 数量规模 | AWS 文档写明 Bedrock Nova RFT 的训练数据最多 2 万 prompts，这是**产品限制**。[S14] | 实际并发作业数、CPU 核小时、GPU 小时、客户支出、CPU:GPU 实际配比。以上均为 `SOURCE_UNAVAILABLE`。 |

### 可执行的容量归因模型（`MODEL_DERIVED`，不是市场统计）

要把技术机制转成 CPU 需求，先对某一种训练任务实测：`rollout/s`、平均生成 token、每条轨迹工具调用次数、执行验证器 CPU 秒、内存峰值、并发沙箱数、GPU 利用率、网络等待、轨迹保留字节与 checkpoint 周期。对一组同质任务，可用 `CPU 核需求 ≈ rollout/s × 每条轨迹的 CPU 秒 ÷ 目标利用率` 做一阶容量估算；多轮工具或模型 judge 分开计。再从云服务实例规格、CPU 型号与采购披露推供应商份额。当前公开来源没有满足这些参数的生产工作负载分布，也没有将其映射到 INTC Xeon 订单的披露，故**全球 GPU:CPU 比、post-training CPU TAM 和 INTC 受益金额均为 `SOURCE_UNAVAILABLE`**。

对 INTC 的正确传导链是：在线 RL 使用场景增长 → 任务中 CPU 环境/验证器占比与核心小时增长 → 客户采购服务器 CPU → Xeon 或竞争方案的份额、ASP 与毛利 → Intel 分部收入和现金回报。每个箭头要独立验证。Google 还展示了基于 TPU 的 RL 路线；post-training 机制本身不指定 Intel CPU。[S18]

## 4. Source records（一手、实际打开）

以下 `n.d.` 表示页面未标稳定发表日；动态文档按核验日快照使用。论文为研究结果而非第三方商业审计。

| ID | URL／文档标题 | 发布／更新 | 核验日／状态 | 对应位置与限制 |
|---|---|---|---|---|
| S01 | [Hugging Face TRL — SFT Trainer](https://huggingface.co/docs/trl/sft_trainer) | n.d. | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | “Looking deeper into the SFT method”；固定监督样本、token loss。动态文档。 |
| S02 | [Rafailov et al. — Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) | 2023-05-29 | 2026-09-26 `PUBLIC_NO_AUTH` | 摘要和 §1；原始 DPO 在优化阶段不需要在线模型采样。 |
| S03 | [DeepSeek AI — DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) | 2025-01-22 | 2026-09-26 `PUBLIC_NO_AUTH` | 摘要、§1.1、§2；两段 RL、冷启动、拒绝采样和蒸馏。没有可外推到行业的 CPU:GPU 数据。 |
| S04 | [Hugging Face TRL — DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer) | n.d. | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | preference dataset 格式及 reference model 参数；实现文档，不是采用量统计。 |
| S05 | [Hugging Face TRL — GRPO Trainer](https://huggingface.co/docs/trl/grpo_trainer) | n.d. | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | “Speed up training with vLLM-powered generation” 和 “Agent Training”；共置／独立 GPU、工具与状态环境。动态文档。 |
| S06 | [NVIDIA NeMo RL — NeMo Gym Integration](https://docs.nvidia.com/nemo/rl/nightly/design-docs/nemo-gym-integration.html) | n.d.，nightly | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | Overview；Gym CPU-only、vLLM HTTP、GRPO／on-policy distillation。是 NVIDIA 实现，不是行业平均。 |
| S07 | [NVIDIA NeMo Gym — Execution and State Match](https://docs.nvidia.com/nemo/gym/build-verifiers/verification-patterns/execution-and-state-match/) | n.d. | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | “Code Execution Against Tests” “Concurrency, Timeouts, and Cleanup”；执行验证与 CPU／进程上限。 |
| S08 | [Song et al. — ECHO-2: A Large-Scale Distributed Rollout Framework for Cost-Efficient Reinforcement Learning](https://arxiv.org/abs/2602.02192) | 2026-02-02，v5 2026-05-26 | 2026-09-26 `PUBLIC_NO_AUTH` | 摘要、§4；分布式 rollout／学习／数据平面。研究系统，不是生产市场份额。 |
| S09 | [AWS — Reinforcement fine-tuning for Amazon Nova: Teaching AI through feedback](https://aws.amazon.com/blogs/machine-learning/reinforcement-fine-tuning-for-amazon-nova-teaching-ai-through-feedback/) | 2026-02-26 | 2026-09-26 `PUBLIC_NO_AUTH` | “Implementation tiers”；AWS 自述已提供的产品路径，未披露采用量。 |
| S10 | [Google Cloud — Gemini Enterprise Agent Platform release notes](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes) | 2026-09-15 项 | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | “Reinforcement learning fine-tuning in the Google Cloud console (Preview)”；预览而非 GA。 |
| S11 | [OpenAI API — Deprecations](https://developers.openai.com/api/docs/deprecations) | 2026-05-07 通知、2026-07-02 限制节点 | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | “Update to OpenAI’s self-serve fine-tuning”；只限自助 fine-tuning 产品，不代表内部训练。 |
| S12 | [OpenAI — Learning to reason with LLMs](https://openai.com/index/learning-to-reason-with-llms/) | 2024-09-12 | 2026-09-26 `PUBLIC_NO_AUTH` | Evals、Chain of Thought、Coding；训练时 RL 与测试时采样需区分。 |
| S13 | [Kwon et al. — Efficient Memory Management for Large Language Model Serving with PagedAttention](https://arxiv.org/abs/2309.06180) | 2023-09-12 | 2026-09-26 `PUBLIC_NO_AUTH` | 摘要、§1；模型权重与 KV cache 的 GPU 显存约束。测的是 serving 系统，不是 post-training 全栈。 |
| S14 | [Amazon Bedrock — Fine-tune Amazon Nova models with reinforcement fine-tuning](https://docs.aws.amazon.com/bedrock/latest/userguide/rft-nova-models.html) | n.d. | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | 五步工作流、最多 20K prompts；上限不等于客户实际训练规模。 |
| S15 | [NVIDIA NeMo RL — Weight Refit: Choosing a Transport](https://docs.nvidia.com/nemo/rl/nightly/guides/refit.html) | n.d.，nightly | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | 训练与生成间权重同步：共置 CUDA IPC、分离 NCCL 等。 |
| S16 | [Mikasa et al. — Improving HPC Code Generation Capability of LLMs via Online Reinforcement Learning with Real-Machine Benchmark Rewards](https://arxiv.org/abs/2602.12049) | 2026-02-12 | 2026-09-26 `PUBLIC_NO_AUTH` | 摘要；GPU 训练集群加 CPU 基准测试集群的特定实验。 |
| S17 | [Google Cloud — Reinforcement learning fine-tuning job](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/reinforcement-tuning/reinforcement-tuning-job) | n.d.，Pre-GA | 2026-09-26 `PUBLIC_PAGE_VALIDATE` | 数据集在 Cloud Storage、奖励函数和 checkpoint；文档标预览限制。 |
| S18 | [Google Cloud — Agent Factory Recap: Reinforcement Learning and Fine-Tuning on TPUs](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-reinforcement-learning-and-fine-tuning-on-tpus/) | 2026-01-16 | 2026-09-26 `PUBLIC_NO_AUTH` | “Why TPUs Shine for RL” 与 GRPO 演示；Google 的技术路线，不是所有 RL 训练的硬件选择。 |

Google Cloud [2026-09-25 技术文章](https://cloud.google.com/blog/topics/developers-practitioners/best-practices-guide-for-customizing-gemini-models) 亦已实际打开（`PUBLIC_NO_AUTH`）：其把「多候选生成 → reward → 更新」作为托管 RLFT 的服务流程；文中早期用户用例不是统一采用率，也未披露硬件账单。OpenAI 的 [RFT 指南](https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning) 亦实际打开（`PUBLIC_PAGE_VALIDATE`，n.d.）：它解释同一循环，同时明确其自助 fine-tuning 正在收缩，不能引用旧发布信息单独证明现时增长。
