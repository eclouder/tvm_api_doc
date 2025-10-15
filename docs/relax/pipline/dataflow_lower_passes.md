---
title: dataflow_lower_passes
description: TVM Relax Pipeline - dataflow_lower_passes 函数 API 文档
---

# dataflow_lower_passes

## 概述

`dataflow_lower_passes` 函数用于获取针对特定目标平台的默认数据流 lowering 过程。该函数根据不同的硬件目标（target）返回相应的优化和转换过程集合，这些过程用于将 Relax 中间表示（IR）转换为目标平台特定的数据流表示。

## 函数签名

```python
def dataflow_lower_passes(target: tvm.target.Target)
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| target | tvm.target.Target | 无 | 目标硬件平台，指定了编译的目标设备特性 |

## 返回值

**类型:** `List[tvm.relax.transform.Pass]`

返回一个 Pass 列表，包含针对指定目标平台的数据流 lowering 过程。这些 Pass 将按顺序应用于 Relax IR 以完成数据流 lowering 转换。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import dataflow_lower_passes

# 为 CUDA 目标获取数据流 lowering 过程
cuda_target = tvm.target.Target("cuda")
cuda_passes = dataflow_lower_passes(cuda_target)
print(f"CUDA dataflow lowering passes: {len(cuda_passes)} passes")

# 为 CPU 目标获取数据流 lowering 过程
cpu_target = tvm.target.Target("llvm -mcpu=core-avx2")
cpu_passes = dataflow_lower_passes(cpu_target)
print(f"CPU dataflow lowering passes: {len(cpu_passes)} passes")
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import dataflow_lower_passes

# 为 ROCm 目标获取并应用数据流 lowering 过程
rocm_target = tvm.target.Target("rocm")
rocm_passes = dataflow_lower_passes(rocm_target)

# 构建完整的优化 pipeline
pipeline = relax.get_pipeline()  # 获取基础 pipeline
for pass_obj in rocm_passes:
    pipeline = pipeline + pass_obj  # 添加数据流 lowering 过程

# 应用完整的 pipeline 到模块
mod = tvm.IRModule()  # 你的 Relax 模块
optimized_mod = pipeline(mod)
```

## 实现细节

该函数通过检查目标平台的 `kind.name` 属性来分发到相应的后端实现：

- **CUDA**: 使用 `backend.cuda.dataflow_lower_passes`
- **ROCm**: 使用 `backend.rocm.dataflow_lower_passes`  
- **Metal**: 使用 `backend.gpu_generic.dataflow_lower_passes`
- **LLVM** (CPU): 使用 `backend.cpu_generic.dataflow_lower_passes`
- **OpenCL with Adreno**: 使用 `backend.adreno.dataflow_lower_passes`

对于不支持的平台，函数会抛出 `ValueError` 异常。

## 相关函数

- [`get_pipeline`](./get_pipeline.md) - 获取基础的 Relax 优化 pipeline
- [`transform.Pass`](./transform_pass.md) - TVM Relax 转换过程基类

## 注意事项

- 该函数返回的是 Pass 列表，需要按顺序应用到 Relax IR 模块上
- 不同的目标平台返回的 Pass 集合可能包含不同的优化策略
- 目前 generic GPU 支持仍在开发中（Todo 注释中提到）
- 确保传入有效的 `tvm.target.Target` 对象

## 错误处理

当传入不支持的目标平台时，函数会抛出 `ValueError` 异常：

```python
try:
    unsupported_target = tvm.target.Target("vulkan")
    passes = dataflow_lower_passes(unsupported_target)
except ValueError as e:
    print(f"Error: {e}")  # 输出: Target vulkan -keys=... is not yet supported by dataflow lowering passes.
```

常见的错误情况包括：
- 目标平台名称拼写错误
- 使用了尚未支持的后端（如 Vulkan、WebGPU 等）
- 目标配置不完整或无效