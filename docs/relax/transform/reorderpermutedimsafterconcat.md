---
title: ReorderPermuteDimsAfterConcat
description: TVM Relax 转换 Pass，用于优化 concat 操作后的 permute_dims 操作顺序
---

# ReorderPermuteDimsAfterConcat

## 概述

`ReorderPermuteDimsAfterConcat` 是一个 TVM Relax 的函数级转换 Pass，主要功能是优化计算图中 `concat` 操作后接 `permute_dims` 操作的执行顺序。该 Pass 通过重新排列操作顺序，减少不必要的张量转置操作，从而提高计算效率。

## 函数签名

```cpp
Pass ReorderPermuteDimsAfterConcat()
```

**返回值：**
- `Pass`：返回一个 TVM Relax 的转换 Pass 对象

## 参数说明

该 Pass 没有显式参数，但在内部执行时会接收以下参数：

- `func`：`Function` - 要转换的 Relax 函数
- `mod`：`IRModule` - 包含函数的 IR 模块
- `pc`：`PassContext` - Pass 执行上下文，包含配置信息

## 实现原理

该 Pass 的核心实现基于模式匹配和重写机制：

1. **模式创建**：使用 `CreatePatterns()` 函数创建匹配模式，识别 `concat` 后接 `permute_dims` 的操作序列
2. **模式匹配**：在计算图中查找符合该模式的操作序列
3. **操作重排**：通过 `RewriteCall()` 函数将 `permute_dims` 操作提前到 `concat` 操作之前，对每个输入张量分别进行转置
4. **等价转换**：确保转换前后的计算语义完全等价

**转换前：**
```
input1 → concat → permute_dims → output
input2 ↗
```

**转换后：**
```
input1 → permute_dims → concat → output
input2 → permute_dims ↗
```

## 优化效果

该 Pass 带来的主要优化效果包括：

1. **减少内存占用**：避免在 concat 操作后产生大的中间转置张量
2. **提高计算效率**：对较小的输入张量分别转置，通常比对大张量转置更高效
3. **优化内存访问**：改善数据局部性，减少缓存未命中
4. **启用后续优化**：为其他基于模式匹配的优化 Pass 创造更多机会

## 使用场景

该 Pass 适用于以下场景：

1. **计算机视觉模型**：在包含通道拼接（channel concatenation）和维度重排的模型中
2. **自然语言处理**：在多头注意力机制中涉及张量拼接和转置的操作
3. **模型融合优化**：作为模型优化流水线的一部分，与其他转换 Pass 配合使用
4. **张量布局优化**：需要优化内存布局和张量形状变换的场景

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import ReorderPermuteDimsAfterConcat

# 创建 IRModule
@relax.expr_functor
def example_model():
    # 假设有 concat 后接 permute_dims 的模式
    # Pass 会自动识别并优化
    pass

# 应用 Pass
mod = example_model()
mod_optimized = ReorderPermuteDimsAfterConcat()(mod)
```

## 相关 Pass

- **FuseOps**：操作融合 Pass，可与本 Pass 配合进一步优化计算图
- **EliminateCommonSubexpr**：公共子表达式消除，处理重复的转置操作
- **CanonicalizeBindings**：规范化绑定，清理优化后的 IR
- **FoldConstant**：常量折叠，优化常量张量的转置操作

该 Pass 通常在 TVM Relax 的优化流水线中较早执行，为后续的融合和优化创造有利条件。