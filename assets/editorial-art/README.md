# 黑色手绘与魔搭紫点缀

使用 https://github.com/HalfAI1102/anthropic-art 的 skill/SKILL.md 与 references/style-spec.md，读取该仓库的三张风格参考。

用户覆盖：白色页面底，黑色手绘为主，彩色仅为极少量魔搭紫 #624AFF，不采用 Skill 默认的大面积彩色背景。无搭搭或其他人物。

提示词核心：Anthropic editorial illustration language; thick near-black #141413 irregular gestural strokes, rounded ends, deliberate asymmetry, sparse symbolic objects, flat ivory #FAF9F5 shapes inside object silhouettes, pure white #FFFFFF outer canvas. Only one tiny ModelScope purple #624AFF detail per icon, less than 1% of canvas. No gradients, shadows, 3D, text or mascot. 4:3 landscape, centered cluster with generous white margins.

主题及点缀：
- seedling：书本新芽／小书签
- mountain：山峰／顶峰小旗
- cubes：积木／连接点
- photo：照片／小太阳
- documents：文档对话／三个小点
- voice：声波／末尾短波段
- campaign：图片视频／播放三角
- palette：画笔颜料盘／一滴颜料和笔尖
- phone：手机拍照巡检／底部小指示点
- poster：教学海报纸张／顶部小图钉

真实任务库统一使用内置 image_gen 生成的 PNG，以同目录现有任务图作为风格参考；不要混用平滑几何 SVG。新增任务图须同时核对主题、缩略图辨识度、粗黑手绘笔触和留白。

原始生成文件保留在 Codex generated_images；上版纯黑细线图保留于 assets/line-art。
