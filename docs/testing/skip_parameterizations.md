---
title: skip_parameterizations
description: 用于在TVM参数化测试中跳过特定参数组合的装饰器函数
---

# skip_parameterizations

## 概述

`skip_parameterizations` 是 TVM 测试框架中的一个重要装饰器函数，专门用于在参数化测试中精确控制测试用例的执行。该函数基于 pytest 框架构建，允许开发人员根据特定的参数组合来跳过不必要的测试执行，从而提高测试效率和针对性。

在 TVM 测试流程中，该函数位于测试用例装饰阶段，主要用于：
- 过滤掉已知会失败的参数组合
- 跳过特定目标平台不支持的参数配置
- 排除性能测试中不相关的参数设置
- 在持续集成中快速跳过耗时但非关键的测试场景

该函数与 TVM 的 `pytest.mark.parametrize` 装饰器紧密配合，为复杂的参数化测试提供了精细化的控制能力。

## 函数签名

```python
def skip_parameterizations(*skip_params, reason):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| *skip_params | tuple | 要跳过的参数组合，每个参数对应测试函数的一个参数位置 | 无 |
| reason | str | 跳过测试的原因说明，会在测试输出中显示 | 必需参数 |

## 返回值

**类型:** `pytest.mark` 对象

返回一个 pytest 标记对象，该对象会在测试执行时根据参数匹配情况决定是否跳过当前测试用例。

## 使用场景

### 单元测试
在算子测试中跳过特定数据类型或形状组合不支持的测试用例

### 集成测试
在端到端模型测试中排除特定目标设备不支持的配置

### 性能测试
跳过已知性能瓶颈的特定参数组合，专注于关键路径测试

### 目标平台测试
针对不同硬件后端（CPU、GPU、NPU）过滤不相关的测试参数

## 使用示例

```python
import tvm.testing
import pytest

# 基本用法：跳过特定的参数组合
@pytest.mark.parametrize("dtype", ["float32", "float16", "int8"])
@pytest.mark.parametrize("shape", [(32, 32), (64, 64)])
@tvm.testing.skip_parameterizations(
    ("float16", (64, 64)),  # 跳过 float16 类型的 64x64 形状
    ("int8", (32, 32)),     # 跳过 int8 类型的 32x32 形状
    reason="目标设备不支持该数据类型的特定形状"
)
def test_matmul_operator(dtype, shape):
    """测试矩阵乘法算子"""
    # 测试实现代码
    A = tvm.nd.array(np.random.randn(*shape).astype(dtype))
    B = tvm.nd.array(np.random.randn(*shape).astype(dtype))
    # ... 执行矩阵乘法测试

# TVM 目标设备相关的跳过示例
@pytest.mark.parametrize("target", ["llvm", "cuda", "opencl"])
@pytest.mark.parametrize("use_optimization", [True, False])
@tvm.testing.skip_parameterizations(
    ("cuda", False),        # 跳过 CUDA 的非优化版本
    ("opencl", True),       # 跳过 OpenCL 的优化版本
    reason="特定后端不支持该优化配置"
)
def test_conv2d_optimization(target, use_optimization):
    """测试卷积算子的优化效果"""
    with tvm.target.Target(target):
        # 根据 use_optimization 参数配置不同的优化级别
        # ... 执行卷积测试
```

## 注意事项

- **参数顺序重要性**: 传递给 `skip_parameterizations` 的参数顺序必须与 `pytest.mark.parametrize` 装饰器的参数顺序完全一致
- **精确匹配**: 函数执行精确的参数值匹配，不支持模糊匹配或模式匹配
- **装饰器顺序**: 必须将 `skip_parameterizations` 装饰器放在所有 `parametrize` 装饰器之后
- **TVM 版本兼容性**: 该函数在 TVM 0.8 及以上版本中稳定可用
- **性能影响**: 在参数组合较多时，建议合理使用以避免不必要的测试跳过检查开销

## 相关函数

- [`pytest.mark.parametrize`](https://docs.pytest.org/en/stable/parametrize.html) - pytest 参数化测试装饰器
- [`tvm.testing.parameter`](https://tvm.apache.org/docs/reference/api/python/testing.html) - TVM 参数化测试工具
- [`pytest.skip`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-skip) - pytest 跳过测试的基础函数
- `_mark_parameterizations` - TVM 内部参数标记实现函数

---