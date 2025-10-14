---
title: xfail_parameterizations
description: 用于标记参数化测试中预期失败的测试用例，在TVM测试框架中管理已知问题的测试参数组合
---

# xfail_parameterizations

## 概述

`xfail_parameterizations` 是 TVM 测试框架中的一个参数化标记函数，专门用于处理参数化测试中的预期失败情况。该函数基于 pytest 框架的 `xfail` 机制，允许测试开发者明确标记某些特定的参数组合在当前环境下预期会失败。

在 TVM 测试流程中，该函数主要用于：
- 标记在特定目标平台或设备上已知存在问题的测试用例
- 处理因硬件限制、编译器bug或临时性问题导致的测试失败
- 在持续集成中区分真正的回归问题和已知问题

该函数与 TVM 的测试基础设施紧密集成，能够与 `tvm.testing.parameter`、`tvm.testing.fixture` 等测试工具协同工作。

## 函数签名

```python
def xfail_parameterizations(*xfail_params, reason):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| *xfail_params | tuple | 预期失败的参数值或参数组合，支持可变参数 | 无 |
| reason | str | 标记为预期失败的原因说明，用于文档和测试报告 | 必需 |

## 返回值

**类型:** `pytest.mark` 装饰器

返回一个 pytest 标记装饰器，该装饰器会将指定的参数组合标记为预期失败（xfail）。当测试运行到这些参数组合时，pytest 会将其作为预期失败处理，不会导致测试套件整体失败。

## 使用场景

### 目标平台特定问题
当某些测试用例在特定目标平台（如 CUDA、OpenCL、Metal）上存在已知问题时，可以使用该函数标记。

### 硬件限制处理
对于内存限制、计算能力不足等硬件相关的问题，标记相应的测试参数。

### 编译器bug规避
当 TVM 编译器在某些特定输入组合下存在已知bug时，临时标记相关测试用例。

### 渐进式测试改进
在修复复杂问题的过程中，逐步减少预期失败的测试用例数量。

## 使用示例

```python
import tvm.testing
import pytest

# 基本用法：标记单个参数值为预期失败
@tvm.testing.parametrize_targets("cuda", "llvm")
@tvm.testing.xfail_parameterizations(
    ("cuda",), 
    reason="CUDA后端在此配置下存在已知的内存分配问题"
)
def test_conv2d_operation(target, dev):
    # 测试实现
    A = te.placeholder((1, 3, 224, 224), name="A")
    W = te.placeholder((64, 3, 7, 7), name="W")
    conv = topi.nn.conv2d(A, W, 1, 1, 1)
    # ... 更多测试逻辑

# 标记多个参数组合
@tvm.testing.parametrize_targets("cuda", "llvm", "opencl")
@tvm.testing.parametrize_parameters(
    ("float32", 128),
    ("float16", 256), 
    ("int8", 512)
)
@tvm.testing.xfail_parameterizations(
    ("cuda", "float16", 256),
    ("opencl", "int8", 512),
    reason="特定目标平台与数据类型的组合存在精度问题"
)
def test_matrix_multiply(target, dtype, size):
    # 矩阵乘法测试实现
    pass

# 与fixture结合使用
@pytest.fixture
def test_config():
    return {"iterations": 100, "tolerance": 1e-6}

@tvm.testing.xfail_parameterizations(
    ("high_memory",),
    reason="内存密集型配置在移动设备上可能失败"
)
def test_memory_intensive_operation(test_config, memory_profile):
    # 内存密集型操作测试
    pass
```

## 注意事项

- **原因说明必需**：必须提供清晰的 `reason` 参数，说明为什么该测试用例被标记为预期失败
- **定期审查**：标记为 xfail 的测试用例应定期审查，确认问题是否已解决
- **目标平台敏感**：相同的参数组合在不同目标平台上的表现可能不同，需要分别标记
- **性能影响**：过度使用可能掩盖真正的回归问题，应谨慎使用
- **TVM版本兼容**：该函数依赖于 TVM 的测试基础设施，不同 TVM 版本间行为可能略有差异

## 相关函数

- [`pytest.mark.xfail`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-xfail) - 底层的 pytest xfail 标记
- [`tvm.testing.parametrize_targets`](../parametrize_targets) - TVM 目标平台参数化
- [`tvm.testing.parametrize_parameters`](../parametrize_parameters) - 通用参数化装饰器
- [`tvm.testing.fixture`](../fixture) - TVM 测试夹具
- [`_mark_parameterizations`](../_mark_parameterizations) - 内部参数化标记函数

---