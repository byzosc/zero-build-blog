---
title: 我用一台 VPS 把服务边界做清楚：入口、部署、监控和云账号安全
date: 2026-07-05
summary: 这不是一篇“躲风控”教程，而是一套更稳的 VPS 用法：让云主机承担真实、可审计、可恢复的边缘控制面，把公网入口、SSH 授权、部署、健康检查、NAS 桥接和备份都收拢起来。
wechat_url:
tags: [VPS, 自托管, DevOps, 云安全, Docker]
---

<!-- 中文版。English: index.md（站内点语言按钮切换）。 -->

# 我用一台 VPS 把服务边界做清楚：入口、部署、监控和云账号安全

![一台 VPS 作为个人基础设施的边缘控制面](cover.png)

## 开头

我最近越来越觉得，一台小 VPS 最有价值的地方，不是“便宜算力”，也不是“随便开个公网 IP”。

它真正厉害的地方是：**把一堆原本散落在家里、NAS、GitHub、Cloudflare、Tailscale 和本地电脑上的入口，收拢成一个边界清楚、能部署、能观测、能回滚的控制面。**

也先把最容易误解的话说在前面：这不是一篇教你“躲 Cloud 扫描”或者规避平台规则的文章。恰好相反，我觉得长期可用的做法是：

> 不伪装，不滥用，不裸奔。让 VPS 承担真实用途，把访问面收窄，把日志和备份做好，让故障能恢复。

Cloud 平台真正害怕的，往往不是你写了一篇文章，而是账号行为看起来像滥用：乱扫、乱发、资源空转、裸露管理面板、没有真实服务、被入侵后还继续跑。VPS 的正确用法，是把自己从这些风险画像里拿出来。

---

## 1. 问题不是“我有没有一台服务器”，而是边界太乱

一个小团队或个人项目跑起来以后，很快会遇到这些问题：

- 家里的 NAS 适合放数据，但不适合直接暴露到公网。
- 本地电脑有密钥，但不能把私钥复制到每台新机器。
- GitHub 上 main 分支更新了，但生产机怎么更新、怎么回滚，不能靠临场手感。
- 管理面板、监控、健康页、应用 API、公网入口，最好各有边界。
- 云厂商会关注资源是否长期空转，安全团队也会关注异常行为；你需要的是“真实使用 + 可解释”，不是“刷存在感”。

这时候 VPS 不应该只是“另一台 Linux”。它应该变成一个**边缘枢纽**。

![VPS 边缘枢纽架构](images/edge-architecture.png)

我的目标是把它分成四条清晰的路：

1. **公网访问**：只让需要公开的服务走 Cloudflare Tunnel / Access 之类的入口。
2. **私有管理**：SSH、Portainer、Cockpit、内部状态页走 Tailscale 这类私网。
3. **部署路径**：GitHub 对齐、打包、备份、覆盖、重启、验证，每一步可重复。
4. **NAS 桥接**：NAS 继续做大容量存储，VPS 只做入口、轻服务、监控和桥接任务，不把 NAS 管理面板裸露出去。

## 2. 第一原则：公网入口尽量少，管理入口尽量私有

很多事故不是服务本身多复杂，而是入口开太多了。

我的基本规则很土，但有效：

- 管理面板不裸露公网。
- 能走 Tailnet 的都走 Tailnet。
- 真要给公网访问，就先过 Access，再进隧道，再到服务。
- VPS 防火墙和反代只放行“真的要被访问”的路径。
- 默认不为图方便开一堆 `0.0.0.0:<port>`。

Cloudflare Tunnel 的好处是，`cloudflared` 从你的机器**主动连出去**，公网用户从 Cloudflare 入口进来，VPS 不需要直接暴露一串入站端口。Tailscale SSH 的好处是，SSH 认证可以和 Tailnet 身份绑定起来，管理路径天然更窄。

这不是为了“藏”。这是为了把攻击面变小。

## 3. 第二原则：密钥永远按方向走，别复制私钥

这次部署前有个很典型的小插曲：新机器要连 VPS，但 VPS 还不认识它。

错误做法是：把已经有权限那台电脑上的 VPS 私钥复制过去。

正确做法是：让新机器自己生成一对密钥，然后把**新机器的公钥**追加到 VPS 的 `authorized_keys`。

也就是这个方向：

```text
新机器私钥留在新机器
新机器公钥 -> VPS ~/.ssh/authorized_keys
```

不要反过来：

```text
旧机器私钥 -> 到处复制
```

这件事看起来很小，但它决定了权限能不能被收束。私钥一旦被复制，你后面就很难回答“到底哪台机器有生产权限”。公钥授权则简单得多：谁有权限，`authorized_keys` 里看得到；要撤销，删那一行。

## 4. 第三原则：部署不是“传文件”，部署是一个 runbook

我现在尽量不把生产机部署理解成“scp 一下”。真正要做的是一套固定动作：

![VPS 后端部署流程](images/deploy-runbook.png)

