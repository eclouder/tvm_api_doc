---
title: SplitCallTIRByPattern
description: TVM Relax 模块级转换 Pass，用于根据预定义模式拆分和重构 TIR 函数调用。
---

# SplitCallTIRByPattern

## 概述

`SplitCallTIRByPattern` 是一个 TVM Relax 模块级转换 Pass，其主要功能是根据预定义的 TIR 模式来拆分和重构 Relax 模块中的 TIR 函数调用。该 Pass 通过识别特定的计算模式，将复杂的 TIR 调用分解为多个更小的、更易于优化的子操作，从而为后续的优化和代码生成提供更好的基础。

## 函数签名

```cpp
Pass SplitCallTIRByPattern(ffi::Array<TIRPattern> patterns, FCodegen fcodegen)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `patterns` | `ffi::Array<TIRPattern>` | 预定义的 TIR 模式数组，用于匹配和拆分目标 TIR 函数调用。每个 `TIRPattern` 定义了要匹配的计算模式特征。 |
| `fcodegen` | `FCodegen` | 代码生成函数，负责为拆分后的新 TIR 函数生成相应的代码。该函数决定了如何将匹配的模式转换为实际的 TIR 函数实现。 |

## 实现原理

`SplitCallTIRByPattern` Pass 的核心实现基于以下步骤：

1. **模式匹配**：Pass 遍历 Relax 模块中的所有 TIR 函数调用，使用提供的 `patterns` 数组来识别符合特定计算模式的调用。

2. **调用拆分**：对于每个匹配的模式，Pass 会将原始的 TIR 函数调用拆分为多个更小的 TIR 函数调用。拆分策略由模式定义决定，可能包括：
   - 将复杂的算子分解为基本算子组合
   - 根据数据布局或计算维度进行分割
   - 提取可重用的计算子图

3. **代码生成**：使用 `fcodegen` 函数为拆分后产生的新 TIR 函数生成实际的实现代码。这个回调函数允许用户自定义如何将抽象的模式转换为具体的 TIR 函数。

4. **模块更新**：将原始模块中被拆分的 TIR 函数调用替换为新的函数调用序列，并添加新生成的 TIR 函数到模块中。

## 优化效果

该 Pass 带来的主要优化效果包括：

- **计算粒度优化**：将粗粒度的复杂算子拆分为细粒度的基本操作，便于后续的调度优化
- **内存访问优化**：通过拆分可以减少临时内存的使用，改善数据局部性
- **并行化机会**：细粒度的操作更容易进行并行化处理
- **目标适配**：可以根据不同硬件目标的特点进行定制化拆分

## 使用场景

`SplitCallTIRByPattern` Pass 适用于以下场景：

- **硬件特定优化**：针对特定加速器或硬件特性，将通用算子拆分为硬件友好的子操作
- **算子融合准备**：在算子融合之前，将复杂算子拆分为更适合融合的基本单元
- **内存层次优化**：根据内存层次结构特点拆分计算，优化数据移动
- **自定义扩展**：用户可以通过自定义模式来扩展 TVM 的优化能力

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import SplitCallTIRByPattern

# 定义自定义的 TIR 模式和代码生成函数
patterns = [
    # 示例：定义矩阵乘法拆分模式
    tir_pattern1,
    # 示例：定义卷积拆分模式  
    tir_pattern2
]

def custom_codegen(pattern, inputs, outputs):
    # 根据模式特征生成相应的 TIR 函数
    if pattern.name == "matmul_split":
        return generate_split_matmul_tir(inputs, outputs)
    elif pattern.name == "conv_split":
        return generate_split_conv_tir(inputs, outputs)

# 创建并应用 Pass
pass_obj = SplitCallTIRByPattern(patterns, custom_codegen)
mod_optimized = pass_obj(mod)
```

## 相关 Pass

- **FuseOps**：算子融合 Pass，与拆分 Pass 形成互补的优化方向
- **LegalizeOps**：算子合法化 Pass，将高级算子转换为目标支持的基本算子
- **AnnotateTIROpPattern**：TIR 算子模式标注 Pass，为拆分提供模式信息
- **MetaScheduleApplyDatabase**：应用元调度数据库，对拆分后的算子进行调度优化