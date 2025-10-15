---
title: DeadCodeElimination
description: TVM Relax 的死代码消除优化 Pass，用于移除未被入口函数引用的冗余代码。
---

# DeadCodeElimination

## 概述

DeadCodeElimination（死代码消除）是 TVM Relax 中的一个模块级优化 Pass，其主要功能是识别并移除 IRModule 中未被任何入口函数直接或间接引用的函数和全局变量。通过消除这些"死代码"，可以显著减小编译后的模型大小，减少内存占用，并提高执行效率。

该 Pass 特别适用于在模型转换和优化过程中，清理因各种变换操作而产生的冗余函数定义。

## 函数签名

```cpp
Pass DeadCodeElimination(ffi::Array<ffi::String> entry_functions)
```

## 参数说明

- **entry_functions** (`ffi::Array<ffi::String>`)
  - 描述：指定作为入口点的函数名称数组。这些函数及其调用链中的函数将被保留，其他未被引用的函数将被视为死代码并移除。
  - 类型：ffi 字符串数组
  - 默认值：通常为空数组，表示使用模块中的所有外部可见函数作为入口点
  - 注意：如果数组为空，Pass 会自动将 IRModule 中所有具有外部链接属性的函数作为入口函数

## 实现原理

DeadCodeElimination Pass 的核心实现基于引用计数和可达性分析：

1. **入口函数收集**：首先确定分析的起点，即入口函数集合。如果用户提供了 `entry_functions` 参数，则使用指定的函数；否则收集所有外部可见的函数作为入口点。

2. **可达性分析**：从入口函数开始，进行深度优先或广度优先遍历，分析函数调用图。对于每个被访问的函数，递归分析其内部调用的其他函数。

3. **死代码识别**：在完整的调用图分析后，所有未被访问到的函数和全局变量都被标记为死代码。

4. **代码移除**：从 IRModule 中删除所有被标记为死代码的函数定义和全局变量。

5. **依赖关系维护**：确保在移除代码时不会破坏模块的结构完整性，保持有效的数据依赖关系。

## 优化效果

使用 DeadCodeElimination Pass 可以带来以下优化效果：

- **代码大小减少**：移除未使用的函数定义，显著减小编译后的二进制大小
- **内存占用降低**：减少运行时需要加载和管理的函数数量
- **编译时间优化**：后续的优化 Pass 需要处理的代码量减少，提高整体编译效率
- **执行性能提升**：避免加载和执行无用的代码，提高运行时性能

## 使用场景

DeadCodeElimination Pass 在以下场景中特别有用：

1. **模型转换后清理**：在完成模型格式转换（如从 PyTorch 到 Relax）后，移除转换过程中生成但实际未使用的辅助函数

2. **优化管道中间阶段**：在复杂的优化管道中，某些优化可能会使部分函数变得不可达，此时插入死代码消除可以清理冗余代码

3. **自定义算子集成**：当集成自定义算子时，可能会引入多个实现版本，通过死代码消除可以移除未被使用的版本

4. **模型剪枝后处理**：在模型权重剪枝后，相关的计算图可能发生变化，需要移除不再被引用的函数

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建 IRModule
mod = tvm.IRModule({
    "main": relax.Function([], relax.Call(relax.ExternFunc("external_func"), [])),
    "unused_func": relax.Function([], relax.const(1, "int32")),
    "helper_func": relax.Function([], relax.const(2, "int32"))
})

# 应用 DeadCodeElimination Pass
# 只保留 "main" 函数作为入口
passes = transform.DeadCodeElimination(["main"])
optimized_mod = passes(mod)

# 优化后，unused_func 和 helper_func 将被移除（如果未被 main 引用）
# 只剩下 main 函数和它实际引用的函数
print(optimized_mod)
```

## 相关 Pass

- **FoldConstant**：常量折叠 Pass，与死代码消除结合可以进一步优化代码
- **FuseOps**：算子融合 Pass，在死代码消除后应用可以获得更好的融合效果
- **LegalizeOps**：算子合法化 Pass，可能需要在其前后都应用死代码消除
- **ToNonDataflow**：将数据流图转换为非数据流表示，与死代码消除协同工作

## 注意事项

1. **入口函数选择**：正确指定入口函数至关重要，如果遗漏了实际使用的入口函数，可能导致重要代码被错误移除

2. **动态调用处理**：对于通过字符串动态调用的函数，可能需要特殊处理以确保不被错误消除

3. **外部函数依赖**：确保所有必要的外部函数调用都得到正确处理，避免破坏模块的功能完整性

4. **调试信息**：在调试阶段可能需要暂时禁用该 Pass，以保留完整的函数调用信息