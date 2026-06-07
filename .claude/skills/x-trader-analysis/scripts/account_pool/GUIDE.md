# X 小号养号 + Cookies 导出完整指南

> 配套阅读: `README.md`（快速参考 / FAQ）。本文是从零起步的详细 SOP。
> 适用场景: 准备 3-5 个 X 小号供 twscrape 长期复用。
> 预计投入: 单次 1.5-3 小时（注册），后续每天 5-10 分钟养号 × 1-2 周。

---

## 心智模型（必读 30 秒）

X 风控的核心逻辑是 **行为指纹 + 设备指纹 + 网络指纹** 三层比对。脚本失败 99% 不是技术问题，而是号的"真人度"不够。

**铁律**:
- 新号注册后 **24 小时内不要登录任何抓取脚本**——立刻调用 API 等于自杀
- 养号期 **必须用浏览器手动操作**，每天 5-10 分钟，至少 7 天
- 进池前账号必须"看起来像真人": 头像、bio、几条原创推、几十次互动
- 一旦进池，**前 7 天低强度跑**（每天 ≤100 请求），观察是否稳定

跳过任何一条都会显著缩短账号寿命。Apify 兜底（`make scrape-apify`）就是为这种情况准备的。

---

## Part 1: 准备资源（注册前 30 分钟）

### 1.1 邮箱（3-5 个独立邮箱）

**推荐 → 不推荐**:

| 邮箱 | 通过率 | 稳定性 | 备注 |
|---|---|---|---|
| Gmail（独立账号） | 高 | 高 | **推荐**。每号一个 Gmail，开应用专用密码 |
| 自建域名邮箱 | 高 | 高 | 有自己域名最好 |
| iCloud / Outlook / Hotmail | 中 | 中 | 不要用 + 别名（X 能识别） |
| ProtonMail / Tutanota | 低 | 低 | X 经常拒绝隐私邮箱 |
| 临时邮箱（10minutemail 等） | 极低 | 极低 | 注册都过不了 |

**Gmail 应用专用密码生成**（用于 twscrape IMAP 拉验证码）:
1. 登录 myaccount.google.com → 安全性 → 两步验证（必须先开）
2. 两步验证页面下方 → 应用专用密码 → 生成
3. 应用选 "邮件"，设备选 "Mac/Other"
4. 复制 16 位密码（去掉空格）。这就是 `--email-password` 的值

### 1.2 手机号（强烈推荐）

**手机号验证的号比纯邮箱号寿命长 5-10 倍**。

获取顺序:
1. **国内手机号**: 最稳，但占用真实号码
2. **Google Voice / 国外实卡**: 中等
3. **SMS-Activate / 5sim / sms-man** 等虚拟号平台: $0.5-2/号，稳定性中等。注意挑"X / Twitter 专用"号段
4. **TextNow / TextFree**: 免费但 X 拒绝率高

**虚拟号注意**: 同一平台短时间内连买 5 号容易触发批量风控（X 能识别号段）。分散购买，间隔 1-2 天。

### 1.3 IP / 网络

每个小号尽量用 **不同的出口 IP** 注册和长期使用。最佳实践:

| 方案 | 成本 | 风控通过率 |
|---|---|---|
| 每号一个住宅代理（Bright Data / IPRoyal） | $5-15/月/号 | 极高 |
| 每号一个 VPS + WireGuard | $5/月 | 高 |
| 4G 流量卡 + 手机热点（每号开关一次飞行模式换 IP） | 几乎零 | 高 |
| 公共 VPN（NordVPN 等） | $5/月 | 中（共享 IP 易触发） |
| 同一家用 WiFi 注册 3-5 号 | 0 | 低（X 看到同源） |

**最低标准**: 至少不要用同一 NAT 公网 IP 注册所有号。在家用 WiFi 注册 1 号、手机 4G 注册 2 号、咖啡厅 WiFi 注册 3 号也比都在家强。

### 1.4 浏览器隔离

每个小号用独立的浏览器 profile，避免 fingerprint 串号:

**方法 A: Chrome 多 user-data-dir（最稳）**
```bash
# 为 u1 创建独立 Chrome 实例
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --user-data-dir=$HOME/.x-profiles/u1 &

# u2
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --user-data-dir=$HOME/.x-profiles/u2 &
```
每个目录是完全独立的 Chrome（独立 cookies / 扩展 / 历史 / 指纹）。

**方法 B: Firefox Multi-Account Containers**（官方扩展）
- 同一 Firefox 进程，但每个 container 隔离 cookies + storage
- 比方法 A 简单，但 fingerprint 部分仍共享

