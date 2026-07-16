---
title: "手K动效已死？AI 正在接管 AE：MotionHub 首次公开"
short_title: "手K动效已死？AI 正在接管 AE"
date: 2026-07-16
summary: 我把 MotionSheet 和 MotionPilot 接成了 MotionHub：AI 先读懂动效规范，再把文字意图写回 After Effects 的可编辑图层与关键帧。
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

上面的演示不是截图推拉：AE 段来自当前工程 `Comp 4` 的 240 帧、60fps 实际渲染，并重新放回真实 AE 界面中展示编辑环境。

![MotionPilot 在 After Effects 内运行](ae-motionpilot.png)

## 现在做到哪一步

两端都已经有可工作的原型：

- MotionSheet 已能解析、检查和导出动效交接数据。
- MotionPilot 已能读取 AE 场景、生成计划并执行受支持的动效操作。
- 演示片使用的都是当前真实界面和当前 AE 工程结果。

也不吹牛：**目前还不是“一键闭环”。** 下一步要做的是统一 motion contract，让 MotionSheet 的结构化结果可以直接成为 MotionPilot 的输入，不再重复描述时间、缓动、层级和图层意图。

这就是 MotionHub 想解决的事：

> 设计能解释，开发能复现，AE 能执行。

## 体验与源码

- [MotionSheet 在线体验](https://zerb.cc.cd/)
- [MotionSheet GitHub](https://github.com/zerbLion/keyframe_sheet)
- [MotionPilot GitHub](https://github.com/zerbLion/motion-design)

本篇源码目录同时附带横版演示、竖版演示、真实 AE 动画源片和各平台可直接发布的短文案。
