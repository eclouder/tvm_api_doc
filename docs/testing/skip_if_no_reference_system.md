---
title: skip_if_no_reference_system
description: 用于在TVM测试中跳过需要参考系统但当前环境不支持的测试用例的装饰器函数
---

# skip_if_no_reference_system

## 概述

`skip_if_no_reference_system` 是 TVM 测试框架中的一个装饰器函数，主要用于在 32 位系统环境下自动跳过需要参考系统支持的测试用例。该函数通过检测当前运行环境是否为 32 位架构，来决定是否执行被装饰的测试函数。

在 TVM 测试流程中，该函数位于测试用例装饰层，与 pytest 测试框架深度集成。它专门用于处理在 i386 容器环境中无法提供参考系统的情况，确保测试套件在不同架构平台上的兼容性。

该函数实际上是 `skip_if_32bit` 装饰器的一个特化版本，专门针对参考系统不可用的场景进行了语义化封装。

## 函数签名

```python
def skip_if_no_reference_system(func):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| func | function | 需要被装饰的测试函数 | 无默认值 |

## 返回值

**类型:** `function`

返回一个经过包装的测试函数，当运行在 32 位系统环境下时，该函数会被 pytest 自动跳过，并显示预定义的跳过原因。

## 使用场景

### 单元测试
在涉及参考系统比较的单元测试中，确保测试不会在不受支持的环境中执行。

### 目标平台测试
当测试用例需要特定的参考系统实现来进行结果验证时，使用此装饰器避免在 32 位环境中的执行失败。

### 跨平台测试套件
在需要确保测试套件在不同架构（x86_64 vs i386）上都能正常运行的场景中使用。

## 使用示例

```python
import tvm
import tvm.testing
import pytest

@tvm.testing.skip_if_no_reference_system
def test_conv2d_reference():
    """测试卷积算子的参考系统实现"""
    # 构建测试数据
    input_data = tvm.nd.array(np.random.rand(1, 3, 224, 224).astype("float32"))
    weight_data = tvm.nd.array(np.random.rand(64, 3, 3, 3).astype("float32"))
    
    # 使用参考系统进行验证
    reference_output = compute_reference_conv2d(input_data, weight_data)
    tvm_output = compute_tvm_conv2d(input_data, weight_data)
    
    # 比较结果
    tvm.testing.assert_allclose(tvm_output.asnumpy(), reference_output, rtol=1e-5)

@tvm.testing.skip_if_no_reference_system  
def test_linear_layer_accuracy():
    """测试全连接层的数值精度"""
    # 此测试在32位系统中会被自动跳过
    # 测试实现代码...
```

## 注意事项

- **架构限制**: 该装饰器专门针对 32 位 i386 架构环境，在其他架构上测试函数会正常执行
- **容器环境**: 主要解决在 Docker 容器等虚拟化环境中参考系统不可用的问题
- **测试依赖**: 被装饰的测试函数必须依赖于参考系统功能，否则不应使用此装饰器
- **pytest 集成**: 与 pytest 的 skip 机制完全兼容，跳过时会显示明确的跳过原因

## 相关函数

- **skip_if_32bit**: 底层实现函数，提供通用的 32 位系统跳过功能
- **requires_gpu**: 类似的装饰器，用于跳过没有 GPU 支持的测试
- **skip_if_llvm_version**: 基于 LLVM 版本跳过的装饰器
- **pytest.mark.skipif**: pytest 原生的条件跳过装饰器