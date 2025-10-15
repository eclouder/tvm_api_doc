---
title: TopologicalSort
description: TVM Relax 中的拓扑排序转换 Pass，用于对函数中的绑定块进行拓扑排序。
---

# TopologicalSort

## 概述

`TopologicalSort` 是一个 TVM Relax 的函数级转换 Pass，主要用于对 Relax 函数中的绑定块（Binding Blocks）进行拓扑排序。该 Pass 通过重新组织绑定块的顺序，确保数据流依赖关系得到正确维护，从而提高后续优化的效果和代码的可读性。

## 函数签名

```cpp
Pass TopologicalSort(TraversalOrder order, StartingLocation starting_location)
```

## 参数说明

### `order` : TraversalOrder
- **类型**: `TraversalOrder` 枚举
- **描述**: 指定拓扑排序的遍历顺序，决定绑定块的排列方式。
- **可选值**:
  - `TraversalOrder::PostOrder`: 后序遍历
  - `TraversalOrder::PreOrder`: 前序遍历
  - `TraversalOrder::DFS`: 深度优先搜索顺序

### `starting_location` : StartingLocation
- **类型**: `StartingLocation` 枚举  
- **描述**: 指定拓扑排序的起始位置，决定从哪个绑定块开始排序。
- **可选值**:
  - `StartingLocation::Start`: 从起始绑定块开始
  - `StartingLocation::End`: 从末尾绑定块开始
  - `StartingLocation::Both`: 从两端同时开始

## 实现原理

`TopologicalSort` Pass 的核心实现基于以下步骤：

1. **依赖分析**: 分析 Relax 函数中所有绑定块之间的数据依赖关系，构建依赖图。

2. **拓扑排序**: 根据指定的遍历顺序（`order`）和起始位置（`starting_location`），对依赖图进行拓扑排序。

3. **块重排**: 按照拓扑排序的结果重新排列绑定块的顺序，确保：
   - 被依赖的绑定块出现在依赖它的绑定块之前
   - 保持原有的语义等价性

4. **函数重构**: 使用重新排序后的绑定块构建新的 Relax 函数。

实现中使用了 `TopologicalSorter` 类来执行具体的排序操作，通过访问者模式遍历 IR 并重构绑定块序列。

## 优化效果

应用 `TopologicalSort` Pass 可以带来以下优化效果：

- **提高可读性**: 使绑定块的排列更加符合数据流顺序，便于开发者理解和调试
- **优化后续 Pass**: 为后续的优化 Pass（如常量折叠、死代码消除等）提供更好的输入结构
- **提升编译效率**: 有序的绑定块布局可以减少编译过程中的分析开销

## 使用场景

`TopologicalSort` Pass 在以下场景中特别有用：

1. **IR 规范化**: 在优化流程的早期阶段，用于规范化 IR 结构
2. **调试和分析**: 当需要分析数据依赖关系时，排序后的绑定块更容易跟踪
3. **优化前置**: 作为其他优化 Pass 的前置步骤，确保输入 IR 具有良好的结构

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import TopologicalSort

# 创建 Relax 模块
mod = tvm.IRModule()

# 应用 TopologicalSort Pass
# 使用深度优先搜索顺序，从起始位置开始排序
pass_config = {
    "order": "DFS",
    "starting_location": "Start"
}
sorted_mod = TopologicalSort(pass_config["order"], pass_config["starting_location"])(mod)

# 或者使用预定义的配置
sorted_mod = relax.transform.TopologicalSort(
    relax.transform.TraversalOrder.DFS,
    relax.transform.StartingLocation.Start
)(mod)
```

## 相关 Pass

- **`DeadCodeElimination`**: 死代码消除，拓扑排序后的 IR 有助于更有效地识别死代码
- **`ConstantFolding`**: 常量折叠，排序后的绑定块可以更早地暴露常量计算机会
- **`FuseOps`**: 算子融合，良好的绑定块顺序有助于识别可融合的算子模式
- **`CanonicalizeBindings`**: 绑定规范化，与拓扑排序协同工作以优化 IR 结构

该 Pass 通常作为 Relax 优化流水线中的早期步骤，为后续更复杂的优化提供结构良好的输入。