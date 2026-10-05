# 后训练（post-training）需求：从技术成立到股东收益的推理报告

研究截点：**2026-09-26**。承接 [INTC / CPU 分析](../intc-cpu-analysis-2026-09-26/README.md)，这里研究大模型预训练后的模型改进，尤其是 SFT、偏好优化、强化学习、评测和蒸馏。报告把 Herman Jin 的新命题当作待检验假设，借 Serenity 的已归纳检查方法追问收入与融资；不代表两人共同发表了这份报告。

## 结论

**后训练是已被技术和产品验证的真实计算用途，但“海量、持续、尚不能满足”的市场规模、对每家硬件公司的增量收入，仍缺公开量化证据。** OpenAI 披露推理模型的表现随强化学习训练算力增加而改善；微软将后训练列为其可共用 AI 集群的工作负载；AWS 已推出面向多步 Agent 的付费强化微调；CoreWeave 已推出用于 RL、工具调用和评测的隔离环境。[OpenAI o1 研究公告](https://openai.com/index/learning-to-reason-with-llms/)、[Microsoft FY26Q1 电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q1)、[AWS 2026-06 产品公告](https://aws.amazon.com/about-aws/whats-new/2026/06/multi-turn-reinforcement-learning-on-sagemaker-ai/)、[CoreWeave 2026Q2 公告](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx)

**可投资的判断分三关：** 后训练能否解决真实任务 → 企业是否反复付费且占用净新增算力 → 哪一家供应商在扣除成本与融资后留下每股收益。微软 2026-07 称 Foundry 已有 10 万客户、收入同比翻倍以上，但披露的是整个 Foundry 平台，不能填作后训练收入。[Microsoft FY26Q4 电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4) 对 INTC，更不能从 RL 需要 CPU 进而推出其 Xeon 销售或 14A 外部代工已受益；[Intel 2026Q2 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)没有按后训练披露订单。

## 1. 先画清工作负载

| 阶段 | 做什么 | 主要资源及证据边界 |
|---|---|---|
| SFT / 离线偏好优化（如 DPO） | 用固定示例或偏好对调整权重 | 需要训练计算与数据；原始 DPO 优化阶段不要求持续从当前模型在线采样，前期收集偏好对仍可能需要生成算力。[SFT 说明](https://huggingface.co/docs/trl/sft_trainer)、[DPO 原论文](https://arxiv.org/abs/2305.18290) |
| 强化学习 / RFT | 按任务反复生成候选或完整轨迹，评分，再更新权重并评测 | 生成阶段运行推理引擎，更新阶段运行训练引擎；评分可能是规则、CPU 代码或另一个 GPU 模型。AWS 的多轮 RL 包含 rollout 编排、轨迹、训练、检查点和评测。[AWS 公告](https://aws.amazon.com/about-aws/whats-new/2026/06/multi-turn-reinforcement-learning-on-sagemaker-ai/)、[NVIDIA NeMo RL 架构](https://docs.nvidia.com/nemo/rl/nightly/about/backends.html) |
| 环境 / 工具 | 为 Agent 提供代码执行、浏览、检索、应用状态及奖励验证 | 可能增加 CPU、内存、存储、网络和沙箱需求；NVIDIA NeMo Gym 的特定设计是 CPU-only 环境，模型生成仍由 GPU 推理服务承担。**这不是行业通用 CPU/GPU 配比。**[NeMo Gym 集成](https://docs.nvidia.com/nemo/rl/nightly/design-docs/nemo-gym-integration.html) |
| 上线推理 | 把改进后的模型提供给最终用户 | 与训练中的 rollout 分属不同业务用途；一份训练用 rollout 不能同时计为另一份独立的终端推理需求。 |

本稿的 `MODEL_DERIVED` 记账式是：**后训练实际资源 = 各训练任务的生成、权重更新、评分/环境与评测资源之和；评估净新增设备需求时，还须考虑共用集群的转用和每单位任务效率提升。** 若某类任务每秒完成 `rollout/s` 条轨迹，每条轨迹需要 `CPU 秒/条` 的环境执行，在目标利用率 `u` 下，粗略所需 CPU 核数约为 `rollout/s × CPU 秒/条 ÷ u`。这个式子必须用相同任务的实测输入，不含模型 judge 的加速器负载，也不能直接换算为 Xeon 销量。计费额、芯片订单和股东利润分别需要费率、利用率、硬件采购与融资资料。微软称其集群同时服务预训练、后训练、合成数据和推理，并称某些模型的每 GPU token 吞吐在一季度改善超过 30%；这说明“有后训练工作负载”与“同幅度新增机器”之间还隔着复用和效率。[Microsoft FY26Q1 电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q1)

**企业数据也不自动带来权重训练。** Microsoft 的产品指南建议把需要引用私有或频繁变化知识的任务交给 RAG，把需要改变行为、风格或任务能力的任务交给微调；真实客户也可能先改提示词、工具和评测。因此“企业拥有数据 × 企业数量”不是后训练预算公式。[Microsoft Foundry RAG 指南](https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation)

## 2. 两人语料中的命题与本次重建

| 来源 | 能归属于本人的表达 | 本次报告怎样检验 |
|---|---|---|
| Herman Jin，2026-09-25 | 以个人 AI 探索提出后训练需求持续扩张、许多公司需求未满足，提醒不要只看终端推理、coding、2C Agent 或单一模型公司的 ARR；并预告进一步讲解。[原帖](https://x.com/ShanghaoJin/status/2103377573053112496)、[本地语料](../../../Herman%20Jin/x-archive/x-2026-09-25/posts.jsonl#L1301)、[首轮 HJ-027](../kol-distillation-2026-09-26/herman-jin-cases.jsonl#L27) | 这是**需求方向假设**，个人观察没有公开可复算的客户数、GPU 小时、CPU 小时或预算；首轮案例已标 `context_limited`。本稿按产品、付费、设备、利润逐关验证。 |
| Herman Jin，2026-06 至 08 | 其公开回复认为模型效果可能更多取决于工程与后训练；8 月视频的本地自动转录谈及企业利用自有数据在云平台做后训练。[回复](https://x.com/ShanghaoJin/status/2070268846691492069)、[本地回复](../../../Herman%20Jin/x-archive/x-2026-09-25/replies.jsonl#L3780)、[视频入口](https://www.youtube.com/watch?v=TQ3G5Jf-yNM)、[本地自动转录](../../../Herman%20Jin/market-overview/market-overview-2026-08-25/transcript.jsonl#L173) | 自动转录未经本轮听音校正，只作背景。微软已确认其集群承接后训练，但没披露该部分业务收入，因此尚不能把企业定制需求量化为云厂增量。 |
| Serenity 的现有样本 | 本地检索未找到她对“后训练总需求”给出完整、独立的预算推导。她曾谈推理 ASIC 对 GPU 份额的威胁，也有成本降低扩大训练/推理使用的回复；这些都不是后训练规模证明。[本地回复 1](../../../Serenity/data/clean/replies.jsonl#L3154)、[本地回复 2](../../../Serenity/data/clean/replies.jsonl#L2227) | 将 [SR-M01](../kol-distillation-2026-09-26/serenity-methods.jsonl#L1) 的需求到瓶颈、[SR-M02](../kol-distillation-2026-09-26/serenity-methods.jsonl#L2) 的付款与融资、[SR-M03](../kol-distillation-2026-09-26/serenity-methods.jsonl#L3) 的产品/阶段对应关系用于本题。**这是分析者应用其方法，不是她本人给出的 post-training 股票推荐。** |

Serenity 2026-08-31 关于 Apple Mac mini / Raspberry Pi 用于 RL 的帖子及回复在本地语料中有截断且援引外部传闻；本轮没有取得相应公司的直接采购披露，故它们不进入供应商收入结论。[本地帖子](../../../Serenity/data/clean/posts.jsonl#L1699)、[本地回复](../../../Serenity/data/clean/replies.jsonl#L4983)

## 3. 证据到哪一层

| 待证命题 | 已见的一手证据 | 当前判断 / 缺口 |
|---|---|---|
| 后训练能够改善特定任务 | OpenAI 的 o1 公告显示推理表现随强化学习训练计算增加而改善；DeepSeek-R1 研究给出 RL 与多阶段训练的实验路径。[OpenAI](https://openai.com/index/learning-to-reason-with-llms/)、[DeepSeek-R1 论文](https://arxiv.org/abs/2501.12948) | **技术层成立，任务有边界。** 奖励质量、初始模型能力和评测集决定效果；不能据论文外推每个企业都要大规模 RL。 |
| 已推出训练产品或预览 | AWS 2026-06 发布多轮 RL，按处理 token 付费；Microsoft Foundry 文档列 RFT；CoreWeave 2026Q2 公布 RL Sandboxes；Google 2026-09-15 把 Gemini RLFT 列为 **Preview**。[AWS](https://aws.amazon.com/about-aws/whats-new/2026/06/multi-turn-reinforcement-learning-on-sagemaker-ai/)、[Microsoft](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reinforcement-fine-tuning)、[CoreWeave](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx)、[Google 更新日志](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes) | **产品化成立，成熟度不同。** 上线、预览或定价是供给证据，不是已付费使用量。Microsoft Learn 页虽可打开正文，页面模板同时出现授权提示，记录为 `PUBLIC_PAGE_VALIDATE`。 |
| 已形成可分辨的大规模商业收入 | Microsoft 2026-07 称 Foundry 10 万客户、收入同比翻倍以上；CoreWeave 2026Q2 总收入 **25.75 亿美元**，并公布新 RL 工具。[Microsoft](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)、[CoreWeave](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx) | **后训练专项收入 `SOURCE_UNAVAILABLE`。** 两家数据混合模型服务、推理、Agent 及其他基础设施；不得分摊成后训练 TAM。 |
| 所有供应商会同比例受益 | NVIDIA NeMo RL 有生成与训练后端；AMD 2026-09 公布 veRL/ROCm 的 RL 运行与小规模实验；Google 还演示过 TPU 上的 RL 路线。[NVIDIA NeMo RL](https://docs.nvidia.com/nemo/rl/nightly/about/backends.html)、[AMD 工程文章](https://rocm.blogs.amd.com/software-tools-optimization/verl/README.html)、[Google 技术文章](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-reinforcement-learning-and-fine-tuning-on-tpus/) | **加速器适配成立，收入归因未成立。** AMD 文中的 16 张 rollout GPU + 16 张训练 GPU 是单个实验配置，不能推行业配比；本轮查阅的 [NVIDIA FY27Q2 财报](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/)和 [AMD 2026Q2 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm)均未按后训练拆分销售。 |
| INTC CPU 因后训练而加速销售 | Intel 2026Q2 披露服务器销量同比增长 9%，主要由 hyperscaler 需求推动，但没有按最终工作负载拆分。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm) | **后训练归因 `SOURCE_UNAVAILABLE`。** 环境/编排可运行在 Intel、AMD、Arm 或其他 CPU；还须确认具体部署、利用率与单位利润。 |

另有两项明显的反向检查：OpenAI [2026 年自助微调平台调整](https://developers.openai.com/api/docs/deprecations)使新组织无法创建训练任务，并计划于 2027-01-06 停止现有活跃客户新建任务；这只说明**该产品渠道**在收缩，不能证明行业后训练总需求下降。另一方面，AMD 自己的 [异步 RL 实验](https://rocm.blogs.amd.com/software-tools-optimization/verl/README.html)显示同样 32 张 GPU 条件下单步时间改善约 1.8 倍，同时后段生成长度变长却未同步改善准确率；这是“更多生成 token 并非都形成有用质量”的具体例子，仍只是该实验结果。

## 4. 从 post-training 推到可投资对象

| 环节 | 可成立的传导 | 何时不能上升为投资结论 |
|---|---|---|
| 云与模型定制平台：MSFT、AMZN 等 | 提供模型选择、微调、RL、评测和上线服务；可能取得训练与后续推理费用。[Microsoft FY26Q1](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q1)、[AWS 多轮 RL](https://aws.amazon.com/about-aws/whats-new/2026/06/multi-turn-reinforcement-learning-on-sagemaker-ai/) | 若训练主要是集团内部研发、没有新增客户支付，或训练服务收入被更低推理价格抵消。缺专项收入和毛利率。 |
| 加速器及软件生态：NVDA、AMD | rollout 与权重更新均可消耗 GPU；两家都给出可运行 RL 的软件栈。[NVIDIA NeMo RL](https://docs.nvidia.com/nemo/rl/nightly/about/backends.html)、[AMD veRL](https://rocm.blogs.amd.com/software-tools-optimization/verl/README.html) | 总 GPU 出货、数据中心收入含预训练/推理等；集群共用、算法效率和客户自研 ASIC 会改变增量和份额。 |
| 环境与云基础设施：CRWV 等 | RL Agent 需要隔离环境、工具调用与评测，CoreWeave 已推出 Sandboxes。[CoreWeave Q2](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx) | 公告没分拆 Sandboxes 收入；同季利息净支出 **6.40 亿美元**，必须把业务增长和融资后股东结果分开。[同一公告](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx) |
| CPU/主机和制造：INTC、AMD、Arm 生态 | 环境和编排会使用 CPU；前一份报告已确认 Intel 服务器产品改善。[Intel 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm) | NeMo Gym 的 CPU-only 实现不能指定 CPU 厂牌或规模。INTC 的 14A 外部代工承诺仍须单独核验，不能由软件训练环节直接推出。[INTC / CPU 报告](../intc-cpu-analysis-2026-09-26/README.md) |

## 5. 可被推翻的情景与下一次检查

| 情景 | 所需的新证据 | 更新动作 |
|---|---|---|
| 需求升级 | 连续两个以上期间披露**付费**后训练任务数、生成/更新 GPU 小时、环境 CPU 小时或专项收入，且客户任务质量和续费改善 | 才可用实际费率与利用率建规模模型，再传到芯片/云收入。 |
| 维持观察 | 更多平台发布 RFT/RL 功能，但财报仍只披露混合 AI 收入与总 CapEx | 认可技术方向，保留供应商收益和规模为条件假设。 |
| 论点转弱 | 更多企业用 RAG/提示/现成模型满足需求；训练工作流效率提高，或收费产品退出而替代渠道未形成可见付费 | 下调**净新增**后训练算力假设，重新检查其他工作负载能否填满共用集群。 |

**最优先补的 5 个口径：**（1）付费客户与任务数；（2）每任务 rollout、参数更新、评测的 GPU 小时和环境 CPU 小时；（3）训练后真实任务质量相对 RAG/提示方案的改善及续费；（4）平台专项收入、成本、利用率；（5）设备供应商可追溯订单和融资后每股收益。当前这些公开量化资料不齐，本稿不估后训练 TAM、不把微软 Foundry 或 NVIDIA/AMD 数据中心收入归到该单一用途，也不据此调整 INTC 目标价。

## 来源记录

| ID | 原件与日期 | 2026-09-26 访问状态 | 本稿用途 |
|---|---|---|---|
| OAI-O1 | [OpenAI, Learning to reason with LLMs](https://openai.com/index/learning-to-reason-with-llms/)，2024-09-12 | `PUBLIC_NO_AUTH` | RL 训练算力与推理表现的公司实验。 |
| DS-R1 | [DeepSeek-R1 论文](https://arxiv.org/abs/2501.12948)，2025-01 初稿 | `PUBLIC_NO_AUTH` | RL 与多阶段后训练路径，实验不代表行业预算。 |
| SFT-DPO | [Hugging Face TRL SFT](https://huggingface.co/docs/trl/sft_trainer)、[DPO 原论文](https://arxiv.org/abs/2305.18290)，动态文档 / 2023-05-29 | TRL `PUBLIC_PAGE_VALIDATE`；论文 `PUBLIC_NO_AUTH` | 固定监督样本与离线偏好优化的工作负载边界。 |
| MSFT-FY26Q1/Q4 | [FY26Q1 电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q1)，2025-10-29；[FY26Q4 电话会](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)，2026-07-29 | `PUBLIC_NO_AUTH` | 集群用途/效率及 Foundry 总客户/收入，后训练占比未披露。 |
| AWS-RL | [AWS 多轮 RL 发布](https://aws.amazon.com/about-aws/whats-new/2026/06/multi-turn-reinforcement-learning-on-sagemaker-ai/)，2026-06-03 | `PUBLIC_NO_AUTH` | 产品、工作流与收费方式。 |
| MSFT-DOCS | [Foundry RFT](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reinforcement-fine-tuning)、[Foundry RAG](https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation)，访问日 2026-09-26 | `PUBLIC_PAGE_VALIDATE` | 产品/替代方案；RFT 页正文可见但模板显示授权提示。 |
| NV-RL | [NVIDIA NeMo RL](https://docs.nvidia.com/nemo/rl/nightly/about/backends.html)、[NeMo Gym](https://docs.nvidia.com/nemo/rl/nightly/design-docs/nemo-gym-integration.html)，访问日 2026-09-26 | `PUBLIC_PAGE_VALIDATE`；nightly 文档可能更新 | 训练/生成后端与一种 CPU 环境实现。 |
| AMD-RL | [AMD veRL on ROCm](https://rocm.blogs.amd.com/software-tools-optimization/verl/README.html)，2026-09-08 | `PUBLIC_NO_AUTH` | 产品适配与**特定**实验性能；不外推份额。 |
| NVDA/AMD-FIN | [NVIDIA FY27Q2 财报](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/)，2026-08-26；[AMD 2026Q2 10-Q](https://ir.amd.com/financial-information/sec-filings/content/0000002488-26-000123/amd-20260627.htm)，2026-08-05 | `PUBLIC_NO_AUTH` | 所查财务披露未按后训练拆分销售；不能把数据中心收入直接归因于后训练。 |
| CRWV-Q2 | [CoreWeave Q2 公告](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx)，2026-08-11 | `PUBLIC_NO_AUTH` | RL Sandboxes 及公司级经营/融资口径。 |
| GOO-RL | [Google Gemini Enterprise Agent Platform 更新日志](https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes)，2026-09-15 更新 | `PUBLIC_PAGE_VALIDATE` | RLFT 预览状态，不作 GA 或客户收入证明。 |
| GOO-TPU | [Google Cloud, Agent Factory Recap](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-reinforcement-learning-and-fine-tuning-on-tpus/)，2026-01-16 | `PUBLIC_NO_AUTH` | TPU 上的 RL 路线，说明机制不指定 GPU 厂牌。 |
| INTC-Q2 | [Intel 2026Q2 Form 10-Q](https://www.intc.com/filings-reports/all-sec-filings/content/0000050863-26-000157/intc-20260627.htm)，2026-07-24 | `PUBLIC_NO_AUTH` | 服务器单位量等历史事实，未作后训练归因。 |
| OAI-FINETUNE | [OpenAI API deprecations](https://developers.openai.com/api/docs/deprecations)，2026-05-07 通知、2026-07-02 限制 | `PUBLIC_PAGE_VALIDATE` | 自助微调渠道收缩，非行业需求总量。 |
| KOL-LOCAL | [首轮观点蒸馏](../kol-distillation-2026-09-26/README.md)与上文逐帖链接 | `USER_PROVIDED`；YouTube 本地文稿为自动转录 | 两人表达与方法归属，不作独立产业数据。 |

一手技术资料详见 [后训练原始资料底稿](primary-evidence.md)。
