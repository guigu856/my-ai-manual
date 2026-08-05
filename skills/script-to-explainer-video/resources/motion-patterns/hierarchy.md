---
id: hierarchy
name: 层级展开
version: 1.0.0
---

# 层级展开

## 适用语义

用于总体与局部、系统与模块、类别与子类、抽象层级逐步展开。

## 不适用

- 纯时间顺序
- 双方案比较
- 回流循环

## 对象模型

- root
- groups
- children
- selected_path

## 空间结构

可使用：

- 树状展开
- 嵌套容器
- 分层堆叠
- 从中心向外的模块化展开

层级深度超过三层时，应分 Scene 逐层解释，不在单屏展示完整树。

## 推荐状态链

```text
ROOT
→ FIRST_LEVEL
→ GROUP_RELATIONS
→ SELECTED_BRANCH
→ SECOND_LEVEL
→ HIERARCHY_HOLD
```

## 主要事件

- reveal
- expand
- connect
- focus-path
- collapse-siblings

## 连续性

下一 Scene 深入某个分支时，保留选中节点的位置或通过镜头推进建立连续性；其他兄弟节点降权或退出。

## 风险

- 把流程误画成层级
- 节点数量过多
- 父子关系和并列关系混淆
- 嵌套容器导致文字空间不足
- 选中路径不明确

## 验收

- 每个节点能否指出其父级
- 同层节点是否使用一致视觉语法
- 进入下一层时观众是否知道当前位于哪里
- 未讲解分支是否适当降权
