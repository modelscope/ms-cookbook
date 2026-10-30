# Contributing to ModelScope Cookbook

Thank you for contributing practical, reproducible knowledge to the cookbook.

## Report an issue

Open a [GitHub issue](https://github.com/modelscope/ms-cookbook/issues/new) with the affected chapter or page, expected behavior, actual behavior, and reproduction steps. For layout issues, include browser, viewport size, and a screenshot without private data.

## Submit a pull request

1. Discuss substantial changes in an issue before implementation.
2. Fork the repository and create a focused branch.
3. Read chapters in `content/chapters/*.md`. Make content edits in `content/source-html/*.html`, or edit the website in `index.html` and `assets/`. Markdown is generated from the HTML sources; do not edit it independently.
4. Preserve article wording, heading hierarchy, section order, code, formulas, and media. Content corrections need a clear source or author approval. Keep layout fixes separate from editorial changes.
5. After editing chapter sources, run `python3 scripts/build-content.py`, then `node scripts/check-site.mjs`. Preview the affected pages on desktop and mobile.
6. Submit a pull request with a concise summary, validation results, and asset attribution. Commit regenerated `content/chapters/*.md` and `assets/content.js` with their source changes.

Never include credentials, document passwords, access tokens, private data, or materials you do not have permission to distribute. Preserve third-party licenses and notices.

## Share a practice on ModelScope

Visit [ModelScope Developer Practices](https://modelscope.cn/spotlight), select **创建内容**, and add the topic **#魔搭紫皮书**. Include the task, environment, reproducible steps, outputs, limitations, and source attribution as appropriate to your contribution.

## Community and credits

### Activity timeline

Keep supplied activity titles, guest titles, descriptions, and agendas verbatim in `content/events/source.md`. Put only dates, identifiers, and activity types in `content/events/manifest.json`. Guest profile links are rendered as platform logos; their destinations are preserved. Activity images are bundled in `assets/events/` using their original filenames.

Run `python3 scripts/build-events.py` to update the website, both Chinese READMEs, and `content/events/README.md` together. Run `python3 scripts/build-events.py --check` to verify that these views match their source. The deployment checks include this verification. Preview the full timeline and homepage on desktop and mobile before submitting changes.

Maintain the two community QR images in `assets/community/qr.png` and `assets/community/agentwork-qr.png`. Preserve their scan quality and verify both desktop and mobile presentation after replacement.

The website's **社区共建** page provides the community QR code, submission routes, and verified code contributor links. Author and reviewer credits are added after names and roles are confirmed.

AIGC contribution directions include image and brand LoRA, image editing, video consistency and workflows, audio and music generation, and evaluation. These are open contribution directions; availability of completed chapters is shown in the book index.

---

## 中文说明

欢迎通过 Issue 反馈问题，或通过 Pull Request 提交范围清晰、可验证的改动。GitHub 阅读版位于 `content/chapters/*.md`；正文修改在 `content/source-html/*.html` 完成，随后运行 `python3 scripts/build-content.py` 同时生成 Markdown 和站点数据，并执行 `node scripts/check-site.mjs` 校验。请勿单独编辑生成的 Markdown。

请保持原稿内容、标题层级与段落顺序，正文勘误需附依据或作者确认。界面修复与内容编辑分开提交。配图、代码、公式及附件均需核对，禁止提交密钥、密码或隐私信息。

也可前往[魔搭开发者实践](https://modelscope.cn/spotlight)，选择「创建内容」，添加专题 **#魔搭紫皮书** 后投稿。署名与审校角色确认后再进入贡献者目录。

场景案例请提供任务与目标用户、运行环境、可复现步骤、效果验证与局限。MCP、Skill、LoRA 等通用技术教程归入对应阅读路径，案例可引用这些技术。
