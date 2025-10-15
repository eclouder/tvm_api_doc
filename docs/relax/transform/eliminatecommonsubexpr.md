---
title: EliminateCommonSubexpr
description: TVM Relax 的公共子表达式消除优化 Pass，用于识别和消除重复计算。
---

# EliminateCommonSubexpr

## 概述

`EliminateCommonSubexpr` 是 TVM Relax 中的一个函数级优化 Pass，主要用于消除计算图中的公共子表达式。该 Pass 能够识别程序中重复出现的相同计算模式，并将这些重复计算合并为单一计算，从而减少计算量和内存使用，提高程序执行效率。

在深度学习模型和计算图中，经常会出现多个地方使用相同输入进行相同计算的情况。通过消除这些公共子表达式，可以避免冗余计算，优化模型性能。

## 函数签名

```cpp
Pass EliminateCommonSubexpr(bool call_only)
```

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `call_only` | `bool` | 控制优化范围的标志参数：<br>- 如果为 `true`，则只对函数调用（Call）节点进行公共子表达式消除<br>- 如果为 `false`，则对所有类型的表达式节点进行优化 |

## 实现原理

`EliminateCommonSubexpr` Pass 的核心实现基于以下技术原理：

1. **表达式规范化**：首先对表达式进行规范化处理，确保结构相同但表示形式不同的表达式能够被正确识别为公共子表达式。

2. **哈希与比较**：使用高效的哈希算法为每个表达式生成唯一标识，通过比较哈希值来快速识别相同的表达式。

3. **表达式替换**：当发现多个相同的表达式时，保留第一个出现的表达式实例，将其余相同的表达式替换为对第一个实例的引用。

4. **作用域分析**：在适当的语法作用域内进行表达式匹配和替换，确保优化的正确性。

5. **调用节点优化**：当 `call_only` 参数为 `true` 时，Pass 会特别关注函数调用节点，因为这些节点通常包含计算密集的操作，消除它们的重复可以带来显著的性能提升。

## 优化效果

该 Pass 能够带来多方面的优化效果：

- **计算量减少**：消除重复计算，减少总的浮点运算次数
- **内存使用优化**：减少中间结果的存储需求
- **执行速度提升**：通过减少冗余计算来加速模型推理
- **代码精简**：生成更简洁、更易读的中间表示

## 使用场景

`EliminateCommonSubexpr` Pass 在以下场景中特别有用：

1. **模型优化流水线**：作为 TVM 优化流水线中的一个标准步骤
2. **包含重复计算的模型**：处理那些在多个分支或层中使用相同计算的模型
3. **计算密集型应用**：对性能要求较高的推理场景
4. **内存受限环境**：在嵌入式设备或移动设备上部署模型时

**使用时机建议**：
- 通常在算子融合和布局变换之后应用
- 在常量折叠之前应用可以获得更好的效果
- 对于包含大量重复计算的模型，建议启用该 Pass

## 示例代码

以下是在 TVM 中使用 `EliminateCommonSubexpr` Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建 IRModule
@relax.function
def example_function(x, y):
    # 假设这里有多个相同的计算表达式
    a1 = relax.op.add(x, y)
    a2 = relax.op.add(x, y)  # 与 a1 相同的表达式
    b1 = relax.op.multiply(a1, a2)
    return b1

mod = tvm.IRModule({"main": example_function})

# 应用 EliminateCommonSubexpr Pass
pass_obj = transform.EliminateCommonSubexpr(call_only=False)
optimized_mod = pass_obj(mod)

# 优化后，重复的 add 操作会被消除
print(optimized_mod)
```

## 相关 Pass

- **FoldConstant**：常量折叠 Pass，与公共子表达式消除协同工作
- **FuseOps**：算子融合 Pass，通常在公共子表达式消除之后应用
- **DeadCodeElimination**：死代码消除，可以清理因表达式替换而产生的无用代码
- **CanonicalizeBindings**：绑定规范化，为公共子表达式识别提供标准化的表达式形式

这些 Pass 通常组合使用，形成完整的优化流水线，共同提升模型性能。