这套流程里，每一步都有目的：

1. **对齐 main**：确认 GitHub 上的 `main` 指向目标提交，不在生产机上猜代码版本。
2. **只打包变更范围**：这次只改后端，就只打包 `backend`；前端没改，不重新 build。
3. **先盘点现场**：看当前容器、端口、timer、反代，避免把不相关服务碰坏。
4. **备份旧目录**：比如先备份旧的 `backend/app/`，带时间戳保存。
5. **覆盖新代码**：只覆盖目标目录，不顺手重构生产机。
6. **重启目标容器**：只重启需要更新的服务。
7. **验证端点**：`/health`、新增 API、公网入口都要跑一遍。
8. **确认周边没坏**：NAS 桥接 timer、监控、隧道、其它栈都要看一眼。

一个简化版的部署骨架大概长这样：

```bash
# 本地：打包目标范围
git archive --format=tar HEAD backend | gzip > backend.tar.gz

# VPS：先备份
ssh vps '
  ts=$(date +%Y%m%d-%H%M%S)
  mkdir -p /opt/backups/myapp/$ts
  cp -a /opt/stacks/myapp/backend/app /opt/backups/myapp/$ts/app
'

# 上传并解包
scp backend.tar.gz vps:/tmp/backend.tar.gz
ssh vps '
  mkdir -p /opt/stacks/myapp/release
  tar -xzf /tmp/backend.tar.gz -C /opt/stacks/myapp/release
  rsync -a --delete /opt/stacks/myapp/release/backend/ /opt/stacks/myapp/backend/
  docker compose -f /opt/stacks/myapp/docker-compose.yml restart backend
'

# 验证
curl -fsS https://example.com/health
curl -fsS https://example.com/api/example
```

真正的生产脚本可以更严谨，但思路就是这样：**先能回滚，再敢部署。**

## 5. 第四原则：云账号安全不是“刷活跃”，而是真实用途 + 可恢复

很多人担心云厂商把资源回收、限制甚至误判，于是第一反应是“要不要制造一点流量”。我不建议这样想。

以 OCI Always Free 为例，官方文档明确说明，长期低利用率的 Always Free 计算资源可能被回收。这个规则背后的意思不是“你要刷假流量”，而是：免费资源应该承载真实用途；如果它对你重要，就应该做好备份和可重建。

我更喜欢用这几个指标判断一台 VPS 是否健康：

- 它有真实服务：入口、健康页、监控、部署目标、桥接任务。
- 它有真实日志：什么时候健康检查、什么时候重启、什么时候部署。
- 它有最小暴露面：公网只暴露必要入口，管理面走私网或 Access。
- 它有备份：配置、数据、关键容器卷、数据库，都能恢复。
- 它有文档：下一次换机器，可以照手册重建。

这比“为了不空闲而空转”靠谱得多。后者很容易变成浪费，甚至更像异常行为。

## 6. 我最终留下的 VPS 清单

如果从零搭一台，我会按这个顺序做：

1. **系统基线**：更新系统，装 Docker、`ufw` / `nftables`、`jq`、`htop`、`ncdu`、备份工具。
2. **私网入口**：接入 Tailscale，只把管理入口放在 Tailnet。
3. **SSH 授权**：每台设备独立密钥；只追加公钥，不复制私钥。
4. **目录约定**：`/opt/stacks` 放 Compose，`/opt/data` 放服务数据，`/opt/backups` 放备份。
5. **公网入口**：用 Tunnel / Access / 反代暴露真正要公开的服务。
6. **健康页**：至少有 `/health` 和一个机器状态 JSON。
7. **监控**：Uptime Kuma / Glances / cron health check，任选轻量组合。
8. **部署 runbook**：备份、覆盖、重启、验证、回滚写成固定步骤。
9. **重建文档**：真实 token、密钥不进仓库；但目录、命令、服务边界要写清楚。

这里最重要的是最后一条：**秘密不进仓库，流程必须进仓库。**

## 7. 一台小 VPS 的正确定位

我现在更愿意把 VPS 看成一个“合规边缘控制面”，而不是一台随便折腾的云机器：

- 它不替代 NAS，只承担入口和轻服务。
- 它不替代 GitHub，只承接部署。
- 它不替代安全产品，但能把管理入口收窄。
- 它不保证云资源永远不被回收，但能让你的服务可解释、可备份、可迁移。

这一套的价值，不在某个命令多高级，而在边界终于清楚了：

> 公网从哪里进，管理从哪里进，代码怎么更新，旧版怎么回滚，服务怎么证明自己活着，数据坏了怎么恢复。

这些问题一旦被回答，VPS 就不只是“有公网 IP 的 Linux”了。它变成了你整个小型基础设施里最稳的那块边界。

## 参考

- [Oracle Cloud Infrastructure: Always Free Resources](https://docs.oracle.com/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Cloudflare Tunnel documentation](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/)
- [Cloudflare Access application paths and policies](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/self-hosted-apps/)
- [Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh)
