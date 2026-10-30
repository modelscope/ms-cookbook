# 魔搭登录、划线与评论

## 功能与可见性

- 游客可阅读正文、公开划线评论与章节留言。
- 登录后可选中同一段落内最多 2000 字：保存仅自己可见的划线，或发表公开想法。
- 章节末尾可留言，按最新优先显示；支持加载更多。点击引用可回到原文。
- 公开留言可点击“回复”，回复引用原留言并显示在其下方；父留言还没加载时先显示引用，加载更多后归入对应讨论。原留言删除后保留其他读者的回复，并提示原留言已删除。
- 用户名链接到魔搭个人主页。新登录优先使用 `preferred_username`，缺失时补取官方 userinfo / OpenAPI 的账号字段。旧留言和愿望始终提供可点击的主页解析入口：已保存用户名时直接跳转；旧显示名为账号名时，通过公开用户接口精确核实后跳转并回填，无需先退出重登。无法精确核实时提示作者重新登录，不做模糊用户搜索。
- 创空间会把应用路径包装为 iframe，不能依靠应用的 303 跳转打开禁止嵌入的魔搭主页。显示旧账号时通过 `/api/readers/{id}/profile` 预先获取真实地址并更新为普通外链；同一页面内按读者复用解析请求。解析尚未结束时点击则尝试预留独立窗口，拦截空白弹窗的浏览器仍可在解析完成后使用普通外链。回归测试确认不会导航到应用中转页。
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
数据库保存随机用户 ID、OIDC sub、显示名称、魔搭用户名和评论；用户 ID 只取自验证后的服务端身份。需要补取 userinfo 时校验其 sub 与已验证身份一致。退出时撤销服务端会话。
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

## 正文链接与首页数字

构建时自动把正文及代码里的裸 HTTP(S)/www 网址转换为可点击链接，保留文字、代码复制内容和原有链接。外部链接在新窗口打开。
MP4 附件构建为带播放控件、支持手机内联播放的播放器，并保留单独打开的链接；不再强制下载。原始源稿及 GitHub Markdown 导出保持不变。

首页“互动交流”读取 `/api/community/summary` 的实时数据库总数，包含公开留言、回复和划线想法，不包含私人划线与许愿池。页面首次打开、切回首页、窗口重新聚焦、发表或删除记录后更新；停留首页时每 30 秒刷新一次，失败时保留上次结果，不显示伪造的零。

首页数字随每次仓库部署重新生成：社区共建按 GitHub `README.md` 中的“内容共建者”名单与 `assets/contributors/github.json` 的代码贡献者名单条目合计，不跨平台推断身份；介绍、主页链接与社区页面使用同一份生成数据。旧名片索引 `assets/contributors/profiles.json` 不再用于计数或展示名单。真实任务取自 `README.md` 的 `practice-cases` 名单，仅统计已开放章节；`content/practice.json` 只定制卡片文案和配图，新增案例未填写定制信息时仍可显示并计数。合计字数统计所有已开放章节（含标题与代码），汉字逐字计、英文及数字按词计，符号和空白不计。首页以万字显示两位小数，悬停可见精确数字。

GitHub `main` 合入后由 Actions 生成内容、校验并部署，创空间并非即时读取 GitHub。可用 `/deployment.json` 的 `commit` 核对线上对应的 GitHub 版本；部署完成才代表同步成功。
