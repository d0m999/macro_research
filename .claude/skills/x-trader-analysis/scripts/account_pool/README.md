# twscrape 账号池管理

> **快速参考 / FAQ**。从零开始的详细养号 + Cookies 导出 SOP 看 [GUIDE.md](./GUIDE.md)（推荐第一次配置必读）。

twscrape 用一个 SQLite DB（默认放 `.claude/skills/x-trader-analysis/.account_pool/accounts.db`）维护一组 X 小号。每次抓取时它会按"最近最少使用 + 未限流"的策略挑账号轮流跑，自动绕过单账号限流。

## 为什么需要账号池

| 方案 | 成本 | 稳定性 | 适用 |
|---|---|---|---|
| Apify | $5/万条 | 高 | 一次性大批量回溯 |
| Scweet 单号 | 免费 | 中（cookies 易过期） | 临时分析单博主 |
| **twscrape 账号池** | **零边际成本** | **高（多号轮询）** | **常态化主力**：每月 1-3 博主、小号长期复用 |

常态化用法目标：3-5 个小号，每号每天 ≤500 请求，总抓取窗口能稳定覆盖每月 1-3 位博主的全部更新。

## 注册 X 小号要点

- 不要用主号——一旦被风控，影响真实账号
- 每个小号最好用**独立邮箱**（推荐 Gmail 应用专用密码，或者每号一个临时邮箱）
- 注册时尽量补全：头像、昵称、绑定手机号（强烈推荐手机号验证，未验证号死的快）
- 注册后**先用浏览器登录 1-2 周**，养号一段时间再加入账号池，避免新号一开口就被风控
- 不同小号尽量用不同 IP（开 VPN 切换地区） / 不同浏览器 fingerprint

## 导出 cookies (推荐, 最稳)

cookies 模式比账号密码自动登录稳定得多。步骤：

### Chrome / Edge
1. 浏览器登录 https://x.com
2. F12 打开 DevTools → 切到 **Application** 面板
3. 左侧 Storage → Cookies → https://x.com
4. 找到这两条并复制 Value：
   - `auth_token`（一长串十六进制）
   - `ct0`（X 的 CSRF token）
5. 拼成字符串：`auth_token=<value>; ct0=<value>`

### Firefox
1. 登录 https://x.com
2. F12 → **Storage** 面板 → Cookies → https://x.com
3. 同上复制 auth_token 与 ct0

### 浏览器扩展（更省事）
- Chrome: "Cookie-Editor" 扩展，登录后右上角图标 → Export → 选 "Header String" 直接拷贝
- Firefox: "cookies.txt" 扩展

## 一键添加账号

```bash
# 推荐：cookies 模式
make account-add ARGS="--username u1 --cookies 'auth_token=xxx; ct0=yyy'"

# 备选：账号密码 + 邮箱（twscrape 用 IMAP 拉验证码，部分邮箱不支持）
make account-add ARGS="--username u1 --password p1 \
    --email u1@gmail.com --email-password mp1"
```

添加成功后脚本会自动做一次 `user_by_login("x")` 测试调用，验证 cookies 真正可用。

## 查看账号池健康度

```bash
make account-health
```

输出表格列说明：
- `username` — X 小号
- `active` — twscrape 是否会用它（False 表示被自动停用）
- `logged_in` — 是否已登录成功
- `probe` — 即时探测结果：
  - `ok` 正常
  - `rate_limited` 临时限流，等几小时自动恢复
  - `cookies_bad` cookies 过期 / 账号被风控，**需要重登**
  - `error` 其它错误
  - `skipped` 账号未激活，未做 probe
- `last_used` — 最近一次被 twscrape 使用的时间
- `total_req` — 总请求数
- `suggest` — 一句话补救建议

加 `--fix` 会把异常账号自动 `set_active(False)`，避免污染下次抓取：

```bash
uv run python scripts/account_pool/health_check.py --fix
```

## 风控规避建议

twscrape 自带"挑空闲号 + 受限号停用"逻辑，但仍需配合：

1. **频率**：每号每天 ≤ 500 请求。3-5 号配置可支撑 1500-2500 请求/天，足够月度 1-3 博主回溯。
2. **错峰**：抓取分散在白天，不要 24 小时不停跑；夜间间隔 6-12 小时。
3. **限流**：scrape_twscrape.py 每分片之间已经有 5-15s 随机抖动，不要手动改小。
4. **健康**：每周跑一次 `make account-health`，及时换号。
5. **更新 cookies**：cookies 有效期典型 30 天。固定每月初批量重导一次。
6. **隔离 IP**：理想情况每号一个独立出口 IP；至少不要 5 个号同一 NAT 公网 IP。

## 常见问题

**Q: cookies 过期怎么办？**
A: 用同一 `--username` 重跑 `add_account.py --cookies "新值"`，twscrape 会覆盖旧记录。

**Q: 账号被封了怎么办？**
A: `health_check --fix` 把它 set_active(False)。换号继续。被风控的号短期内不要复活，等 1-2 周再试。

**Q: 全部号都被风控？**
A: 1) 检查抓取频率是不是太高；2) 临时改用 Apify 兜底（`make scrape-apify`）；3) 重新养一批号。

**Q: 数据库放哪？要不要提交？**
A: 默认 `.claude/skills/x-trader-analysis/.account_pool/accounts.db`。**绝对不要提交**，已经在 `.gitignore` 里。

**Q: 想用现成的号池服务？**
A: 不推荐——共享号池随时被批量风控。自己养 3-5 号成本极低，且生命周期可控。