**方法 C: 不同浏览器**（Chrome / Edge / Firefox / Safari 各一个）
- 最简单，但只能撑 3-4 号

---

## Part 2: 注册（每号 15-25 分钟）

### 2.1 开始注册

1. 启动独立浏览器 profile（见 1.4）
2. 接入对应的 IP（VPN / 代理 / 手机热点）
3. 访问 https://x.com → 点 "Sign up" 或 "Create account"
4. **关键**: 选 "Use phone instead" 用手机号注册（不要用邮箱注册流程）

### 2.2 填写资料

| 字段 | 建议 |
|---|---|
| Name | 真名感的英文/中文名，不要 user123 / test4567 |
| Phone | 输入手机号，等待 SMS 验证码 |
| Birthday | 25-45 岁之间随机 |
| Username（@handle） | 别太像 bot。`john_btc_2024` 比 `xkfd9z3m4` 好 |
| Password | 12+ 位，混合大小写数字符号 |

### 2.3 验证步骤

X 注册有 3-5 个连续验证步骤:
- 手机号验证（收 SMS）
- 偶尔会要求邮箱二次验证
- arkose challenge（推拼图、选物体）—— 别用脚本，老实手动做
- 设备指纹检测（背景静默执行）

任何一步卡住超过 2 次重试，**放弃该号**，换 IP + 邮箱 + 手机号重来。死磕只会让 IP / 邮箱进黑名单。

### 2.4 完善 profile（注册成功后立刻做，10 分钟内）

完成度低的号 24 小时内被锁概率 > 50%。立刻做:

1. **上传头像**: 任何看起来真实的图（人像 / 风景 / 卡通都可以），不要默认蛋形
2. **写 bio**: 30-80 字。crypto 相关或日常都行
   - 好例子: `BTC max | DeFi explorer | NYC`
   - 好例子: `trading futures since 2019, mostly ETH / SOL`
   - 烂例子: bio 留空 / 只有 emoji / `test account`
3. **背景图**: 可选但加分
4. **位置**: 随便填一个真实城市
5. **关注 5-10 个真实账号**: @elonmusk @VitalikButerin @CryptoCobain @cz_binance 等大号
6. **发第 1 条推**: 一句无害的话。`GM, market looks interesting today` / `any thoughts on BTC?` 都行

完成上面 6 步算"基本完成"。可以关闭 X 等 24 小时再来。

---

## Part 3: 养号 1-2 周（每天 5-10 分钟）

### 3.1 每日活动清单（必做）

每天打开浏览器，对每个小号做:

- [ ] 滚动 timeline 1-2 分钟（不要立刻关）
- [ ] Like 5-10 条推文（点不同账号的，不要集中点一个）
- [ ] Retweet 1-2 条
- [ ] 自己发 1 条推（看心情，但每周至少 3 条原创）
- [ ] 关注 1-2 个新账号
- [ ] 偶尔回复 1 条推文（`good point` / `agree` 之类）

### 3.2 强烈禁止

- 24 小时不上线（X 视为僵尸号）
- 一天发 10+ 推（spam 嫌疑）
- 一天关注 20+ 账号（反垃圾触发）
- 立刻换国家 IP 登录（`this device is suspicious`）
- 用 X 自带的 API 工具 / 第三方 App 登录
- 点广告（明显的 bot 行为）

### 3.3 何时算"出关"

满足下列条件后才能加入账号池:

- [ ] 注册满 **7 天**（最低）/ **14 天**（推荐）
- [ ] 关注数 30+，粉丝 1-5（自然增长，不要刷粉）
- [ ] 原创推 5+ 条
- [ ] Like / Retweet 累计 50+
- [ ] 邮箱已验证（X 设置里能看到绿勾）
- [ ] 手机号已验证
- [ ] 7 天内没收到过任何 `verify you're human` 弹窗

任何一条不满足 → 继续养。

### 3.4 养号失败的信号

| 现象 | 含义 | 处理 |
|---|---|---|
| 登录时弹 `Confirm your phone` 反复 | 风控盯上 | 完整做完验证，下次别换 IP |
| 突然要求重新填写 birthday / location | 行为可疑 | 老实填，未来 3 天降低活动强度 |
| 发推后 1 分钟内推文被删 | spam filter | 推文内容太可疑（含链接？敏感词？） |
| 24-48h 内账号被锁 | 严重风控 | 弃号 |

---

## Part 4: Cookies 导出详细步骤

养号期满后，导出 cookies 加入账号池。

### 4.1 必需的两个 cookies

只需要两个字段:

