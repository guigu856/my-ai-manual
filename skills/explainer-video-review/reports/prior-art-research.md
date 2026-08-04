# Prior-Art Research

## Scope

本次 redesign 针对“已有成片的证据化审查”，不把生产 Skill、参考视频学习和通用媒体工具混成同一职责。查询时间：2026-08-05。

Catalog 结果：4 组查询均成功，`skills.sh` 与 SkillsMP 均返回结果，共 55 个候选 family。安装数和 stars 仅是发现线索，不是质量评分。

## 重点来源

1. [OpenMontage Agent Guide](https://github.com/calesthio/OpenMontage/blob/4eab34c5cfcccaa4f1970554928feccce73ee930/AGENT_GUIDE.md)
   - 机制：先做 pipeline/preflight，再执行阶段化工作，并保留 checkpoint 和 self-review。
   - 采用：把媒体清单、审查基准、证据 gate 和修复闭环放在审查前置流程。
   - 排除：其完整生产编排、provider 菜单和项目看板超出本 Skill 的审查边界。

2. [Microsoft ResearchStudio paper2video Skill](https://github.com/microsoft/ResearchStudio/blob/88c08f176d945fa33dad21957d3c1cd6d6443051/ResearchStudio-Reel/skills/paper2video/SKILL.md)
   - 机制：严格的视频包 QA、保留实际渲染帧、绑定音频/字幕/视觉 cue 的 canonical timeline，以及失败后的根因修复循环。
   - 采用：报告使用媒体指纹、证据类型、时间轴定位和“修复源文件后整片重渲染”。
   - 排除：其 PPTX、SVG、paper2video 专用工具链不进入本 Skill。

3. [BaoCut Agent Skill](https://github.com/JimLiu/baocut/blob/ceb22e61aa2f9e9391b8859918fb3d763931f132/skills/baocut/SKILL.md)
   - 机制：清晰的 job routing、参考文档按任务加载、版本/坐标系契约、可恢复的审计与修复语义。
   - 采用：把输入类型、审查档位、报告输出和 repair handoff 明确化。
   - 排除：BaoCut CLI、转录编辑和 macOS 应用依赖不适用于本 Skill。

4. [iart-ai Explainer Video Skill](https://github.com/iart-ai/explainer-video-skills/blob/3e2d411b725d9a72939cf8e5eb81579e751373e7/skills/explainer-video/SKILL.md)
   - 机制：显式触发示例、脚本到屏幕的阶段边界、输出契约和 rendered-still 检查。
   - 采用：保留四维审查与生产 Skill 的清楚 handoff。
   - 排除：其面向新视频创作的 storyboard/scene pipeline 不复制到 post-render audit。

## Keep / Adapt / Reject / Invent

- **Keep**：阶段化 gate、基于实际媒体的证据、canonical 时间轴、根因修复后整片复渲、显式路由和恢复条件。
- **Adapt**：把“逐帧”改成 quick/standard/dense 三档确定性采样；把审计输出统一成 status/severity/confidence/evidence/finding。
- **Reject**：默认要求用户逐维度确认、把某一工具链写成硬依赖、用单帧推断连续性或音画同步、删除整个任务目录。
- **Invent**：`review-manifest.json`、`review-report.json` 契约、`missing_evidence` 边界、四维 finding ID 和与生产 Skill 对应的复审协议。

## Missing Evidence

- 候选目录没有提供与本仓库完全同构的中文概念动效 post-render reviewer，因此四维规则仍来自本仓库原始 Skill 的领域约束。
- 当前只有结构性 fixture 和脚本测试，尚无真实 MP4 provider render、逐帧播放记录或人审结果。
