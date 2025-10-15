---
title: get_default_pipeline
description: TVM Relax Pipeline - get_default_pipeline 函数 API 文档
---

# get_default_pipeline

## 概述

`get_default_pipeline` 函数用于根据给定的目标设备获取默认的 Relax 编译流水线。该函数是 TVM Relax 编译流程中的关键组件，能够自动为不同的硬件后端选择合适的编译优化策略。

## 函数签名

```python
def get_default_pipeline(target: tvm.target.Target)
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| target | tvm.target.Target | 无 | 目标设备对象，包含硬件架构、特性等编译目标信息 |

## 返回值

**类型:** `tvm.relax.transform.Pipeline`

返回一个 Relax 编译流水线对象，该流水线包含针对特定目标设备优化的转换序列。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax

# 为 CUDA 目标获取默认流水线
cuda_target = tvm.target.Target("cuda")
cuda_pipeline = relax.get_default_pipeline(cuda_target)

# 为 CPU 目标获取默认流水线
cpu_target = tvm.target.Target("llvm -mcpu=core-avx2")
cpu_pipeline = relax.get_default_pipeline(cpu_target)

# 应用流水线到 Relax 模块
mod_transformed = cuda_pipeline(mod)
```

### 高级用法

```python
import tvm
from tvm import relax

# 为 Adreno GPU 获取默认流水线
opencl_target = tvm.target.Target("opencl -device=adreno")
adreno_pipeline = relax.get_default_pipeline(opencl_target)

# 自定义流水线组合
custom_pipeline = tvm.transform.Sequential([
    adreno_pipeline,
    # 添加自定义转换
    relax.transform.SomeCustomPass()
])
```

## 实现细节

该函数通过检查目标设备的 `kind.name` 属性来路由到相应的后端专用流水线：

- **CUDA**: 使用 `backend.cuda.get_default_pipeline`
- **ROCm**: 使用 `backend.rocm.get_default_pipeline`  
- **Metal**: 使用 `backend.gpu_generic.get_default_pipeline`
- **LLVM (CPU)**: 使用 `backend.cpu_generic.get_default_pipeline`
- **OpenCL with Adreno**: 使用 `backend.adreno.get_default_pipeline`

每个后端都实现了针对其硬件特性的优化流水线，包括算子融合、内存布局优化、代码生成等关键编译步骤。

## 相关函数

- [`relax.build`](./relax_build.md) - 构建 Relax 模块为可执行格式
- [`relax.transform.Pipeline`](./pipeline_class.md) - 编译流水线类文档
- [`tvm.target.Target`](../target/target.md) - 目标设备配置类

## 注意事项

- 目前仅支持 CUDA、ROCm、Metal、LLVM 和 Adreno OpenCL 目标设备
- 对于其他目标设备，需要手动构建编译流水线
- 返回的流水线是只读的，如需修改建议创建副本
- 流水线的具体内容可能随 TVM 版本更新而变化

## 错误处理

当传入不支持的目标设备时，函数会抛出 `ValueError` 异常：

```python
try:
    pipeline = relax.get_default_pipeline(unsupported_target)
except ValueError as e:
    print(f"不支持的设备: {e}")
    # 需要手动构建流水线
    custom_pipeline = create_custom_pipeline(unsupported_target)
```

错误消息会明确指出不支持的目标设备，并建议用户手动构建 IRModule。