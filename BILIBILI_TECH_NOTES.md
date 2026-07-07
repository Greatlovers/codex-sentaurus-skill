# 开源一个 Sentaurus + Codex 自动化 Skill：Workbench-first、低 token 监控和 mesh-first 收敛调试

最近在调 Sentaurus/TCAD 仿真时，我把自己常用的一套流程整理成了一个 Codex skill，并做了公开安全打包。

这个 skill 的目标不是替代 Sentaurus Workbench，而是让 Codex 在 Workbench 项目体系内自动完成一些重复但很耗时间的工作：查节点、看依赖、提交仿真、监测状态、定位收敛失败，并尽量从网格和结构本身去修复问题。

## 核心设计

### Workbench-first

项目状态以 Sentaurus Workbench 为准。节点依赖、`gtree.dat`、`gexec.cmd`、`.sta`、结果目录都保留在 Workbench 体系里。Codex 只负责辅助操作，不绕开 Workbench 硬改生成文件。

### 低 token 监控

长时间仿真不让 Codex 一直轮询日志。提交任务后，用外部 watcher 监测 `.sta` 状态，Codex heartbeat 只检查一个很小的 terminal marker。没有终态就直接退出，不读日志、不 SSH、不分析，尽量减少 token 消耗。

### Mesh-first 收敛修复

遇到 SDevice 数值收敛失败时，默认优先看 `*_des_min.tdr` 和上游 SDE 源文件，把失败热点映射到具体几何区域和网格定义。优先改 SDE 网格和局部结构，而不是无脑缩小 `MinStep`、放松收敛或者堆迭代次数。

### 官方案例引导

如果需要判断网格怎么改，会优先找相近的 Sentaurus 官方案例，比如 trench、IGBT、LDMOS、power diode 等结构，然后参考官方 `.cmd` / `.par` 里的网格策略。

### 可选 GitHub handoff

外部 GPT handoff 默认关闭。如果需要，也可以用 GitHub 做文件中转，把失败节点的诊断文件交给外部模型生成完整替换版 `.cmd`。不过这部分需要私有仓库和额外配置。

## 公开打包说明

这次公开包已经做了脱敏处理：不包含 VM IP、本机路径、私有 handoff 状态、仿真结果、Sentaurus 官方文件、license、官方索引大文件等内容。公开版主要保留 skill 逻辑、辅助脚本、技术说明和可本地重建索引的脚本。

## 适用场景

- Sentaurus Workbench 项目节点比较多，需要自动查状态和按依赖提交；
- SDevice 经常因为局部网格/结构问题不收敛；
- 想把 TCAD 调参经验固化成可复用的工程流程；
- 希望 Codex 少读大日志，用更低 token 成本监控长时间仿真。
