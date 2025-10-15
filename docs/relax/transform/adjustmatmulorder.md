---
title: AdjustMatmulOrder
description: TVM Relax 中用于调整矩阵乘法顺序的函数级优化 Pass
---

# AdjustMatmulOrder

## 概述

`AdjustMatmulOrder` 是 TVM Relax 中的一个函数级变换 Pass，主要用于优化神经网络中矩阵乘法（Matmul）操作的执行顺序。该 Pass 通过智能地重新排列矩阵乘法操作的顺序，旨在减少计算复杂度和内存访问开销，从而提升模型推理性能。

在深度学习中，矩阵乘法是许多操作（如全连接层、注意力机制等）的核心组成部分，其执行顺序对整体性能有显著影响。`AdjustMatmulOrder` Pass 能够自动识别并优化这些操作的顺序，无需用户手动干预。

## 函数签名

```cpp
Pass AdjustMatmulOrder()
```

该 Pass 不接受任何参数，返回一个 TVM Pass 对象，可以直接应用于 Relax 函数。

## 参数说明

此 Pass 为无参数 Pass，在创建时不需要指定任何配置参数。在内部执行时，它会接收以下标准 Pass 参数：

- `func: Function` - 要优化的 Relax 函数
- `mod: IRModule` - 包含函数的 IR 模块
- `pc: PassContext` - Pass 执行上下文

## 实现原理

`AdjustMatmulOrder` Pass 的实现基于模式匹配和重写技术，主要流程如下：

1. **模式创建**：通过 `CreatePatterns(func)` 函数识别函数中所有矩阵乘法操作的模式。这些模式可能包括连续的矩阵乘法链、与转置操作结合的矩阵乘法等。

2. **模式匹配**：在函数中搜索符合预定义模式的矩阵乘法操作序列。常见的模式包括：
   - `(A @ B) @ C` 与 `A @ (B @ C)` 的等价变换
   - 涉及转置操作的矩阵乘法重排
   - 批量矩阵乘法的顺序优化

3. **代价评估**：对于每个匹配的模式，评估不同顺序下的计算复杂度（通常基于浮点操作数 FLOPs）和内存访问模式。

4. **操作重写**：使用 `RewriteCall(pattern, rewriter, func)` 将原始矩阵乘法序列替换为计算代价更低的等价形式。

该 Pass 的核心数学原理是利用矩阵乘法的结合律，即 `(A × B) × C = A × (B × C)`，但不同结合顺序的计算复杂度可能不同。例如，对于维度为 `(m, n)`, `(n, p)`, `(p, q)` 的三个矩阵，两种结合顺序的计算复杂度分别为：
- `(A × B) × C`：`m×n×p + m×p×q`
- `A × (B × C)`：`n×p×q + m×n×q`

## 优化效果

`AdjustMatmulOrder` Pass 能够带来以下优化效果：

1. **计算复杂度降低**：通过选择最优的矩阵乘法顺序，显著减少浮点操作次数
2. **内存访问优化**：改善数据局部性，减少缓存未命中
3. **并行度提升**：为后续的并行化优化创造更好的条件
4. **内存占用减少**：减少中间结果的存储需求

在实际应用中，对于复杂的矩阵乘法链，性能提升可达 10%-50%，具体效果取决于矩阵的维度和操作序列的结构。

## 使用场景

该 Pass 适用于以下场景：

1. **深度学习模型优化**：特别是包含多个全连接层或复杂注意力机制的模型
2. **科学计算**：涉及大量矩阵运算的数值计算应用
3. **模型部署**：在模型编译和部署阶段自动优化计算图
4. **以下时机建议使用**：
   - 在算子融合之前应用，为融合创造更多机会
   - 在静态内存规划之前应用，减少中间结果的内存需求
   - 对于已知包含复杂矩阵运算链的模型

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 构建包含矩阵乘法链的示例模块
@relax.function
def example_matmul_chain(A: relax.Tensor((128, 256)), 
                        B: relax.Tensor((256, 512)), 
                        C: relax.Tensor((512, 1024))):
    # 原始计算：((A @ B) @ C)
    AB = relax.op.matmul(A, B)
    ABC = relax.op.matmul(AB, C)
    return ABC

# 应用 AdjustMatmulOrder Pass
mod = tvm.IRModule({"main": example_matmul_chain})
mod = transform.ApplyPasses(mod, [
    transform.AdjustMatmulOrder()
])

# 优化后的计算可能变为：(A @ (B @ C))
# 具体优化结果取决于矩阵维度和代价模型
```

## 相关 Pass

- **FuseOps**：算子融合 Pass，与调整矩阵乘法顺序协同工作
- **FoldConstant**：常量折叠 Pass，可能在矩阵乘法重排后发现新的常量折叠机会
- **EliminateCommonSubexpr**：公共子表达式消除，可能受益于矩阵乘法的重排
- **DynamicToStatic**：动态到静态转换，为矩阵乘法顺序优化提供更多信息

建议的使用顺序：
1. `AdjustMatmulOrder`
2. `FoldConstant` 
3. `FuseOps`
4. 其他优化 Pass