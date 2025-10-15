---
title: ComputePrimValue Pass
description: TVM Relax 模块级转换 Pass，用于计算和替换函数中的原始值表达式。
---

# ComputePrimValue Pass

## 概述

`ComputePrimValue` 是一个 TVM Relax 模块级转换 Pass，其主要功能是遍历 IRModule 中的所有函数，计算并替换其中的原始值（PrimValue）表达式。该 Pass 通过将可计算的 PrimValue 表达式替换为具体的常量值，简化 IR 表示，为后续优化和代码生成阶段提供更简洁的中间表示。

## 函数签名

```cpp
Pass ComputePrimValue()
```

该 Pass 不接受任何参数，返回一个配置好的模块级 Pass 对象。

## 参数说明

此 Pass 没有直接参数，但在内部执行时会接收以下隐式参数：

- `IRModule mod`：输入的 IR 模块，包含需要优化的函数
- `PassContext pc`：Pass 执行上下文，包含配置选项和诊断信息

## 实现原理

`ComputePrimValue` Pass 的核心实现基于访问者模式，主要步骤如下：

1. **初始化注入器**：创建 `PrimValueComputeInjector` 实例，该注入器负责遍历和转换函数中的表达式。

2. **遍历函数**：对 IRModule 中的每个函数进行遍历：
   - 检查函数是否为 `Function` 类型
   - 使用注入器对函数进行转换，计算其中的 PrimValue 表达式
   - 如果函数被修改，将更新后的函数添加到更新集合中

3. **应用更新**：如果检测到函数被修改：
   - 创建模块的写时复制副本
   - 将更新后的函数应用到模块中
   - 调用注入器的 `Finalize` 方法完成最终处理

4. **返回结果**：返回处理后的 IRModule

## 优化效果

该 Pass 的主要优化效果包括：

- **简化 IR 结构**：将复杂的 PrimValue 表达式替换为简单的常量值
- **减少运行时开销**：在编译时完成计算，避免运行时重复计算
- **提高后续优化效果**：为常量传播、死代码消除等后续优化提供更好的基础
- **提升代码生成质量**：生成更简洁高效的目标代码

## 使用场景

`ComputePrimValue` Pass 适用于以下场景：

- **编译优化管道**：作为标准优化管道的一部分，在早期阶段执行
- **常量表达式优化**：当 IR 中包含大量可计算的 PrimValue 表达式时
- **张量形状计算**：在处理动态形状计算时，简化形状相关的表达式
- **性能敏感应用**：对运行时性能要求较高的应用场景

## 示例代码

```python
import tvm
from tvm import relax

# 创建原始 IRModule
@relax.function
def example_func(x: relax.Tensor((16, 32), "float32")):
    # 假设有可计算的 PrimValue 表达式
    shape_value = relax.PrimValue(16 * 32)  # 可计算为 512
    return x

mod = tvm.IRModule({"main": example_func})

# 应用 ComputePrimValue Pass
mod_optimized = relax.transform.ComputePrimValue()(mod)

# 优化后的模块中，PrimValue 表达式将被计算为常量值
```

## 相关 Pass

- **ConstantFolding**：常量折叠 Pass，处理更一般的常量表达式优化
- **DeadCodeElimination**：死代码消除 Pass，可移除因 PrimValue 计算而变得无用的代码
- **CanonicalizeBindings**：规范化绑定 Pass，清理和优化变量绑定
- **FuseOps**：算子融合 Pass，在简化表达式后进行更有效的算子融合

该 Pass 通常作为 TVM Relax 优化管道中的早期阶段 Pass，为后续更复杂的优化奠定基础。