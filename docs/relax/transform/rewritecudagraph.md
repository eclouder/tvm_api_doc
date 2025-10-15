---
title: RewriteCUDAGraph
description: TVM Relax 中用于重写 CUDA Graph 的模块级转换 Pass
---

# RewriteCUDAGraph

## 概述

`RewriteCUDAGraph` 是一个 TVM Relax 的模块级转换 Pass，主要用于在 CUDA 后端启用 CUDA Graph 优化。该 Pass 通过重写计算图，使得 Relax 模型能够利用 CUDA Graph 的特性来减少内核启动开销，提升推理性能。

## 函数签名

```cpp
Pass RewriteCUDAGraph()
```

**返回值**: `Pass` - 返回一个 TVM 转换 Pass 对象

## 参数说明

该 Pass 不接受显式参数，但通过 `PassContext` 配置来控制行为：

- `relax.backend.use_cuda_graph` (Bool, 可选): 控制是否启用 CUDA Graph 重写的配置选项
  - 默认值: `Bool(false)` (禁用)
  - 设置为 `Bool(true)` 时启用 CUDA Graph 重写

## 实现原理

`RewriteCUDAGraph` Pass 的核心实现逻辑如下：

1. **配置检查**: 首先检查 `PassContext` 中的 `relax.backend.use_cuda_graph` 配置项
2. **条件执行**: 只有当配置项为 `true` 时，才会执行实际的图重写操作
3. **图重写**: 调用底层的 `::tvm::relax::RewriteCUDAGraph` 函数对 IRModule 进行转换
4. **模块返回**: 返回转换后的 IRModule，如果未启用 CUDA Graph 则返回原始模块

```cpp
bool use_cuda_graph = 
    pc->GetConfig<Bool>("relax.backend.use_cuda_graph").value_or(Bool(false))->value;
if (use_cuda_graph) {
    mod = ::tvm::relax::RewriteCUDAGraph(std::move(mod));
}
```

## 优化效果

启用 `RewriteCUDAGraph` Pass 可以带来以下优化效果：

- **减少内核启动开销**: CUDA Graph 将多个内核启动操作合并为单个图执行，显著减少启动延迟
- **提高推理吞吐量**: 对于重复执行的推理任务，使用 CUDA Graph 可以提升整体吞吐量
- **降低 CPU 开销**: 减少主机与设备之间的通信开销

## 使用场景

该 Pass 主要适用于以下场景：

- **推理部署**: 在需要高性能推理的 CUDA 后端部署场景
- **重复执行**: 当同一个计算图需要多次执行时（如批量推理）
- **延迟敏感**: 对推理延迟有严格要求的应用场景
- **静态图优化**: 适用于计算图结构固定的情况

## 示例代码

以下是如何在 TVM 编译流程中使用 `RewriteCUDAGraph` Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 构建 Relax 模块
mod = tvm.IRModule({...})

# 创建 Pass 序列，包含 RewriteCUDAGraph
seq = transform.Sequential([
    # ... 其他 Pass
    transform.RewriteCUDAGraph(),
    # ... 其他 Pass
])

# 在启用 CUDA Graph 的上下文中执行转换
with tvm.transform.PassContext(opt_level=3, config={
    "relax.backend.use_cuda_graph": True
}):
    mod_optimized = seq(mod)
```

或者单独使用该 Pass：

```python
# 单独应用 RewriteCUDAGraph Pass
with tvm.transform.PassContext(config={
    "relax.backend.use_cuda_graph": True
}):
    mod_optimized = transform.RewriteCUDAGraph()(mod)
```

## 相关 Pass

- **`FuseOps`**: 算子融合 Pass，通常与 CUDA Graph 重写结合使用以获得更好的性能
- **`FuseTIR`**: TIR 级别的融合 Pass，为 CUDA Graph 提供更细粒度的优化
- **`ToMixedPrecision`**: 混合精度转换，可与 CUDA Graph 协同优化
- **`LegalizeOps`**: 算子合法化 Pass，确保算子能够在 CUDA 后端正确执行

## 注意事项

- CUDA Graph 要求计算图结构在执行过程中保持不变
- 对于动态形状或控制流复杂的模型，CUDA Graph 可能无法充分发挥优势
- 需要 CUDA 10.0 或更高版本支持
- 在某些特定硬件上可能需要额外的兼容性检查