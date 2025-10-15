---
title: MergeCompositeFunctions
description: TVM Relax 中用于合并复合函数的模块级优化 Pass。
---

# MergeCompositeFunctions

## 概述

`MergeCompositeFunctions` 是一个 TVM Relax 的模块级优化 Pass，主要功能是合并 IRModule 中的复合函数。该 Pass 通过识别和合并具有相同计算模式的函数，减少模块中的函数数量，从而优化模型的计算图结构，提高后续优化的效率。

## 函数签名

```cpp
Pass MergeCompositeFunctions()
```

**返回值：**
- `Pass`：返回一个 TVM Pass 对象，该 Pass 可以在 IRModule 上执行复合函数合并操作。

## 参数说明

此 Pass 不接受任何显式参数，它通过 TVM 的 PassContext 来获取执行上下文信息。

## 实现原理

`MergeCompositeFunctions` Pass 的核心实现逻辑如下：

1. **模块遍历**：遍历输入 IRModule 中的所有函数
2. **函数分析**：分析每个函数的计算模式和数据流图结构
3. **模式匹配**：识别具有相同计算模式的函数，这些函数可能只是参数名称或中间变量名称不同，但计算逻辑相同
4. **函数合并**：将匹配到的相同函数合并为一个共享函数，并更新所有调用点
5. **结果返回**：返回优化后的新 IRModule

该 Pass 的实现基于 TVM 的模块 Pass 框架，通过 `CreateModulePass` 创建，优化级别为 0，表示这是一个基础优化 Pass。

## 优化效果

使用 `MergeCompositeFunctions` Pass 可以带来以下优化效果：

- **减少函数数量**：合并重复的函数定义，减少 IRModule 中的函数总数
- **降低内存占用**：减少重复的函数定义可以降低编译时内存使用
- **提高编译效率**：减少函数数量可以加速后续的优化 Pass 执行
- **优化代码生成**：为后续的代码生成阶段提供更简洁的 IR 表示

## 使用场景

`MergeCompositeFunctions` Pass 适用于以下场景：

- **模型优化流水线**：作为 TVM Relax 优化流水线的一部分，在函数规范化之后执行
- **重复函数消除**：当模型包含多个相同计算模式的函数时，用于消除冗余
- **子图融合准备**：在子图融合优化之前，先合并相同的函数模式
- **自定义算子优化**：对于用户自定义的复合函数，识别并合并相同的实现

## 示例代码

以下是如何在 TVM Relax 中使用 `MergeCompositeFunctions` Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建 IRModule
mod = tvm.IRModule({})

# 创建 MergeCompositeFunctions Pass
merge_pass = transform.MergeCompositeFunctions()

# 应用 Pass
optimized_mod = merge_pass(mod)

# 或者作为优化流水线的一部分
pipeline = transform.Sequential([
    transform.MergeCompositeFunctions(),
    # 其他优化 Pass...
])

optimized_mod = pipeline(mod)
```

## 相关 Pass

- **FuseOps**：操作符融合 Pass，将多个细粒度操作符合并为更大的复合函数
- **FoldConstant**：常量折叠 Pass，在编译时计算常量表达式
- **EliminateCommonSubexpr**：消除公共子表达式 Pass，识别并合并相同的计算表达式
- **CanonicalizeBindings**：规范化绑定 Pass，标准化 Relax 变量绑定形式

这些 Pass 通常与 `MergeCompositeFunctions` 配合使用，共同构成 TVM Relax 的完整优化流水线。