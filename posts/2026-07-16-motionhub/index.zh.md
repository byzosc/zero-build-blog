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

> **一句话：** MotionSpec 定规范，MotionPilot 把意图写回 AE，MotionSheet 用同一规范交付与走查。三个工具合起来，就是 MotionHub。

标题说得狠一点，事实说得克制一点：AI 还没有替代动效师的审美，但它已经不只是在“帮你 K 几帧”。我把三个工具放到一起后，才意识到它正在进入一条可编辑、可约束、可走查的专业生产链。

它不是再生成一段无法修改的黑盒视频，而是把结构、计划和结果留在正常的设计工作流里。

| 组成 | 负责什么 | 产出 |
| --- | --- | --- |
| MotionSpec | 定义曲线、时长和命名预设 | 共享 `motion-tokens.json` |
| MotionPilot | 在 AE 内理解并执行动效意图 | 可编辑图层、关键帧、效果和表达式 |
| MotionSheet | 读取 Lottie / Bodymovin JSON | 图层、时间轴、交接表和规范走查 |
| MotionHub | 把定义、生成与走查接起来 | 一份规范贯穿的动效工作流 |

## MotionSpec：把规范写成系统

MotionSpec 把公司动效规范从散落的文档和个人经验，变成一份可共享的 `motion-tokens.json`。曲线、时长与命名预设都能可视化编辑；MotionPilot 和 MotionSheet 读取同一份规范。

![MotionSpec 真实页面](motionspec.png)

## MotionSheet：读懂动效

MotionSheet 在浏览器本地读取 JSON，不上传源文件。它把关键帧、时间、曲线、动作分组和父子关系转成开发能读的交接表，也能在时间轴上定位具体是哪个图层在动。

![MotionSheet 时间轴与图层定位](motionsheet-demo.gif)

## MotionPilot：把意图写回 AE

MotionPilot 运行在 After Effects 面板里。它结合选中图层、可选画面信息和 LLM 生成动效计划，再由确定性的 JSX 执行器落到 AE。

重点不是“生成一段视频”，而是生成后仍然能继续改：图层、关键帧、效果和表达式都留在正常的 AE 工作流里。

上面的演示直接使用真实 AE 屏幕录制：右侧在 MotionPilot 输入“8 瓣发光花环向中心旋转收拢成圆，再反向展开；节奏放慢 2x”并点击 Generate，随后左侧合成和时间轴出现真实写入的图层与关键帧。片中只把 API 等待段做了明确标注的压缩跳时，生成过程与结果保持原速；后半段则是 MotionSheet 真实页面对动效数据进行预览、定位和交付。为了说明它不是针对单个案例写死，后段还切换到第二份 JSON，展示另一组图层在时间轴、详情和 Table 视图之间的完整检查流程。

![MotionPilot 在 After Effects 内运行](motionpilot-demo.gif)

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

三个部分都已经有可以工作的页面或原型：

- MotionSpec 已能编辑并导出共享动效规范。
- MotionSheet 已能解析、检查和导出动效交接数据。
- MotionPilot 已能读取 AE 场景、生成计划并执行受支持的动效操作。
- 演示片使用 MotionPilot 的真实 AE 面板和执行结果；API 等待段有明确标注的压缩跳时，MotionSheet 段为两份 JSON 的真实页面操作。

也不吹牛：**目前还不是“一键闭环”。** 下一步要补的是完整 handoff 导入桥，让 MotionSheet 的结构化结果可以直接成为 MotionPilot 的输入，同时继续受同一份 `motion-tokens.json` 约束，不再重复描述时间、缓动、层级和图层意图。

这就是 MotionHub 想解决的事：

> 设计能解释，开发能复现，AE 能执行。

## 体验与源码

- [MotionSheet 在线体验](https://zerb.cc.cd/)
- [MotionPilot 页面](https://zerb.cc.cd/pilot)
- [MotionSheet GitHub](https://github.com/zerbLion/keyframe_sheet)
- [MotionPilot GitHub](https://github.com/zerbLion/motion-design)

本篇源码目录同时附带横版演示、竖版演示、真实 AE 动画源片和各平台可直接发布的短文案。
