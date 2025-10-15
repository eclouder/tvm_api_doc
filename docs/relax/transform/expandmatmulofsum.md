---
title: ExpandMatmulOfSum
description: TVM Relax 变换 Pass，用于展开矩阵乘法中的求和操作以优化计算。
---

# ExpandMatmulOfSum

## 概述

`ExpandMatmulOfSum` 是一个 TVM Relax 函数级变换 Pass，主要功能是识别并展开矩阵乘法操作中的求和表达式。该 Pass 通过将复杂的矩阵乘法与求和组合操作分解为更简单的操作序列，使得后续的优化 Pass 能够更好地进行优化，从而提高计算效率。

## 函数签名

```cpp
Pass ExpandMatmulOfSum()
```

## 参数说明

此 Pass 没有显式参数，它作为一个无参数的函数 Pass 被创建和使用。

在内部实现中，Pass 接收以下参数：
- `Function func`: 需要变换的 Relax 函数
- `IRModule mod`: 包含该函数的 IR 模块
- `PassContext pc`: Pass 执行上下文，包含配置信息

## 实现原理

`ExpandMatmulOfSum` Pass 的核心实现基于模式匹配和重写机制：

1. **模式创建**：通过 `CreatePatterns(func)` 函数创建匹配模式，识别出矩阵乘法中包含求和操作的模式。

2. **模式匹配**：在函数中查找符合特定模式的矩阵乘法操作，特别是那些可以分解为更简单操作的复杂表达式。

3. **表达式重写**：使用 `RewriteCall(pattern, rewriter, func)` 将匹配到的复杂矩阵乘法表达式重写为等效但更简单的操作序列。

4. **函数级变换**：作为函数级 Pass，它逐个处理模块中的每个函数，确保所有相关的矩阵乘法操作都被正确处理。

## 优化效果

该 Pass 的主要优化效果包括：

- **计算简化**：将复杂的矩阵乘法表达式分解为基本操作，便于后续优化
- **内存访问优化**：通过分解操作，可能减少中间结果的存储需求
- **并行化机会**：简单的操作序列更容易被调度器并行化
- **融合优化**：为后续的操作融合 Pass 创造更好的条件

## 使用场景

`ExpandMatmulOfSum` Pass 适用于以下场景：

- **深度学习模型优化**：在处理包含复杂矩阵运算的神经网络模型时
- **线性代数计算**：优化涉及矩阵乘法和求和组合的科学计算应用
- **编译优化流水线**：作为 TVM 优化流水线中的早期变换步骤
- **性能调优**：当发现矩阵乘法操作成为性能瓶颈时

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import ExpandMatmulOfSum

# 创建 IRModule
mod = tvm.IRModule({})

# 应用 ExpandMatmulOfSum Pass
mod = ExpandMatmulOfSum()(mod)

# 或者作为优化流水线的一部分
seq = tvm.transform.Sequential([
    ExpandMatmulOfSum(),
    # 其他优化 Pass...
])
mod = seq(mod)
```

## 相关 Pass

- **FuseOps**：操作融合 Pass，将简单操作融合为更复杂的核函数
- **SimplifyExpr**：表达式简化 Pass，简化复杂的算术表达式
- **CanonicalizeBindings**：规范化绑定 Pass，标准化变量绑定
- **EliminateCommonSubexpr**：消除公共子表达式 Pass，减少冗余计算

这些 Pass 通常与 `ExpandMatmulOfSum` 配合使用，共同构成 TVM Relax 的完整优化流水线。