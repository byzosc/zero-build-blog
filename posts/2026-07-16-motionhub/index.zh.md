---
title: "手K动效已死？AI 正在接管 AE：MotionHub 首次公开"
short_title: "手K动效已死？AI 正在接管 AE"
date: 2026-07-16
summary: 右边写一句动效描述，左边得到可继续编辑的 AE 图层与关键帧。MotionHub 正在把这条 AI 动效链路做成可复用、可扩展的公共底座。
wechat_url:
tags: [动效设计, After Effects, Lottie, AI, 工具]
---

# 手K动效已死？AI 正在接管 AE

![MotionHub 由 MotionSheet 和 MotionPilot 组成](cover.png)

<video controls playsinline preload="metadata" poster="cover.png">
  <source src="motionhub-demo.mp4" type="video/mp4">
</video>

> **一句话：** MotionSheet 负责读懂已有动效，MotionPilot 负责把新的动效意图落到 AE 里，两者合起来就是 MotionHub。

标题说得狠一点，事实说得克制一点：AI 还没有替代动效师的审美，但它已经可以接管大量重复的执行工作。我最近把两个项目放到一起看，才发现它们其实是同一条链路的两端。这个完整方向，我把它叫做 **MotionHub**。

它不是再生成一段无法修改的黑盒视频，而是把结构、计划和结果留在正常的设计工作流里。

| 组成 | 负责什么 | 产出 |
| --- | --- | --- |
| MotionSheet | 读取 Lottie / Bodymovin JSON | 图层、时间、曲线、层级和交接表 |
| MotionPilot | 在 AE 内理解并执行动效意图 | 可编辑图层、关键帧、效果和表达式 |
| MotionHub | 把“读”和“写”接起来 | 从分析、规范到执行的共同协议 |

## MotionSheet：读懂动效

MotionSheet 在浏览器本地读取 JSON，不上传源文件。它把关键帧、时间、曲线、动作分组和父子关系转成开发能读的交接表，也能在时间轴上定位具体是哪个图层在动。

![MotionSheet 时间轴与图层定位](motionsheet-demo.gif)

## MotionPilot：把意图写回 AE

MotionPilot 运行在 After Effects 面板里。它结合选中图层、可选画面信息和 LLM 生成动效计划，再由确定性的 JSX 执行器落到 AE。

重点不是“生成一段视频”，而是生成后仍然能继续改：图层、关键帧、效果和表达式都留在正常的 AE 工作流里。

上面的演示直接使用真实 AE 屏幕录制：右侧在 MotionPilot 输入“8 瓣发光花环向中心旋转收拢成圆，再反向展开；节奏放慢 2x”并点击 Generate，随后左侧合成和时间轴出现真实写入的图层与关键帧。片中只把 API 等待段做了明确标注的压缩跳时，生成过程与结果保持原速；后半段则是 MotionSheet 真实页面对同一类动效数据进行预览、定位和交付。

![MotionPilot 在 After Effects 内运行](ae-motionpilot.png)

## 为什么插件才是关键

没有 MotionPilot，AI 当然也能临时写一段 JSX。但每做一种动效，都可能重新处理图层索引、AE API、JSON 转义、权限、撤销和错误回传。脚本能跑一次，不等于能力能稳定复用。

| 没有插件 | 有 MotionPilot |
| --- | --- |
| 每个动效从一份新 JSX 开始 | 场景读取、执行、回传与撤销只解决一次 |
| LLM 同时猜意图和 AE 实现细节 | LLM 负责理解，确定性执行器负责落地 |
| 错误散落在脚本、AE 和通信链路中 | 错误能定位到具体指令和图层 |
| 这次做完，下次大概率重写 | 新增一种 motion primitive，之后持续复用 |

所以插件不是一个“替你点按钮”的小工具，而是 **AI 操作 AE 的公共底座**。它把最容易出错的工程部分固定下来，让人和模型把时间花在节奏、层级与审美上。

## 为什么准备 MIT 开源

这件事最让人兴奋的地方，不是我一个人能做多少动效，而是能力可以累积：有人补一种关键帧策略，有人补一种效果或表达式，有人贡献测试工程和失败样本，下一次所有人和所有 AI 都能直接复用。

我准备把自有插件代码转为 MIT 开源，并持续迭代执行协议、动效策略、审美约束和安全回滚。**目前仓库尚未完成正式许可证切换，因此这里说的是开源计划，不是已经完成的状态。** 第三方代码仍保留各自的许可证和署名。

最终想做的不是“自动生成这朵花”，而是这条可扩展链路：

> 发来参考图、GIF 或视频 -> AI 拆解结构与节奏 -> MotionPilot 写入可编辑 AE -> 人继续精修

今天还不能保证“任何动效都一次成功”。但每增加一个可靠的执行能力，下一次就不必从头手搓。这才是 MotionHub 可以不断变强的原因。

## 现在做到哪一步

两端都已经有可工作的原型：

- MotionSheet 已能解析、检查和导出动效交接数据。
- MotionPilot 已能读取 AE 场景、生成计划并执行受支持的动效操作。
- 演示片使用 MotionPilot 的真实 AE 面板和执行结果；API 等待段有明确标注的压缩跳时，MotionSheet 段为真实页面操作。

也不吹牛：**目前还不是“一键闭环”。** 下一步要做的是统一 motion contract，让 MotionSheet 的结构化结果可以直接成为 MotionPilot 的输入，不再重复描述时间、缓动、层级和图层意图。

这就是 MotionHub 想解决的事：

> 设计能解释，开发能复现，AE 能执行。

## 体验与源码

- [MotionSheet 在线体验](https://zerb.cc.cd/)
- [MotionSheet GitHub](https://github.com/zerbLion/keyframe_sheet)
- [MotionPilot GitHub](https://github.com/zerbLion/motion-design)

本篇源码目录同时附带横版演示、竖版演示、真实 AE 动画源片和各平台可直接发布的短文案。
