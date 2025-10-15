---
title: ReorderTakeAfterMatmul
description: TVM Relax 转换 Pass，用于将 Take 操作重新排序到矩阵乘法操作之后。
---

# ReorderTakeAfterMatmul

## 概述

`ReorderTakeAfterMatmul` 是一个 TVM Relax 函数级别的转换 Pass，主要功能是重新排列计算图中 `Take` 操作和矩阵乘法（Matmul）操作的执行顺序。该 Pass 通过识别特定的计算模式，将原本在矩阵乘法之前执行的 `Take` 操作重新排序到矩阵乘法之后执行，从而优化计算效率。

## 函数签名

```cpp
Pass ReorderTakeAfterMatmul()
```

## 参数说明

此 Pass 不接受任何显式参数，它是一个无参数的函数 Pass。

## 实现原理

`ReorderTakeAfterMatmul` Pass 的实现基于 TVM 的图重写机制，主要步骤如下：

1. **模式创建**：通过 `CreatePatterns()` 函数创建需要匹配的计算图模式，该模式识别 `Take` 操作紧接在矩阵乘法操作之前的计算子图。

2. **图重写**：使用 `RewriteCall()` 函数对匹配到的计算子图进行重写，将 `Take` 操作从矩阵乘法的输入位置移动到输出位置。

3. **函数转换**：Pass 作为一个函数级别的转换，遍历 IRModule 中的每个函数，应用上述重写规则。

核心实现代码：
```cpp
auto pass_func = [=](Function func, IRModule mod, PassContext pc) {
  auto [pattern, rewriter] = CreatePatterns();
  return RewriteCall(pattern, rewriter, func);
};
return CreateFunctionPass(pass_func, 1, "ReorderTakeAfterMatmul", {});
```

## 优化效果

该 Pass 的主要优化效果包括：

1. **计算效率提升**：通过减少中间结果的存储和传输，降低内存访问开销
2. **内存优化**：避免在矩阵乘法之前创建大型的索引选择结果，减少临时内存分配
3. **并行化机会**：矩阵乘法操作通常具有更好的并行化特性，先执行矩阵乘法可以提供更多的优化机会

## 使用场景

`ReorderTakeAfterMatmul` Pass 适用于以下场景：

1. **深度学习模型**：在处理包含嵌入层查找后接全连接层的模型时特别有效
2. **推荐系统**：推荐系统中常见的特征查找和矩阵运算组合
3. **自然语言处理**：词嵌入查找后接变换层的模型结构

建议在以下时机使用该 Pass：
- 在计算图优化阶段的早期应用
- 当模型中出现 `Take` 操作紧接矩阵乘法操作的模式时
- 在内存受限的设备上部署模型时

## 示例代码

以下是一个使用该 Pass 的示例：

```python
import tvm
from tvm import relax

# 创建 IRModule
mod = tvm.ir.IRModule()

# 应用 ReorderTakeAfterMatmul Pass
seq = tvm.transform.Sequential([
    relax.transform.RewriteDataflowReshape(),
    relax.transform.ReorderTakeAfterMatmul(),
    relax.transform.FoldConstant()
])
optimized_mod = seq(mod)
```

## 相关 Pass

- **FoldConstant**：常量折叠 Pass，可以进一步优化重排序后的计算图
- **RewriteDataflowReshape**：数据流重整形 Pass，通常在该 Pass 之前使用
- **FuseOps**：操作融合 Pass，可以在重排序后进一步融合相关操作
- **DeadCodeElimination**：死代码消除 Pass，用于清理重排序后产生的无用代码

该 Pass 通常作为 TVM Relax 优化管道的一部分，与其他 Pass 协同工作以获得最佳性能。