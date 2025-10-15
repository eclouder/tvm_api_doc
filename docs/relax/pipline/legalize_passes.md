---
title: legalize_passes
description: TVM Relax Pipeline - legalize_passes 函数 API 文档
---

# legalize_passes

## 概述

`legalize_passes` 函数用于根据给定的目标设备获取默认的合法化（legalization）Pass 集合。该函数是 TVM Relax Pipeline 中的重要组成部分，负责为不同的硬件后端分配合适的合法化优化流程。

## 函数签名

```python
def legalize_passes(target: tvm.target.Target)
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| target | tvm.target.Target | 无 | 目标硬件设备，用于确定应该返回哪个后端的合法化 Pass 集合 |

## 返回值

**类型:** `List[tvm.ir.transform.Pass]`

返回一个 Pass 列表，包含针对指定目标设备的合法化转换 Pass。这些 Pass 用于将 Relax IR 转换为目标硬件能够高效执行的格式。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import legalize_passes

# 为 CUDA 目标获取合法化 Pass
cuda_target = tvm.target.Target("cuda")
cuda_passes = legalize_passes(cuda_target)
print(f"CUDA legalization passes: {len(cuda_passes)} passes")

# 为 CPU 目标获取合法化 Pass
cpu_target = tvm.target.Target("llvm -mcpu=core-avx2")
cpu_passes = legalize_passes(cpu_target)
print(f"CPU legalization passes: {len(cpu_passes)} passes")
```

### 在完整 Pipeline 中使用

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import legalize_passes, get_default_pipeline

# 构建完整的编译 pipeline
target = tvm.target.Target("cuda")
pipeline = get_default_pipeline(target)

# 获取特定阶段的合法化 Pass
legalization_stage = legalize_passes(target)
print(f"Legalization stage contains {len(legalization_stage)} passes")
```

## 实现细节

该函数通过检查目标设备的 `kind.name` 属性来分派到相应的后端实现：

1. **CUDA 后端**: 使用 `backend.cuda.legalize_passes(target)`
2. **ROCm 后端**: 使用 `backend.rocm.legalize_passes(target)`  
3. **Metal 后端**: 使用 `backend.gpu_generic.legalize_passes(target)`
4. **LLVM CPU 后端**: 使用 `backend.cpu_generic.legalize_passes(target)`
5. **Adreno GPU (OpenCL)**: 当目标为 OpenCL 且包含 "adreno" 关键字时，使用 `backend.adreno.legalize_passes(target)`

每个后端都实现了针对其硬件特性的特定合法化优化，如内存布局转换、特殊指令映射等。

## 相关函数

- [`get_default_pipeline`](./get_default_pipeline.md) - 获取完整的默认编译 pipeline
- [`build`](./build.md) - 构建 Relax 模块到目标设备
- [`transform`](./transform.md) - 应用 Pass 转换到 Relax 模块

## 注意事项

- 该函数目前不支持所有目标设备，对于不支持的目标会抛出 `ValueError`
- GPU 通用后端（gpu-generic）的支持仍在开发中（Todo 标记）
- 返回的 Pass 列表顺序很重要，应该按照指定的顺序执行
- 不同的目标设备可能有不同数量和类型的合法化 Pass

## 错误处理

当传入不支持的目标设备时，函数会抛出 `ValueError`：

```python
try:
    unsupported_target = tvm.target.Target("vulkan")
    passes = legalize_passes(unsupported_target)
except ValueError as e:
    print(f"Error: {e}")
    # 输出: Error: Target vulkan is not yet supported by library dispatch passes.
```

常见的错误情况包括：
- 目标设备类型不在支持列表中
- 目标设备字符串格式不正确
- 后端模块导入失败

---