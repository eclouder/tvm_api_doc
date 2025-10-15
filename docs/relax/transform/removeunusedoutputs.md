---
title: RemoveUnusedOutputs Pass
description: 移除 Relax IRModule 中未使用的函数输出，减少不必要的计算和内存占用。
---

# RemoveUnusedOutputs Pass

## 概述

`RemoveUnusedOutputs` Pass 是一个用于优化 TVM Relax IRModule 的转换 Pass。其主要功能是识别并移除函数中未被使用的输出项，从而减少不必要的计算和内存分配，提高程序执行效率。

该 Pass 特别适用于处理返回元组的函数，当函数的某些输出在后续计算中未被使用时，可以安全地移除这些未使用的输出，简化计算图。

## 函数签名

```cpp
Pass RemoveUnusedOutputs()
```

**返回值：**
- `Pass`：一个 TVM Pass 对象，可以应用于 IRModule

## 参数说明

该 Pass 函数不接受任何参数，是一个无参的工厂函数，返回一个可执行的 Pass 对象。

## 实现原理

`RemoveUnusedOutputs` Pass 的核心实现基于以下步骤：

### 1. 收集使用信息
使用 `PartialTupleUsageCollector::Collect(mod)` 遍历整个 IRModule，收集每个函数输出的使用情况。该收集器会分析所有函数调用点，确定哪些输出项被实际使用。

### 2. 构建使用掩码
对于每个函数，生成一个布尔掩码（usage mask），其中每个元素对应函数的一个输出：
- `true` 表示该输出被使用
- `false` 表示该输出未被使用

### 3. 更新被调用函数
对于每个需要优化的函数：
- 根据使用掩码重构函数体，移除未使用的输出
- 创建新的函数签名，只包含被使用的输出
- 在 IRModule 中添加优化后的函数版本

### 4. 更新调用点
对于所有调用被优化函数的调用点：
- 将调用目标从原函数重定向到优化后的函数
- 保持参数不变，但输出结构信息相应更新

### 5. 验证一致性
在更新过程中进行严格的验证：
- 确保调用点与函数定义匹配
- 验证输出数量与使用掩码长度一致
- 检查结构信息的一致性

## 优化效果

该 Pass 带来的主要优化效果包括：

1. **计算量减少**：移除未使用的输出意味着相关的计算可以被消除
2. **内存占用降低**：减少不必要的中间结果存储
3. **执行效率提升**：简化计算图，减少数据传输
4. **代码简化**：生成更简洁的 IR，便于后续优化

## 使用场景

`RemoveUnusedOutputs` Pass 适用于以下场景：

### 典型应用场景
- **多输出模型**：如目标检测模型同时输出边界框和分类得分
- **中间结果丰富**的函数调用链
- **条件分支**导致部分输出未被使用的情况
- **模型蒸馏**或**子图提取**后的优化

### 使用时机
建议在以下阶段应用该 Pass：
- 在主要的图优化 Pass 之后
- 在算子融合之前
- 在代码生成之前

## 示例代码

以下是一个使用 `RemoveUnusedOutputs` Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建一个包含多输出函数的 IRModule
@relax.expr.function
def multi_output_func(x: relax.Tensor((1, 3, 224, 224), "float32")):
    # 假设这个函数返回三个输出
    output1 = relax.op.nn.conv2d(x, ...)
    output2 = relax.op.nn.relu(output1)
    output3 = relax.op.nn.max_pool2d(output2)
    return (output1, output2, output3)

# 构建 IRModule
mod = tvm.IRModule({
    "main": multi_output_func
})

# 应用 RemoveUnusedOutputs Pass
seq = tvm.transform.Sequential([
    transform.RemoveUnusedOutputs(),
    # 其他优化 Pass...
])

optimized_mod = seq(mod)
```

在这个例子中，如果后续计算只使用了 `output3`，那么 `RemoveUnusedOutputs` Pass 会移除 `output1` 和 `output2` 的计算。

## 相关 Pass

### 互补 Pass
- **DeadCodeElimination**：移除完全未被使用的函数和变量
- **FuseOps**：算子融合，可与本 Pass 协同优化
- **SimplifyInference**：推理简化，处理类似的冗余计算

### 依赖关系
该 Pass 通常作为优化流水线的一部分，建议在以下 Pass 之后使用：
- 主要的图优化 Pass
- 常量折叠 Pass
- 公共子表达式消除 Pass

### 注意事项
- 该 Pass 主要处理函数级别的输出优化
- 对于算子级别的冗余消除，建议结合其他优化 Pass
- 在训练场景中需谨慎使用，确保不会影响梯度计算