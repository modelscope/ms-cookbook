# 章节阅读与维护

在 GitHub 阅读请打开 [Markdown 章节目录](chapters/)。每章对应 `chapters/chapter-NN.md`，支持直接显示正文、图片、代码、公式和表格。

- `manifest.json`：篇章顺序、标题、阅读状态与同步日期。
- `chapters/`：自动生成的 Markdown 阅读版。
- `source-html/`：用于网站构建的原始 HTML，保留段落、标题层级、列表、表格、代码、公式、图片和附件顺序，采用 XML 兼容的闭合标签。
- `sync-report.json`：本次原稿同步的版本号、内容哈希及逐章校验结果。它记录导入时的证据，不会随日常修改自动改写。

章节按全书目录连续编号为 01–39，文件名、目录和阅读路径使用相同编号。第 22、39 章目前是原稿中的共建邀请，第 29 章为 Agent 入门正文。`discussionId` 是留言存储的固定标识，不随目录编号调整，以便原有笔记和留言继续归属同一篇正文。

## 修改与构建

正文修改必须有明确的勘误依据或作者确认。请保留单篇文章的内容、章节结构与原有代码；网站布局调整只修改页面代码与样式。

修改 `source-html/` 下的章节源文件后，在仓库根目录运行：

```bash
python3 scripts/build-content.py
node scripts/check-site.mjs
python3 -m http.server 4174 --bind 127.0.0.1
```

构建脚本同时生成 `chapters/*.md` 和 `assets/content.js`，不改写正文。Markdown 中的复杂表格使用 GitHub 可渲染的 HTML 表格保留单元格结构。请同时提交源文件与生成文件，不要独立修改 Markdown。运行 `python3 scripts/build-content.py --check` 可检查两种输出是否过期。

原稿中的空标题仍保留在源文件中，网站目录会跳过无文字的条目。第 27 章当前保留原稿的待更新说明。嵌入表格的实际单元格内容随正文提供，图片与附件使用本地相对路径。

完整参与方式见 [贡献指南](../CONTRIBUTING.md)。

旧的 `chapters/` 稿件已迁移到本目录，Git 历史保留原版本。`node scripts/build-content.mjs` 继续作为兼容入口调用同一个 Python 构建器；加上 `--check` 可只校验、不写文件。构建需要 Python 3。

2026-10-15 新增第 11 章 MiniCPM 文本微调与手机部署、第 21 章 MiniCPM-V 手机巡检，分别插在原第 10/11、19/20 章之间。后续章节顺延，旧章 `discussionId` 保持不变。来源、原稿版本与编号映射见 [MiniCPM 同步记录](minicpm-sync-report.json)；两章均可下载飞书原附的[实践包](../assets/minicpm-20261015/minicpm-practice-v0.1.zip)。包内稿件与验证说明保留附件发布时的版本，正文以 `source-html/` 和生成的 Markdown 为准。

2026-10-16 在第 25 章之后新增第 26 章「想要教学海报？要不试试让 AI 帮忙画一张」，完整同步飞书原文及 16 张配图。原第 26–37 章顺延为第 27–38 章，既有 `discussionId` 保持不变。来源、原文版本、素材校验值及编号映射见 [Qwen-Image 同步记录](qwen-image-sync-report.json)。

2026-10-22 整合 Mini AI Scientist 社区投稿：保留已合并的 MiniCPM 与 Qwen-Image 章节，将 Mini AI Scientist 编为第 37 章，原第 37–38 章顺延为第 38–39 章。既有正文与 `discussionId` 保持不变；历史同步记录仍保留导入时的编号与证据。

2026-10-30 按确认后的目录将「补充：Agent 框架知识」移至第七篇末尾：原第 36 章产线巡检调整为第 35 章，原第 37 章 Mini AI Scientist 调整为第 36 章，原第 35 章框架知识调整为第 37 章。三篇正文与既有 `discussionId` 保持不变，源文件、Markdown、网站数据及 README 引用同步调整。
