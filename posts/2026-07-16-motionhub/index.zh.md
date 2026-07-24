---
title: "动效设计最危险的一刻：AI 开始接管从规范到交付的整条链路"
short_title: "AI 开始接管整条动效链路"
date: 2026-07-16
summary: MotionSpec 定规范、MotionPilot 在 AE 生成、MotionSheet 交付与走查；一份 motion-tokens.json 开始贯穿可编辑的动效生产链。
wechat_url:
tags: [动效设计, After Effects, Lottie, AI, 工具]
---

# 动效设计最危险的一刻：AI 开始接管整条动效链路

![MotionHub 动效生产链](cover.png)

<video controls playsinline preload="metadata" poster="cover.png">
  <source src="motionhub-demo.mp4" type="video/mp4">
</video>

![MotionHub 从 MotionSpec 到 MotionPilot 再到 MotionSheet](motionhub-system.png)

MotionSpec 定规范，MotionPilot 把意图写回 AE，MotionSheet 用同一份规范交付与走查。这三个工具是我做的，合起来叫 MotionHub，现在都挂在 [zerb.cc.cd](https://zerb.cc.cd/) 上。

标题起得狠，要说的事其实很克制：AI 还没有替代动效师的审美，但它确实已经不只是"帮你 K 几帧"。我把三个工具接在一起之后才看清，它正在进入一条可编辑、可约束、可走查的生产链——结构、计划和结果都留在正常的设计工作流里，而不是又生成一段改不了的黑盒视频。

## MotionSpec：把规范写成系统

MotionSpec 把公司动效规范从散落的文档和个人经验里捞出来，变成一份可共享的 `motion-tokens.json`。曲线、时长与命名预设都能可视化编辑，MotionPilot 和 MotionSheet 读的是同一份。

![MotionSpec 真实页面](motionspec.png)

## MotionSheet：读懂动效

MotionSheet 在浏览器本地读取 JSON，不上传源文件。它把关键帧、时间、曲线、动作分组和父子关系转成开发能读的交接表，也能在时间轴上点中一段动画，直接定位是哪个图层在动。

![MotionSheet 时间轴与图层定位](motionsheet-demo.gif)

## MotionPilot：把意图写回 AE

MotionPilot 跑在 After Effects 面板里。它读取选中图层和可选的画面信息，让 LLM 生成动效计划，再交给确定性的 JSX 执行器写进 AE。生成完不是终点：图层、关键帧、效果和表达式都留在正常的 AE 工程里，随时可以接着改。

上面的演示是真实 AE 录屏。我在右侧 MotionPilot 输入"8 瓣发光花环向中心旋转收拢成圆，再反向展开；节奏放慢 2x"，点 Generate，左侧合成和时间轴随后出现真实写入的图层与关键帧。片中只把等 API 的段落做了标注过的压缩跳时，生成过程与结果保持原速。后半段是 MotionSheet 真实页面对动效数据做预览、定位和交付；为了说明它不是对着单个案例写死的，还切了第二份 JSON，把另一组图层在时间轴、详情和 Table 视图之间完整查了一遍。

![MotionPilot 在 After Effects 内运行](motionpilot-demo.gif)

## 为什么插件才是关键

没有 MotionPilot，AI 当然也能临时写一段 JSX。但每做一种动效，都要重新处理一遍图层索引、AE API、JSON 转义、权限、撤销和错误回传。脚本跑通了一次，不代表这个能力下次还在——下次多半是重写。

MotionPilot 把这些最容易出错的工程问题固定下来：场景读取、执行、回传和撤销只解决一次；LLM 只负责理解意图，落地交给确定性执行器；出错能定位到具体指令和具体图层；每新增一种 motion primitive，之后一直复用。它不是一个"替你点按钮"的小工具，是 AI 操作 AE 的公共底座——人和模型的时间才能花在节奏、层级和审美上。

## 为什么准备 MIT 开源

一个人能做的动效有限，能力能累积才有意思：有人补一种关键帧策略，有人补一种效果或表达式，有人贡献测试工程和失败样本，下一次所有人和所有 AI 都直接复用。

我准备把自有插件代码转为 MIT 开源，持续迭代执行协议、动效策略、审美约束和安全回滚。目前仓库还没有完成正式的许可证切换，所以这里说的是开源计划，不是已完成的状态；第三方代码保留各自的许可证和署名。

最终想做的不是"自动生成这朵花"，而是这条能一直加长的链路：发来参考图、GIF 或视频，AI 拆解结构与节奏，MotionPilot 写入可编辑的 AE，人继续精修。今天还不能保证任何动效一次成功，但每多一个可靠的执行能力，下一次就不必从头手搓。

## 现在做到哪一步

三个部分都有能真实跑起来的页面或原型：

- MotionSpec 已能编辑并导出共享动效规范。
- MotionSheet 已能解析、检查和导出动效交接数据。
- MotionPilot 已能读取 AE 场景、生成计划并执行受支持的动效操作。
- 演示片用的是 MotionPilot 的真实 AE 面板和执行结果；API 等待段有明确标注的压缩跳时，MotionSheet 段是两份 JSON 的真实页面操作。

还没做到的也直说：目前不是"一键闭环"。下一步是补完整的 handoff 导入桥，让 MotionSheet 的结构化结果直接成为 MotionPilot 的输入，同时继续受同一份 `motion-tokens.json` 约束，不再重复描述时间、缓动、层级和图层意图。

到那一步，设计能解释、开发能复现、AE 能执行，这条链才算真正接上。

## 体验与源码

- [MotionHub 首页](https://zerb.cc.cd/)
- [MotionSheet 在线体验](https://zerb.cc.cd/app)
- [MotionSpec 规范编辑](https://zerb.cc.cd/tokens)
- [MotionPilot 页面](https://zerb.cc.cd/pilot)
- [MotionSheet GitHub](https://github.com/zerbLion/keyframe_sheet)
- [MotionPilot GitHub](https://github.com/zerbLion/motion-design)

本篇的源码目录里还放着横版和竖版完整演示、真实 AE 动画源片，以及各平台可直接发布的短文案。
