---
title: "Is Hand-Keyframing Dead? MotionHub Brings AI Into After Effects"
short_title: "Is Hand-Keyframing Dead?"
date: 2026-07-16
summary: Describe motion on the right and get editable AE layers and keyframes on the left. MotionHub is turning that AI workflow into shared, extensible infrastructure.
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

The demo puts cause and effect in one frame: a motion description is entered on the right, while the corresponding animation appears from an empty canvas on the left. The left-side motion is a real 240-frame, 60fps render of the current `Comp 4`. The panel and execution states are an explicitly labeled demonstration composite of the intended interaction, not a claim that the full one-click loop is finished.

![MotionPilot running inside After Effects](ae-motionpilot.png)

## Why the plugin is the important part

Without MotionPilot, an AI can still produce a one-off JSX script. But every new effect risks rebuilding layer lookup, AE API calls, JSON transport, permissions, undo handling, and error reporting. A script that runs once is not the same as a capability that can be reused reliably.

| Without the plugin | With MotionPilot |
| --- | --- |
| Start each effect from another JSX file | Solve scene I/O, execution, feedback, and undo once |
| Ask the LLM to guess intent and AE internals | Let the LLM interpret; let a deterministic executor apply |
| Debug failures across scripts, AE, and transport | Trace failures to a command and layer |
| Finish once, then rewrite next time | Add a motion primitive once and reuse it |

The plugin is not merely a shortcut. It is shared infrastructure for AI to operate After Effects, keeping the fragile engineering stable while people and models focus on timing, hierarchy, and taste.

## Why I plan to open-source it under MIT

The exciting part is compounding capability. One contributor can add a keyframe strategy, another an effect or expression, and another a test project or failure case. Every person and every AI can then reuse that vocabulary.

I plan to release the first-party plugin code under MIT and keep iterating on the execution contract, motion strategies, aesthetic constraints, and safe rollback. **The repository has not completed its license transition yet, so this is the plan, not a claim that the conversion is already done.** Third-party code will retain its original notices and licenses.

The destination is not “generate this one flower.” It is an extensible loop:

> Send an image, GIF, or video -> AI decomposes structure and timing -> MotionPilot writes editable AE -> a human refines it

Today, MotionHub cannot promise that every motion reference will work on the first try. But every reliable execution primitive means the next attempt no longer starts from zero.

## What works now, and what comes next

Both ends already work as prototypes. MotionSheet can inspect and export motion handoff data. MotionPilot can read an AE scene, generate a plan, execute supported operations, and return to the normal AE editing workflow. In the launch video, the left side is a real AE result and the right side is a clearly labeled composite of the intended panel interaction.

The honest boundary: **the two products are not yet a one-click closed loop.** The next milestone is a shared motion contract so MotionSheet output can become MotionPilot input without re-describing timing, easing, hierarchy, or layer intent.

That is what MotionHub means to me:

> Designers can explain motion. Developers can reproduce it. After Effects can execute it.

## Try the projects

- [MotionSheet live demo](https://zerb.cc.cd/)
- [MotionSheet on GitHub](https://github.com/zerbLion/keyframe_sheet)
- [MotionPilot on GitHub](https://github.com/zerbLion/motion-design)

The vertical social demo, real AE source clip, and platform-ready copy are included with this post's source assets.
