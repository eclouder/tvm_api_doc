---
title: parametrize_targets
description: 用于在TVM测试中针对特定目标平台和设备参数化测试函数的装饰器
---

# parametrize_targets

## 概述

`parametrize_targets` 是 TVM 测试框架中的一个关键装饰器函数，主要用于在 pytest 测试中对特定的目标平台（target）和设备（device）进行参数化。该函数允许开发者明确指定测试用例应该在哪些目标平台上运行，特别适用于那些只针对特定硬件平台或需要验证目标特定功能（如汇编代码）的测试场景。

在 TVM 的测试生态中，该函数与 `enabled_targets`、`exclude_targets` 和 `known_failing_targets` 等函数协同工作，共同构成了 TVM 跨平台测试的基础设施。当测试函数需要针对不同后端（如 LLVM、CUDA、OpenCL 等）验证相同功能时，使用此装饰器可以避免编写重复的测试代码。

## 函数签名

```python
def parametrize_targets(*args):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| *args | 可变参数 | 可以接受一个函数或多个目标平台字符串。当作为无参装饰器使用时，参数为被装饰的函数；当指定目标平台时，参数为目标平台名称字符串列表 | 无 |

**参数说明：**
- 当只有一个参数且为可调用函数时：作为无参装饰器使用，测试将针对 `tvm.testing.enabled_targets()` 返回的所有可用目标平台运行
- 当有多个字符串参数时：每个字符串代表一个目标平台名称，测试将仅在这些指定的目标平台上运行

## 返回值

**类型:** `function` 或 `pytest.mark.parametrize` 标记

根据使用方式返回：
- 当作为无参装饰器使用时：直接返回被装饰的函数
- 当指定目标平台时：返回 pytest 的参数化标记，用于在测试会话级别对 `target` 参数进行参数化

## 使用场景

### 目标平台特定测试
当测试用例需要验证特定目标平台的专有功能时，如：
- 验证特定硬件的汇编代码生成
- 测试目标特定的 intrinsic 函数
- 验证硬件加速器的特定功能

### 跨平台功能验证
当需要在多个目标平台上验证相同功能的正确性时，避免为每个平台编写重复的测试代码。

### 受限目标测试
当某些测试只适用于部分目标平台，在其他平台上无意义或无法运行时。

## 使用示例

### 基本用法：指定特定目标平台

```python
import tvm.testing
import tvm
import pytest

@tvm.testing.parametrize_targets("llvm", "cuda")
def test_vector_add(target, dev):
    """测试向量加法在不同目标平台上的正确性"""
    # 创建测试数据
    n = 1024
    A = tvm.te.placeholder((n,), name='A')
    B = tvm.te.placeholder((n,), name='B')
    C = tvm.te.compute((n,), lambda i: A[i] + B[i], name='C')
    
    # 构建和运行
    s = tvm.te.create_schedule(C.op)
    f = tvm.build(s, [A, B, C], target=target)
    
    # 在设备上执行验证
    # ... 具体的测试逻辑
```

### 无参装饰器用法（向后兼容）

```python
@tvm.testing.parametrize_targets
def test_target_specific_feature(target, dev):
    """测试将针对所有启用的目标平台运行"""
    # 此测试将自动在所有 tvm.testing.enabled_targets() 返回的目标平台上运行
    # 测试逻辑...
```

### 测试目标特定的汇编代码

```python
@tvm.testing.parametrize_targets("llvm -mcpu=core-avx2")
def test_avx2_intrinsics(target, dev):
    """验证 AVX2 intrinsic 函数的正确性"""
    # 此测试专门针对支持 AVX2 指令集的 LLVM 目标
    # 测试逻辑涉及 AVX2 特定的向量化操作
```

## 注意事项

- **测试函数签名要求**：使用 `parametrize_targets` 装饰的测试函数必须接受 `target` 和 `dev` 参数，即函数签名应为 `def test_xxxx(target, dev):`

- **目标平台可用性**：指定的目标平台必须在当前环境中可用且已启用，否则测试可能会被跳过

- **与自动参数化的关系**：现代 TVM 版本会自动为接受 `target` 或 `dev` 参数的测试函数进行参数化，因此显式使用无参装饰器通常不再必要

- **性能考虑**：参数化会在每个目标平台上运行完整的测试，对于耗时较长的测试，应考虑使用 `pytest` 的标记功能进行选择性运行

- **错误处理**：如果指定的目标平台不可用，测试将自动跳过而不是失败

## 相关函数

- [`tvm.testing.enabled_targets()`](../enabled_targets)：获取当前环境中所有启用的目标平台
- [`tvm.testing.exclude_targets()`](../exclude_targets)：排除特定目标平台的装饰器
- [`tvm.testing.known_failing_targets()`](../known_failing_targets)：标记在特定目标平台上已知会失败的测试
- `pytest.mark.parametrize`：pytest 原生的参数化装饰器，本函数基于此实现

## 版本兼容性

此函数从 TVM 早期版本开始提供，保持了良好的向后兼容性。无参装饰器用法在现代版本中主要由自动参数化机制处理，但为了兼容旧代码仍然支持。