---
title: FoldConstant
description: TVM Relax 中的常量折叠优化 Pass，用于在编译时计算常量表达式。
---

# FoldConstant

## 概述

FoldConstant 是 TVM Relax 中的一个函数级变换 Pass，主要功能是执行常量折叠优化。该 Pass 会在编译时识别并计算那些可以在编译阶段确定值的表达式，将计算结果替换为常量值，从而减少运行时的计算开销。

常量折叠是编译器优化中的经典技术，通过提前计算常量表达式，可以简化计算图、减少操作节点数量，并可能为后续优化创造更多机会。

## 函数签名

```cpp
Pass FoldConstant()
```

## 参数说明

该 Pass 不接受任何显式参数，它是一个无参数的工厂函数，返回一个配置好的 FunctionPass 对象。

## 实现原理

FoldConstant Pass 的核心实现基于 `ConstantFolder::Fold` 方法，其主要工作原理如下：

1. **表达式遍历**：通过访问者模式遍历 Relax 函数中的所有表达式
2. **常量识别**：识别包含常量操作数的表达式
3. **编译时计算**：在编译时执行这些表达式的计算
4. **结果替换**：将计算结果替换为新的常量节点

具体实现代码：
```cpp
Pass FoldConstant() {
  auto pass_func = [=](Function f, IRModule m, PassContext pc) {
    return ConstantFolder::Fold(f, m);
  };
  return CreateFunctionPass(pass_func, 0, "FoldConstant", {});
}
```

## 优化效果

应用 FoldConstant Pass 可以带来以下优化效果：

- **计算简化**：减少运行时的计算操作数量
- **内存优化**：消除中间计算结果的内存分配
- **图简化**：简化计算图结构，为后续优化提供更好的基础
- **性能提升**：通过减少运行时计算提升执行效率

## 使用场景

FoldConstant Pass 适用于以下场景：

1. **模型编译优化**：在模型编译流程的早期阶段应用
2. **常量表达式优化**：处理包含大量常量计算的模型
3. **图简化准备**：在为其他优化 Pass 准备简化计算图时
4. **静态形状计算**：在需要计算静态形状信息的场景中

建议在以下时机使用该 Pass：
- 在算子融合之前应用，以简化融合模式
- 在内存优化之前应用，以减少内存分配
- 在代码生成之前应用，以生成更简洁的代码

## 示例代码

以下是在 TVM 中使用 FoldConstant Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建 IRModule
@relax.expr.function
def example_function(x: relax.TensorStructInfo):
    # 包含常量计算的表达式
    const_a = relax.const(2.0, dtype="float32")
    const_b = relax.const(3.0, dtype="float32")
    add_result = relax.add(const_a, const_b)  # 这个加法可以在编译时计算
    return relax.multiply(x, add_result)

# 应用 FoldConstant Pass
mod = tvm.IRModule({"main": example_function})
mod = transform.FoldConstant()(mod)

# 经过优化后，add_result 将被替换为常量 5.0
```

## 相关 Pass

- **DeadCodeElimination**：死代码消除，可以清理常量折叠后不再使用的节点
- **FuseOps**：算子融合，常量折叠后的简化图更有利于融合优化
- **CanonicalizeBindings**：规范化绑定，与常量折叠协同优化计算图
- **StaticPlanBlockMemory**：静态内存规划，受益于常量折叠带来的内存优化

这些 Pass 通常组合使用，形成完整的优化流水线，以获得最佳的优化效果。