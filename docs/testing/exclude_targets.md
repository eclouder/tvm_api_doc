---
title: exclude_targets
description: 用于在TVM测试中排除特定目标平台的装饰器函数
---

# exclude_targets

## 概述

`exclude_targets` 是 TVM 测试框架中的一个装饰器函数，主要用于在参数化测试中排除特定的目标平台。当开发者需要对 TVM 代码进行跨平台测试，但某些目标平台由于功能限制或不兼容性无法支持特定测试用例时，可以使用此装饰器来精确控制测试的执行范围。

该函数在 TVM 测试流程中扮演着重要的过滤角色，与 `tvm.testing.enabled_targets()` 和 `tvm.testing.parametrize_targets` 等函数配合使用，共同构成了 TVM 的多平台测试体系。通过内部应用 `pytest.mark.skipif` 机制，它能够在测试运行时动态跳过被排除的目标平台。

## 函数签名

```python
def exclude_targets(*args):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| *args | str | 可变参数，接受一个或多个要排除的目标平台名称 | 无 |

## 返回值

**类型:** `function`

返回一个装饰器函数，该装饰器会为被装饰的测试函数添加 `tvm_excluded_targets` 属性，记录需要排除的目标平台列表。

## 使用场景

### 目标平台兼容性测试
当某个 TVM 操作或特性在特定目标平台上不受支持时，使用此装饰器排除该平台，确保测试套件能够正常完成。

### 功能特性测试
测试某些仅在特定架构上可用的功能时，排除不支持该功能的目标平台。

### 性能基准测试
在进行性能对比测试时，排除那些由于硬件限制无法提供有意义的性能数据的平台。

### 渐进式开发
在开发新功能时，可以先排除尚未实现支持的目标平台，随着开发的推进逐步增加测试覆盖。

## 使用示例

### 基本用法：排除单个目标平台

```python
import tvm.testing

@tvm.testing.exclude_targets("cuda")
def test_matrix_multiply(target, dev):
    """测试矩阵乘法，但排除CUDA平台"""
    # 测试实现代码
    A = tvm.nd.array(np.random.rand(128, 128).astype("float32"), device=dev)
    B = tvm.nd.array(np.random.rand(128, 128).astype("float32"), device=dev)
    # ... 矩阵乘法测试逻辑
```

### 排除多个目标平台

```python
@tvm.testing.exclude_targets("llvm", "cuda", "opencl")
def test_specialized_operation(target, dev):
    """测试仅在特定加速器上支持的专用操作"""
    # 这个操作可能只在 vulkan 或 metal 等平台上可用
    # 排除其他不支持的平台
    assert target in ["vulkan", "metal"]
    # ... 专用操作测试逻辑
```

### 与参数化测试结合使用

```python
import pytest

# 先使用 exclude_targets 排除不支持的平台
# 再使用 parametrize_targets 进行参数化测试
@tvm.testing.exclude_targets("cuda")
@pytest.mark.parametrize("target", tvm.testing.enabled_targets())
def test_convolution_operations(target, dev):
    """在各种可用平台上测试卷积操作，但排除CUDA"""
    # 卷积操作测试实现
    # 这个测试会在所有 enabled_targets() 中除了cuda的平台运行
```

## 注意事项

- **函数签名要求**: 被装饰的测试函数必须遵循 `def test_xxxxxxxxx(target, dev):` 的签名格式，其中 `target` 参数接收目标平台名称，`dev` 参数接收对应的设备对象。

- **目标平台名称**: 传入的目标平台名称应与 TVM 内部使用的标识符一致，如 "llvm"、"cuda"、"rocm"、"opencl"、"metal"、"vulkan" 等。

- **与pytest集成**: 该装饰器底层使用 pytest 的跳过机制，被排除的目标平台在测试执行时会被标记为跳过而非失败。

- **执行顺序**: 当与其他装饰器（如 `@pytest.mark.parametrize`）一起使用时，需要注意装饰器的应用顺序。

- **测试发现**: 被排除的目标平台仍然会在 pytest 的测试发现中出现，但执行时会自动跳过。

## 相关函数

- **tvm.testing.enabled_targets()**: 获取当前环境中所有可用的目标平台列表
- **tvm.testing.parametrize_targets**: 自动为测试函数参数化所有可用目标平台
- **pytest.mark.skipif**: pytest 原生的条件跳过装饰器
- **tvm.testing.requires_target**: 要求特定目标平台可用的装饰器，与 exclude_targets 功能互补