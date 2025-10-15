---
title: get_pipeline
description: TVM Relax Pipeline - get_pipeline 函数 API 文档
---

# get_pipeline

## 概述

`get_pipeline` 函数用于根据名称获取 TVM Relax 预构建的编译流水线。该函数是 TVM Relax 编译流程中的核心组件，允许用户通过简单的名称调用来获取经过优化的预定义编译流水线，从而简化深度学习模型的编译过程。

## 函数签名

```python
def get_pipeline(name: str = 'zero', **kwargs) -> tvm.transform.Pass
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| name | str | 'zero' | 预构建流水线的名称。必须是 `PIPELINE_MAP` 中已注册的流水线名称 |
| kwargs | Dict[str, object] | - | 用于配置流水线的关键字参数，具体参数取决于所选的流水线类型 |

## 返回值

**类型:** `tvm.transform.Pass`

返回一个 TVM 转换 Pass 对象，该对象代表了完整的编译流水线，可以应用于 Relax 模块进行编译优化。

## 使用示例

### 基本用法

```python
import tvm
from tvm.relax import get_pipeline

# 获取默认的 'zero' 流水线
pipeline = get_pipeline()

# 获取特定的预构建流水线
optimized_pipeline = get_pipeline("optimized")

# 应用流水线到 Relax 模块
mod_optimized = pipeline(mod)
```

### 高级用法

```python
import tvm
from tvm.relax import get_pipeline

# 使用关键字参数配置流水线
custom_pipeline = get_pipeline(
    "advanced", 
    enable_fusion=True,
    optimization_level=2,
    target_device="cuda"
)

# 将流水线应用于模块并构建
with tvm.transform.PassContext(opt_level=3):
    optimized_mod = custom_pipeline(relax_mod)
    ex = relax.build(optimized_mod, target="llvm")
```

## 实现细节

函数内部维护了一个 `PIPELINE_MAP` 字典，该字典映射流水线名称到对应的工厂函数。当调用 `get_pipeline` 时：

1. 首先检查请求的流水线名称是否在 `PIPELINE_MAP` 中注册
2. 如果名称不存在，抛出 `ValueError` 异常并列出所有可用的流水线名称
3. 如果名称存在，调用对应的工厂函数并传入所有关键字参数
4. 返回构建好的 `tvm.transform.Pass` 对象

## 相关函数

- [`relax.transform.get_default_pipeline`](./get_default_pipeline.md) - 获取默认的 Relax 编译流水线
- [`tvm.transform.Sequential`](./Sequential.md) - TVM 转换 Pass 序列容器
- [`relax.build`](./build.md) - 构建 Relax 模块为可执行格式

## 注意事项

- 在使用前请确保所需的流水线名称已在 `PIPELINE_MAP` 中注册
- 不同的流水线可能接受不同的关键字参数，请参考具体流水线的文档
- 返回的 Pass 对象需要通过 `tvm.transform.PassContext` 来应用执行
- 流水线的性能特征和优化效果会因名称和配置参数的不同而有所差异

## 错误处理

- **ValueError**: 当指定的 `name` 参数不在预定义的流水线名称列表中时抛出。错误消息会包含所有可用的流水线名称候选列表，方便用户选择正确的流水线。
- **TypeError**: 当传递给 `kwargs` 的参数类型与特定流水线期望的类型不匹配时可能抛出。
- **RuntimeError**: 在流水线构建或执行过程中遇到内部错误时抛出。

常见的错误处理方式：

```python
try:
    pipeline = get_pipeline("unknown_pipeline")
except ValueError as e:
    print(f"可用流水线: {e}")
    # 回退到默认流水线
    pipeline = get_pipeline()
```