---
title: library_dispatch_passes
description: TVM Relax Pipeline - library_dispatch_passes 函数 API 文档
---

# library_dispatch_passes

## 概述

`library_dispatch_passes` 函数用于根据给定的目标设备获取默认的库调度（library dispatch）Pass 集合。该函数是 TVM Relax 编译流水线中的关键组件，负责为不同的硬件后端分配合适的优化 Pass 序列，以实现高效的代码生成。

## 函数签名

```python
def library_dispatch_passes(target: tvm.target.Target)
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| target | tvm.target.Target | 无 | 目标设备对象，包含硬件架构、特性等编译目标信息 |

## 返回值

**类型:** `List[tvm.ir.transform.Pass]`

返回一个 Pass 列表，包含针对指定目标设备优化的库调度 Pass 序列。这些 Pass 负责将高级 Relax 操作转换为特定硬件后端的库调用。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import library_dispatch_passes

# 为 CUDA 目标获取库调度 Pass
cuda_target = tvm.target.Target("cuda")
cuda_passes = library_dispatch_passes(cuda_target)
print(f"CUDA 库调度 Pass 数量: {len(cuda_passes)}")

# 为 CPU 目标获取库调度 Pass
cpu_target = tvm.target.Target("llvm -mcpu=core-avx2")
cpu_passes = library_dispatch_passes(cpu_target)
print(f"CPU 库调度 Pass 数量: {len(cpu_passes)}")
```

### 在完整编译流水线中使用

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import get_default_pipeline, library_dispatch_passes

# 创建目标设备
target = tvm.target.Target("cuda")

# 获取默认编译流水线
pipeline = get_default_pipeline(target)

# 在特定阶段插入库调度 Pass
library_passes = library_dispatch_passes(target)
# 将库调度 Pass 集成到完整流水线中
```

## 实现细节

该函数通过检查目标设备的 `kind.name` 属性来分派到相应的后端实现：

1. **CUDA 后端**: 调用 `backend.cuda.library_dispatch_passes(target)`
2. **ROCm 后端**: 调用 `backend.rocm.library_dispatch_passes(target)`
3. **Metal 后端**: 调用 `backend.gpu_generic.library_dispatch_passes(target)`
4. **LLVM 后端**: 调用 `backend.cpu_generic.library_dispatch_passes(target)`
5. **Adreno OpenCL**: 当目标为 OpenCL 且包含 "adreno" 关键字时，调用 `backend.adreno.library_dispatch_passes(target)`

每个后端实现都返回针对该硬件平台优化的 Pass 序列，这些 Pass 通常包括：
- 操作符融合和模式匹配
- 内存布局优化
- 特定硬件库调用插入
- 性能调优相关的转换

## 相关函数

- [`get_default_pipeline`](./get_default_pipeline.md) - 获取完整的默认编译流水线
- [`build`](./build.md) - 构建 Relax 模块到目标设备
- [`transform`](./transform.md) - 应用 Pass 序列到 IRModule

## 注意事项

- 该函数目前仅支持有限的后端目标：CUDA、ROCm、Metal、LLVM 和 Adreno OpenCL
- 对于不支持的硬件目标，函数会抛出 `ValueError` 异常
- 返回的 Pass 序列顺序对性能有重要影响，不应随意修改
- GPU 通用后端（gpu-generic）目前仍在开发中，暂不支持

## 错误处理

当传入不支持的目标设备时，函数会抛出 `ValueError` 异常：

```python
try:
    unsupported_target = tvm.target.Target("vulkan")
    passes = library_dispatch_passes(unsupported_target)
except ValueError as e:
    print(f"错误: {e}")
    # 输出: 错误: Target vulkan -keys=... is not yet supported by library dispatch passes.
```

建议在使用前检查目标设备是否被支持，或使用 try-except 块进行错误处理。