| 字段 | 长度 | 作用 |
|---|---|---|
| `auth_token` | 40 位十六进制 | 主登录凭证 |
| `ct0` | 32 或 160 位十六进制 | CSRF token，所有写操作必需 |

`guest_id`、`personalization_id`、`gt`、`kdt` 等都不需要。

### 4.2 方法 A: Chrome / Edge DevTools（推荐）

1. 登录 https://x.com（用对应的浏览器 profile）
2. 按 **F12** 打开 DevTools
3. 顶部 Tab 切到 **Application**（不是 Console / Network）
4. 左侧栏: Storage → **Cookies** → 单击 `https://x.com`
5. 右侧出现 cookies 表格。找 `auth_token` 一行:
   - 单击它，下方面板显示完整 Value
   - 复制 Value（不要复制 Name）
6. 同样找 `ct0`，复制 Value
7. 拼接成字符串:
   ```
   auth_token=<auth_token的值>; ct0=<ct0的值>
   ```
   注意分号后有一个空格

**拼接示例**（假数据）:
```
auth_token=abc123def456789012345678901234567890abcd; ct0=ef0123456789abcdef0123456789abcd
```

### 4.3 方法 B: Firefox DevTools

1. F12 → 顶部 Tab 切到 **Storage**（不是 Inspector / Console）
2. 左侧 Cookies → 点 `https://x.com`
3. 表格里找 `auth_token`，单击它，最下方面板看 Value，复制
4. 同上 `ct0`
5. 拼接

### 4.4 方法 C: Safari

Safari 默认不开发者菜单:
1. Safari → 偏好设置 → 高级 → 勾选"在菜单栏中显示「开发」菜单"
2. 登录 x.com
3. 菜单栏: 开发 → 显示 Web 检查器
4. 顶部 Tab → 存储空间 → Cookies → x.com
5. 找 auth_token / ct0，复制 Value
6. 拼接

### 4.5 方法 D: 浏览器扩展（最省事）

**Cookie-Editor 扩展**（Chrome / Edge / Firefox 都有）:

1. 安装: Chrome Web Store / Firefox Add-ons 搜 "Cookie-Editor"
2. 登录 x.com
3. 点扩展图标 → 弹出窗口列出所有 cookies
4. 右上角 → "Export" 按钮 → 选 **Header String**
5. 自动复制到剪贴板，格式类似:
   ```
   guest_id=v1%3A...; ...; auth_token=abc...; ct0=ef...; ...
   ```
6. 这整段可以直接用（多余字段无害），或只挑 auth_token 和 ct0 拼接

**EditThisCookie**（Chrome 老牌）: 类似流程，导出格式选 "Netscape HTTP Cookie File" 然后手动转。

### 4.6 一步验证 cookies 是否有效

不依赖任何脚本的快速验证:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  'https://api.x.com/1.1/account/settings.json' \
  -H "Cookie: auth_token=<你的auth_token>; ct0=<你的ct0>" \
  -H "x-csrf-token: <你的ct0>" \
  -H "authorization: Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
```

- 返回 `200` → cookies 有效，可以入池
- 返回 `401` / `403` → cookies 失效或账号已被风控
- 返回 `429` → 这个 IP 被 X 临时限流，等 1 小时再测

> Bearer token 是 X web 客户端的公开常量，不变化也不敏感。

---

## Part 5: 加入账号池

```bash
make -f .claude/skills/x-trader-analysis/Makefile account-add \
    ARGS="--username u1 --cookies 'auth_token=xxx; ct0=yyy'"
