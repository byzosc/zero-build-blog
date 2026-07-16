---
title: "Is Hand-Keyframing Dead? MotionHub Brings AI Into After Effects"
short_title: "Is Hand-Keyframing Dead?"
date: 2026-07-16
summary: MotionHub connects MotionSheet and MotionPilot so AI can read motion structure, plan from intent, and write editable layers and keyframes back into After Effects.
wechat_url:
tags: [motion-design, after-effects, lottie, ai, tools]
lang: en
translations: [zh]
---

# Is Hand-Keyframing Dead? AI Is Moving Into After Effects

![MotionHub combines MotionSheet and MotionPilot](cover.png)

<video controls playsinline preload="metadata" poster="cover.png">
  <source src="motionhub-demo.mp4" type="video/mp4">
</video>

> **In one sentence:** MotionSheet explains existing motion; MotionPilot turns new intent into editable work inside After Effects. Together, they form MotionHub.

The headline is aggressive; the claim is deliberately narrower. AI has not replaced a motion designer's taste, but it can already take over a growing amount of repetitive execution. MotionHub is the workflow connecting two projects I was already building.

The goal is not another black-box generated clip. Structure, planning, and the result all stay inside a normal design workflow.

| Part | Job | Output |
| --- | --- | --- |
| MotionSheet | Read Lottie / Bodymovin data | Layers, timing, curves, hierarchy, handoff table |
| MotionPilot | Plan and execute motion in AE | Editable layers, keyframes, effects, and expressions |
| MotionHub | Connect both directions | A shared motion contract from analysis to execution |

## MotionSheet: read motion

MotionSheet runs in the browser and reads JSON locally. It turns animation data into a developer-readable table, adds timeline inspection, and keeps parent-child motion visible instead of flattening it into a vague duration.

![MotionSheet timeline and layer inspection](motionsheet-demo.gif)

## MotionPilot: write motion

MotionPilot lives inside After Effects. It combines selected-layer context, optional visual context, an LLM-generated plan, and deterministic JSX execution. The result remains editable in AE; it is not a rendered black-box clip.

The demo above no longer fakes the AE section with screenshot zooms. Its AE motion comes from a real 240-frame, 60fps render of the current `Comp 4`, composited back into the actual AE interface to preserve the editing context.

![MotionPilot running inside After Effects](ae-motionpilot.png)

## What works now, and what comes next

Both ends already work as prototypes. MotionSheet can inspect and export motion handoff data. MotionPilot can read an AE scene, generate a plan, execute supported operations, and return to the normal AE editing workflow.

The honest boundary: **the two products are not yet a one-click closed loop.** The next milestone is a shared motion contract so MotionSheet output can become MotionPilot input without re-describing timing, easing, hierarchy, or layer intent.

That is what MotionHub means to me:

> Designers can explain motion. Developers can reproduce it. After Effects can execute it.

## Try the projects

- [MotionSheet live demo](https://zerb.cc.cd/)
- [MotionSheet on GitHub](https://github.com/zerbLion/keyframe_sheet)
- [MotionPilot on GitHub](https://github.com/zerbLion/motion-design)

The vertical social demo, real AE source clip, and platform-ready copy are included with this post's source assets.
