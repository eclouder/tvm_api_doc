---
title: finalize_passes
description: TVM Relax Pipeline - finalize_passes 函数 API 文档
---

# finalize_passes

## 概述

`finalize_passes` 函数用于获取针对特定目标平台的默认合法化（legalization）Pass 序列。该函数是 TVM Relax 编译流水线中的关键组件，负责为目标硬件生成最终的优化和代码生成 Pass。

## 函数签名

```python
def finalize_passes(target: tvm.target.Target) -> List[tvm.ir.transform.Pass]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| target | tvm.target.Target | 无 | 目标硬件平台，用于确定适用的最终优化 Pass 序列 |

## 返回值

**类型:** `List[tvm.ir.transform.Pass]`

返回一个 Pass 列表，包含针对指定目标平台的最终优化和代码生成 Pass 序列。这些 Pass 负责将 Relax IR 转换为目标硬件可执行的形式。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import finalize_passes

# 为 CUDA 目标获取最终 Pass 序列
cuda_target = tvm.target.Target("cuda")
cuda_passes = finalize_passes(cuda_target)
print(f"CUDA final passes count: {len(cuda_passes)}")

# 为 CPU 目标获取最终 Pass 序列
cpu_target = tvm.target.Target("llvm -mcpu=core-avx2")
cpu_passes = finalize_passes(cpu_target)
print(f"CPU final passes count: {len(cpu_passes)}")
```

### 在完整编译流程中使用

```python
import tvm
from tvm import relax
from tvm.relax.pipeline import finalize_passes

# 构建模型并应用最终 Pass 序列
mod = tvm.IRModule()  # 假设已有构建好的模块
target = tvm.target.Target("cuda")

# 获取最终 Pass 序列并应用到模块
final_passes = finalize_passes(target)
with tvm.transform.PassContext(opt_level=3):
    optimized_mod = tvm.transform.Sequential(final_passes)(mod)
```

## 实现细节

该函数根据目标平台的类型分发到相应的后端实现：

- **CUDA**: 使用 `backend.cuda.finalize_passes`
- **ROCm**: 使用 `backend.rocm.finalize_passes`  
- **Metal**: 使用 `backend.gpu_generic.finalize_passes`
- **LLVM (CPU)**: 使用 `backend.cpu_generic.finalize_passes`
- **OpenCL Adreno**: 使用 `backend.adreno.finalize_passes`

每个后端实现都提供了针对特定硬件架构优化的 Pass 序列，包括内存布局优化、指令选择、寄存器分配等关键步骤。

## 相关函数

- [`get_default_pipeline`](./get_default_pipeline.md) - 获取默认的 Relax 编译流水线
- [`legalize_ops`](./legalize_ops.md) - 操作符合法化 Pass
- [`lower_gpu_kernel`](./lower_gpu_kernel.md) - GPU 内核代码生成 Pass

## 注意事项

- 该函数目前仅支持有限的目标平台：CUDA、ROCm、Metal、LLVM 和 OpenCL Adreno
- 对于不支持的平台，函数会抛出 `ValueError` 异常
- GPU 通用后端（gpu-generic）目前仍在开发中，暂不支持
- 返回的 Pass 序列应该按照顺序应用到 Relax IR 模块上

## 错误处理

当传入不支持的目标平台时，函数会抛出 `ValueError` 异常：

```python
try:
    unsupported_target = tvm.target.Target("vulkan")
    passes = finalize_passes(unsupported_target)
except ValueError as e:
    print(f"Error: {e}")  # 输出: Target vulkan is not yet supported by finalization passes.
```

建议在使用前检查目标平台是否被支持，或者捕获可能的异常进行适当处理。