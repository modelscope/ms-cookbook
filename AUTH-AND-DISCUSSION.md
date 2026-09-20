# 魔搭登录、划线与评论

## 功能与可见性

- 游客可阅读正文、公开划线评论与章节留言。
- 登录后可选中同一段落内最多 2000 字：保存仅自己可见的划线，或发表公开想法。
- 章节末尾可留言，按最新优先显示；支持加载更多。点击引用可回到原文。
- 作者可删除自己的记录。`MODERATOR_SUBS` 可配置管理员的 OIDC sub（逗号分隔），管理员可删除公开内容。
- 原文变更后先校验段落、偏移和引用；无法唯一匹配时保留笔记并提示无法定位，不把划线错误应用到其他文字。

## 本地运行

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
APP_BASE_URL=http://127.0.0.1:7860 .venv/bin/uvicorn app:app --host 127.0.0.1 --port 7860 --no-access-log
```

访问 http://127.0.0.1:7860 。原来的静态 HTTP 服务不提供 `/api`，不能用于登录和评论。

默认评论与账号数据保存在 `.data/reading.sqlite3`，访问统计保存在独立的 `.data/analytics.sqlite3`，密钥保存在 `.data/session.key`；这些文件均被 Git 忽略。
没有 OAuth 配置时明确显示登录待开启，不提供伪造的演示登录。
本地真实 OAuth 需创建允许本地回调的互联应用，设置以下环境变量（不要把密钥写入 Git）：

- `OAUTH_CLIENT_ID`
- `OAUTH_CLIENT_SECRET`
- `OPENID_PROVIDER_URL=https://www.modelscope.cn`
- `APP_BASE_URL=http://127.0.0.1:7860`
- 回调地址：`http://127.0.0.1:7860/auth/callback`

## 创空间部署

依据官方文档 https://www.modelscope.cn/docs/studios/oauth ：Static 不支持内置 OAuth。
本版本需要 Docker 创空间（平台要求已绑定阿里云账号并完成实名认证）。
在现有创空间设置中将部署类型调整为 Docker，启用 OAuth，仅勾选 `openid profile`，然后部署本版本。
平台自动注入 `OAUTH_CLIENT_ID`、`OAUTH_CLIENT_SECRET`、`OPENID_PROVIDER_URL`、`OAUTH_SCOPES`、`STUDIO_HOST`。
线上回调为 `https://<STUDIO_HOST>/auth/callback`；如果使用独立应用则显式配置 `APP_BASE_URL` 和对应回调。

Docker 监听 7860，持久化数据目录固定为 `/mnt/workspace/purplebook`。创空间通过 `ossfs` 挂载该目录，访问统计的 SQLite 运行库位于容器本地磁盘，并定期生成一致性快照保存到持久化目录；同时保留上一版快照作为恢复点。请备份持久化目录，不要启用多个应用副本共同写入这些数据。
更换域名后需更新 OAuth 回调。创空间 iframe 的第三方 Cookie 受浏览器限制，因此登录在新窗口完成，并在该独立页面继续阅读和评论。

部署脚本已改为要求 Docker，拒绝把带后端的版本发布成 Static。GitHub Action 会先跑 API 测试再发布。
当前实现不会自动更改线上创空间设置，也不会把本地未提交的改动推送到线上。

## 访问统计

网站会按逻辑页面记录匿名 PV 和 UV，首页、目录、阅读路径、真实任务库、社区页和每一章分别统计。访客标识由浏览器随机生成，服务端只保存经过 HMAC 处理的哈希，不关联魔搭账号、姓名或评论数据。统计日期使用 `Asia/Shanghai`，区间查询使用最近 180 天的每日访客记录，累计 UV 通过独立去重表持续保存。全站小时 PV/UV 从功能启用后开始记录，小时明细保留最近 90 天；同一访客在每个小时内分别去重，所选日期的 UV 按全天访客去重。统计库运行在本地文件系统，持久化层保存当前与上一版完整快照；检测到运行库损坏时优先从快照恢复，并保留带时间戳的故障副本。

统计页面位于 `/analytics`，打开后直接显示累计、今日、每小时和所选时间范围的数据。小时视图支持今天、昨天和最近 90 天内的指定日期。今日指标每日 0 点重新计算，近 N 天指标使用滚动窗口，累计指标从有效统计数据的首日持续增长。该地址不放入读者页面的公开导航，知道固定网址即可访问。统计接口只提供聚合后的只读数据。

## 身份与安全

使用 Authlib 完成 OIDC state、nonce、签名及身份校验。Cookie 中只保存随机服务端会话 ID、CSRF 与短期授权事务；不保存访问令牌。
数据库保存随机用户 ID、OIDC sub、显示名称和评论；用户 ID 只取自验证后的服务端身份。退出时撤销服务端会话。
写操作要求有效登录、同源 Origin 和 CSRF token。每位用户每分钟最多 10 次写入。静态文件仅通过显式允许的目录提供，源代码、数据库、密钥不会作为静态文件暴露。
前端通过 textContent 渲染用户内容，拒绝将评论作为 HTML 执行。
生产会话使用 HTTPS Secure、HttpOnly、SameSite=Lax Cookie。

## 验证

```sh
.venv/bin/pip install pytest
.venv/bin/python -m pytest tests -q
node --check assets/discussion.js
node scripts/check-site.mjs
```

测试覆盖游客写入拒绝、CSRF、私人划线隔离、所有权删除、持久化重启、分页、频率限制、退出撤销、静态文件隔离、OAuth 非法 state，以及模拟已验证身份后的会话建立。
真实魔搭授权回跳必须在配置合法 OAuth 应用后联调；模拟提供方测试不等同真实 OAuth 登录验收。

浏览器端到端验证（安装 Playwright 后）：

```sh
node tests/discussion-browser.cjs
# 使用本机 Edge 时：PLAYWRIGHT_CHANNEL=msedge node tests/discussion-browser.cjs
```

该验证会启动 7861 端口的隔离测试服务并生成测试会话，仅写入临时目录；结束后清理，不往真实评论库写入测试内容。

创空间提供方兼容：认证发现固定使用 `https://www.modelscope.cn/.well-known/openid-configuration`，避免平台内部提供方别名触发地址白名单或浏览器跳转问题。客户端 ID 和密钥仍取自平台注入。