```

成功标志: 脚本最后会打印 `账号 u1 已加入池子，user_by_login 测试通过`。

如果脚本报错:
- `cookies_bad`: 重新导一次 cookies（可能复制错了）
- `account_locked`: 账号需要登录浏览器解锁
- `database locked`: 关闭其他 `account-*` 命令

---

## Part 6: 长期维护

### 6.1 每周（5 分钟）

```bash
make -f .claude/skills/x-trader-analysis/Makefile account-health
```

- 看 `probe` 列: 有 `cookies_bad` 或 `error` → 重导该号 cookies
- 看 `total_req` 列: 某号特别低 → 检查 active 状态
- 跑 `--fix` 自动停用异常号

**每周保活动作**: 登录每个号的浏览器，刷 timeline 1 分钟，发 1 条推 / 点 5 个 like。号有真人活动 X 才不会眼红。

### 6.2 每月（30 分钟）

- [ ] 重导所有号的 cookies（X cookies 典型 30 天过期）
- [ ] 补 1-2 个新号到池（自然衰减率约 20%/月）
- [ ] 检查 `data/raw/*.jsonl` 总条数，调整月度抓取频率

### 6.3 每季度（1 小时）

- [ ] 复盘哪些号长期稳定（active 占比 > 80%、cookies 失效少）→ 保留
- [ ] 哪些号反复挂 → 弃用，养新号替换
- [ ] 看抓取成功率，更新本 GUIDE

---

## Part 7: 故障诊断速查表

| 现象 | 根因 | 处理 |
|---|---|---|
| 注册时反复 arkose challenge | IP / 浏览器指纹被标记 | 换 IP（手机热点）+ 换 profile 重试，3 次失败弃 IP |
| 注册 1 小时内被锁 | 邮箱可疑 / 资料太空 | 弃号，下次注册立刻完善 profile |
| 加入账号池立刻 cookies_bad | 1. cookies 复制错 2. 没养号 | 1. 重导（看 8.1） 2. 弃号重养 |
| 跑 3-5 天后突然 cookies_bad | cookies 失效（异地登录 / 风控） | 浏览器重登 → 重导 cookies |
| `rate_limited` | 该号超限 | 等 15min-2h 自动恢复，不动它 |
| 全部号同时挂 | 共用出口 IP 被批量风控 | 立刻停爬，等 1-2 周再试 |
| 重导 cookies 后仍 cookies_bad | 账号已封 | 弃号 |
| account-health 显示 logged_in=False | twscrape 还没第一次调用过 | 跑一次 scrape 后再 health |

---

## Part 8: 常见陷阱

### 8.1 复制 cookies 错误

**错误 1**: 把 Name 也复制了
```
错: auth_tokenauth_token=abc123...
对: auth_token=abc123...
```

**错误 2**: 复制了带引号的值
```
错: auth_token="abc123..."; ct0="ef0..."
对: auth_token=abc123...; ct0=ef0...
```
（Cookie-Editor 有时会带引号，手动去掉）

**错误 3**: 分号后没空格
```
错: auth_token=abc;ct0=ef
对: auth_token=abc; ct0=ef
```
（twscrape 通常能解析，但保险起见加空格）

**错误 4**: 复制到换行符
- 用 `tr -d '\n'` 清理: `echo "你的cookies" | tr -d '\n'`

### 8.2 浏览器 profile 串号

同一个 Chrome profile 登录多个 X 账号 → cookies 互相覆盖 → 导出时拿到的是"最后登录"那个号的 cookies。

**防御**: 每个号一个 user-data-dir（见 1.4 方法 A）。

### 8.3 同 IP 大批量注册

3-5 个号 1 小时内在同一 IP 注册 → X 自动批量标记。

**防御**: 间隔 24h 注册一个 + 换 IP。慢比快重要。

### 8.4 cookies 拿对了但 twscrape 报错

很可能是 ct0 的长度问题。X 有两种 ct0:
- 32 位（旧）
- 160 位（新，2024 后）

两种都可以用。但**不要混用**: 比如 auth_token 是旧号导的，ct0 是新号导的 → CSRF 不匹配。

**防御**: 同一个号同一时间导，不要分批导。

### 8.5 验证码邮箱模式

如果用 `--email --email-password` 让 twscrape 自动登录（不推荐）:
- Gmail 必须开应用专用密码（普通密码不行）
- iCloud 需要开 IMAP（设置 → 邮件 → 高级）
- 部分邮箱（QQ / 163）不支持，必须改 cookies 模式

---

## 附录: 完整冷启动 Checklist（贴墙上的版本）

**第一次配置（Day 0-14）**:

- [ ] 准备 3-5 个独立 Gmail，每个生成应用专用密码
- [ ] 准备 3-5 个手机号（虚拟或实卡）
- [ ] 配 3-5 个浏览器 profile（独立 user-data-dir）
- [ ] 准备 3-5 个独立 IP（VPN / 代理 / 4G）
- [ ] Day 0: 注册号 1（25 分钟）
- [ ] Day 0: 立刻完善 profile（10 分钟）
- [ ] Day 1: 注册号 2（不要同一天注册多个号）
- [ ] Day 2-7: 每天 5-10 分钟养所有号
- [ ] Day 8-14: 继续养，强度可以略增
- [ ] Day 15: 导出 cookies × 5
- [ ] Day 15: `make account-add` × 5
- [ ] Day 15: `make account-health` 全绿
- [ ] Day 15: 第一次低强度抓取（USER=test --max 100）

**日常维护**:

- [ ] 每周 `make account-health` 一次
- [ ] 每周浏览器登录每个号刷 1 分钟
- [ ] 每月初批量重导 cookies
- [ ] 每月新养 1 号补充
