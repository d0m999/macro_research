# Task 2: Financial Modeling

只在执行 initiating coverage 的财务模型任务时读取。

1. 定义历史/预测期间、币种、单位、GAAP/non-GAAP 和 consolidated/segment 口径。
2. 从 source manifest 填充历史 actuals，保留 reported label、期间、单位、来源和 adjustment。
3. 按业务模型建立收入、margin、tax、D&A、CapEx、working capital、debt、share count 和 FCF drivers。
4. 预测只使用 dated guidance、用户输入或有推导的 `MODEL_DERIVED` 情景；无来源 consensus 保持缺失。
5. 用公式连接 schedules、三表和 FCF；不以隐藏 hardcode plug 平衡模型。
6. 完成资产负债、现金、retained earnings、debt、shares 和 scenario checks。

完成时模型中的每个 hardcode 有状态，每个派生值可追踪；金融经验参数不得作为事实默认值。
