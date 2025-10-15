---
title: CombineParallelMatmul
description: TVM Relax 中用于合并并行矩阵乘法操作的函数级优化 Pass。
---

# CombineParallelMatmul

## 概述

`CombineParallelMatmul` 是 TVM Relax 中的一个函数级变换 Pass，主要功能是识别并合并函数中可并行执行的矩阵乘法操作。通过将多个独立的矩阵乘法操作合并为单个批量矩阵乘法操作，该 Pass 能够减少内核启动开销，提高计算效率，特别适用于包含多个相似形状矩阵乘法的计算图。

## 函数签名

```cpp
Pass CombineParallelMatmul(FCheck check)
```

## 参数说明

- **check**: `FCheck` 类型参数
  - 功能：可选的自定义检查函数，用于确定哪些矩阵乘法操作可以被合并
  - 类型：函数指针或函数对象，接受操作参数并返回布尔值
  - 默认值：如果未提供，Pass 将使用默认的合并条件
  - 用途：允许用户根据特定需求定制合并策略

## 实现原理

该 Pass 的核心实现逻辑基于以下步骤：

1. **模式识别**：遍历计算图，识别所有矩阵乘法（matmul）操作节点
2. **兼容性分析**：分析矩阵乘法的输入形状、数据类型和计算模式，确定哪些操作可以合并
3. **依赖检查**：确保要合并的操作之间没有数据依赖关系，可以安全并行执行
4. **操作合并**：将多个独立的矩阵乘法合并为单个批量矩阵乘法操作
5. **结果分发**：将批量操作的结果重新分割为原始的输出格式

关键技术点包括：
- 使用 TVM 的模式匹配机制识别矩阵乘法操作
- 基于形状和类型推断确保合并的安全性
- 维护计算图的语义等价性

## 优化效果

使用 `CombineParallelMatmul` Pass 可以带来以下优化效果：

- **性能提升**：减少内核启动次数，提高 GPU/加速器利用率
- **内存优化**：合并操作可能减少中间结果的存储需求
- **计算效率**：利用批量矩阵乘法的硬件优化，提高计算吞吐量
- **开销减少**：降低调度和内核启动的系统开销

## 使用场景

该 Pass 适用于以下场景：

- **神经网络推理**：包含多个并行全连接层的模型
- **多头注意力**：Transformer 模型中的多头自注意力机制
- **并行分支**：计算图中存在多个并行执行的矩阵乘法分支
- **批量处理**：需要对多个独立输入进行相同矩阵乘法运算的场景

最佳使用时机：
- 在算子融合之前应用，为后续优化创造机会
- 在计算图包含多个相似形状的矩阵乘法时
- 在目标硬件支持高效批量矩阵乘法时

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建 Relax 模块
@relax.function
def example_model(x: relax.Tensor((1, 64), "float32"),
                  w1: relax.Tensor((64, 128), "float32"),
                  w2: relax.Tensor((64, 128), "float32")):
    # 两个并行的矩阵乘法
    out1 = relax.op.matmul(x, w1)
    out2 = relax.op.matmul(x, w2)
    return relax.op.concat([out1, out2], axis=1)

# 应用 CombineParallelMatmul Pass
mod = tvm.IRModule({"main": example_model})
pass_seq = transform.Sequential([
    transform.CombineParallelMatmul()
])
optimized_mod = pass_seq(mod)

# 优化后的计算图将合并两个 matmul 操作
```

## 相关 Pass

- **FuseOps**：算子融合 Pass，可与本 Pass 配合进一步优化计算图
- **OperatorFusion**：通用的算子融合优化
- **AlterOpLayout**：改变算子布局，可能影响矩阵乘法的合并机会
- **CanonicalizeBindings**：规范化绑定，为模式匹配创造更好的条件

## 注意事项

- 该 Pass 主要关注计算图中的并行矩阵乘法，对于串行或有复杂依赖的矩阵乘法可能不适用
- 合并决策依赖于形状推断的准确性，建议在完整的形状信息可用时应用此 Pass
- 自定义的 `check` 函数可以用于实现特定领域的合并策略