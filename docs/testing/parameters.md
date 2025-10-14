---
title: parameters
description: 用于定义pytest参数化测试fixture的便捷函数，支持多参数组合测试
---

# parameters

## 概述

`tvm.testing.parameters` 是 TVM 测试框架中的核心参数化工具函数，专门用于简化 pytest 参数化测试的编写。该函数的主要作用是定义一组参数化的测试fixture，使得测试函数能够自动运行多次，每次使用不同的参数组合。

在 TVM 测试流程中，该函数位于测试用例的参数化层，与 pytest 框架深度集成。它特别适用于那些没有显著设置成本的参数类型，如基本数据类型、字符串、元组等。与 `tvm.testing.parameter` 不同，当测试函数接受多个通过单次 `parameters` 调用定义的参数时，测试只会为每个参数集运行一次，而不是所有参数的笛卡尔积组合。

## 函数签名

```python
def parameters(*value_sets, ids=None):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| *value_sets | 可变参数列表 | 参数值集合的列表。每个值集合代表要测试的单个参数组合。接受这些参数定义的单元测试将对列表中的每个参数集运行一次。 | 无默认值 |
| ids | List[str], 可选 | 参数集的名称列表。如果为None，pytest将为每个参数集生成名称。对于元组等复合类型，生成的名称可能不够直观。 | None |

## 返回值

**类型:** `List[function]`

返回 pytest.fixture 的函数输出列表。这些输出应该解包为单独的命名参数，每个返回的函数对应一个参数化的fixture。

## 使用场景

### 单元测试
在 TVM 算子测试、张量运算验证等场景中，使用 `parameters` 快速测试不同数据类型和形状的组合。

### 目标平台测试
测试 TVM 在不同目标设备（CPU、GPU、加速器等）上的行为，可以参数化目标字符串和设备类型。

### 性能测试
通过参数化不同的优化级别、线程数等配置，评估 TVM 编译后代码的性能特征。

### 集成测试
在端到端模型测试中，参数化不同的模型架构、输入尺寸和精度要求。

## 使用示例

```python
import tvm.testing
import pytest

# 基本用法：测试不同尺寸和数据类型的组合
size, dtype = tvm.testing.parameters(
    (16, 'float32'), 
    (512, 'float16'),
    (1024, 'int32')
)

def test_tensor_operations(size, dtype):
    """测试不同尺寸和数据类型下的张量操作"""
    # 创建测试张量
    A = tvm.te.placeholder((size, size), name='A', dtype=dtype)
    B = tvm.te.placeholder((size, size), name='B', dtype=dtype)
    
    # 简单的张量加法
    C = tvm.te.compute((size, size), lambda i, j: A[i, j] + B[i, j])
    
    # 构建和运行测试
    s = tvm.te.create_schedule(C.op)
    # ... 构建和验证逻辑
    assert isinstance(size, int)
    assert dtype in ['float32', 'float16', 'int32']

# 目标设备参数化测试
target, dev = tvm.testing.parameters(
    ("llvm", "cpu"),
    ("cuda", "gpu"),
    ("opencl", "gpu")
)

def test_device_specific_kernels(target, dev):
    """测试不同目标设备上的内核执行"""
    # 设备特定的测试逻辑
    tvm_target = tvm.target.Target(target)
    # ... 设备配置和内核测试
```

## 注意事项

- **设置成本限制**: 该函数适用于设置成本低的参数类型。对于需要复杂初始化或高成本设置的场景，应使用 `tvm.testing.fixture` 替代。

- **模块级作用域**: 参数定义适用于模块中的所有测试。如果特定测试需要不同的参数值，应使用 `@pytest.mark.parametrize` 标记该测试。

- **参数组合行为**: 与 `tvm.testing.parameter` 不同，单次 `parameters` 调用中的多个参数会作为组合集处理，而不是独立的参数维度。

- **ID 生成**: 当不提供 `ids` 参数时，pytest 自动生成的参数名称可能对复杂数据类型不够友好，建议为复杂参数提供明确的标识符。

## 相关函数

- [`tvm.testing.parameter`](parameter): 用于定义独立的参数化维度，会产生所有参数的笛卡尔积组合
- [`tvm.testing.fixture`](fixture): 用于定义具有显著设置成本的测试fixture
- `pytest.mark.parametrize`: pytest原生的参数化装饰器，用于单个测试的特殊参数需求

该函数与 TVM 的目标平台和设备抽象层紧密配合，支持跨平台的一致性测试体验，是 TVM 测试生态中的重要组成部分。