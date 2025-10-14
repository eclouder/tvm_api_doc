---
title: requires_package
description: 用于标记需要特定Python包才能运行的TVM测试的装饰器函数
---

# requires_package

## 概述

`requires_package` 是 TVM 测试框架中的一个装饰器函数，主要用于标记那些依赖特定 Python 包的单元测试。当测试用例需要额外的第三方库支持时，使用此装饰器可以确保在缺少必要依赖的情况下自动跳过测试，而不是导致测试失败。

该函数在 TVM 的测试流程中扮演着重要的角色：
- 自动检测测试环境中的包依赖
- 提供清晰的跳过测试原因说明
- 与 pytest 测试框架无缝集成
- 支持同时检查多个包的可用性

## 函数签名

```python
def requires_package(*packages):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| packages | 可变参数 (str) | 测试运行所需的Python包名列表，可以传入一个或多个包名 | 无 |

## 返回值

**类型:** `function`

返回一个 pytest 装饰器包装器，该包装器会为测试函数应用相应的跳过条件标记。当装饰的函数被调用时，如果指定的包不可用，pytest 会自动跳过该测试。

## 使用场景

### 单元测试
当测试用例依赖于特定的数据处理库（如 `pandas`、`numpy`）或机器学习框架时。

### 集成测试
在需要与外部系统交互的测试中，如数据库连接、云服务SDK等。

### 目标平台测试
针对特定硬件加速器或运行时环境的测试，需要相应的驱动或库支持。

### 可选功能测试
测试 TVM 的可选功能模块，这些模块可能依赖额外的第三方包。

## 使用示例

```python
import tvm.testing
import pytest

# 单个包依赖检查
@tvm.testing.requires_package("torch")
def test_torch_integration():
    """测试TVM与PyTorch的集成功能"""
    import torch
    # 测试代码...

# 多个包依赖检查
@tvm.testing.requires_package("tensorflow", "keras")
def test_tf_keras_models():
    """测试TensorFlow和Keras模型转换"""
    import tensorflow as tf
    import keras
    # 测试代码...

# 在类中使用
class TestMLFramework:
    @tvm.testing.requires_package("scipy")
    def test_scientific_computing(self):
        """测试科学计算相关功能"""
        import scipy
        # 测试代码...

# 与TVM目标设备测试结合
@tvm.testing.parametrize_targets("llvm", "cuda")
@tvm.testing.requires_package("cupy")
def test_gpu_accelerated_operations(target, dev):
    """测试GPU加速操作，需要CuPy支持"""
    import cupy as cp
    # 特定于GPU的测试代码...
```

## 注意事项

- **导入时机**: 包的导入检查发生在装饰器应用时，而不是测试运行时
- **包名准确性**: 必须使用正确的Python包导入名称，可能与pip安装的名称不同
- **嵌套使用**: 可以与其他pytest装饰器（如 `@pytest.mark.parametrize`）组合使用
- **错误信息**: 当测试被跳过时，pytest会显示清晰的原因信息，如 "Cannot import 'package_name'"
- **性能影响**: 装饰器只在测试收集阶段执行一次，不会影响测试运行时的性能

## 相关函数

- **`tvm.testing.requires_cuda`**: 检查CUDA可用性的专用装饰器
- **`tvm.testing.requires_gpu`**: 检查GPU支持的装饰器
- **`pytest.importorskip`**: pytest原生的导入跳过函数
- **`tvm.testing.enabled_targets`**: TVM目标设备过滤函数

该装饰器与TVM的多目标测试框架紧密结合，可以确保测试在正确的环境和依赖条件下运行，提高了测试的可靠性和可维护性。