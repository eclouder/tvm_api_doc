---
title: LazySetOutput
description: TVM Relax 的 LazySetOutput Pass 用于延迟设置函数输出，优化参数处理性能。
---

# LazySetOutput

## 概述

LazySetOutput Pass 是 TVM Relax 中的一个函数级变换 Pass，主要功能是**延迟设置函数的输出**。该 Pass 通过 `WithLazyOutputs` 函数对具有全局符号名的函数进行处理，优化参数处理的性能，特别是在模型部署和参数转换场景中。

## 函数签名

```cpp
Pass LazySetOutput()
```

**返回值：**
- `Pass`：一个 TVM Pass 对象，可在 Pass 流水线中执行

## 参数说明

该 Pass 本身不接受参数，但在内部处理时会检查函数的以下属性：

- **函数属性 `tvm::attr::kGlobalSymbol`**：用于标识函数是否具有全局符号名。只有具有该属性的函数才会被处理。

## 实现原理

LazySetOutput Pass 的核心实现逻辑如下：

1. **函数筛选**：首先检查函数是否具有 `tvm::attr::kGlobalSymbol` 属性。如果没有该属性，直接返回原函数，不做任何处理。

2. **延迟输出设置**：对于具有全局符号名的函数，调用 `WithLazyOutputs(func)` 函数进行处理。该函数会：
   - 将函数的输出设置为延迟计算模式
   - 优化参数的内存分配和传输
   - 减少不必要的数据拷贝

3. **Pass 配置**：使用 `CreateFunctionPass` 创建函数级 Pass，设置：
   - 优化级别为 0（基础优化）
   - Pass 名称为 "LazySetOutput"
   - 无前置依赖 Pass

## 优化效果

使用 LazySetOutput Pass 可以带来以下优化效果：

- **内存优化**：减少参数传输过程中的内存分配和拷贝
- **性能提升**：通过延迟输出计算，避免不必要的即时计算开销
- **部署友好**：特别适合模型部署场景，优化参数加载过程

## 使用场景

LazySetOutput Pass 主要适用于以下场景：

1. **模型部署**：在将模型部署到目标设备时，优化参数处理流程
2. **参数转换**：在模型参数格式转换过程中使用
3. **大型模型**：处理参数量较大的模型时，内存优化效果更加明显
4. **多设备部署**：在不同设备间传输模型参数时

**使用时机建议：**
- 在参数绑定和优化之后使用
- 在模型导出或序列化之前使用

## 示例代码

```python
import tvm
from tvm import relax

# 创建 IRModule
module = relax.transform.LazySetOutput()(module)

# 或者在 Pass 流水线中使用
seq = tvm.transform.Sequential([
    # ... 其他 Pass
    relax.transform.LazySetOutput(),
    # ... 其他 Pass
])
optimized_module = seq(module)
```

## 相关 Pass

- **`ToNonDataflow`**：将数据流图转换为非数据流格式
- **`BindParams`**：参数绑定 Pass，与 LazySetOutput 配合使用
- **`FoldConstant`**：常量折叠 Pass，可在 LazySetOutput 之前使用
- **`DeadCodeElimination`**：死代码消除，清理优化后的无用代码

## 注意事项

- 该 Pass 只对具有全局符号名的函数生效
- 优化级别设置为 0，表示这是一个基础优化 Pass
- 在使用时需要确保函数已正确设置全局符号属性