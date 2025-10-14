---
title: fixture
description: 用于定义pytest测试夹具的装饰器函数，在TVM测试框架中用于管理测试前的状态设置和资源共享
---

# fixture

## 概述

`fixture` 是 TVM 测试框架中一个核心的装饰器函数，专门用于定义 pytest 测试夹具。在 TVM 的测试生态系统中，该函数扮演着关键角色，帮助开发者管理测试前的状态设置、资源分配和参数化测试。

主要功能包括：
- 将普通函数标记为 pytest 夹具，使其返回值可以在测试函数中作为参数使用
- 支持与 `tvm.testing.parameter` 配合实现参数化测试
- 提供返回值缓存机制，优化昂贵的测试设置过程
- 与 TVM 的目标平台和设备管理无缝集成

该函数是 TVM 测试工具链的重要组成部分，确保了测试的独立性、可重复性和性能优化。

## 函数签名

```python
def fixture(func=None, *, cache_return_value=False):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| func | function | 要转换为夹具的函数对象 | None |
| cache_return_value | bool | 是否缓存夹具的返回值。当设置为 True 时，相同的夹具参数组合只会执行一次，后续测试复用缓存结果 | False |

## 返回值

**类型:** `function`

返回一个经过包装的 pytest 夹具函数。该函数具有与原始函数相同的签名，但被注册到 pytest 的夹具系统中，可以在测试函数中作为参数使用。

## 使用场景

### 单元测试
为 TVM 算子和图优化提供可重用的测试环境和数据准备

### 集成测试
管理跨多个模块的复杂测试设置，如编译流水线的完整测试

### 性能测试
缓存昂贵的基准测试设置，避免重复执行耗时的初始化过程

### 目标平台测试
为不同的目标平台（CPU、GPU、加速器）创建特定的测试环境配置

## 使用示例

### 基本用法
```python
import tvm.testing

@tvm.testing.fixture
def simple_setup():
    """简单的测试夹具，返回固定值"""
    return {"data": np.random.rand(100, 100), "threshold": 0.5}

def test_relu_operation(target, dev, simple_setup):
    """测试ReLU操作，使用夹具提供的数据"""
    data = simple_setup["data"]
    threshold = simple_setup["threshold"]
    
    # 构建TVM计算图并测试
    A = te.placeholder(data.shape, name="A")
    B = te.compute(A.shape, lambda *i: tvm.te.if_then_else(A(*i) > threshold, A(*i), 0.0))
    s = te.create_schedule(B.op)
    
    # 在目标设备上运行测试
    # ... 测试实现代码
```

### 参数化夹具
```python
import tvm.testing

# 定义参数
dtype = tvm.testing.parameter("float32", "float64")
shape = tvm.testing.parameter((32, 32), (64, 64))

@tvm.testing.fixture
def tensor_setup(dtype, shape):
    """基于参数的夹具，为不同数据类型和形状创建张量"""
    return tvm.nd.array(np.random.rand(*shape).astype(dtype))

def test_matmul_operation(tensor_setup):
    """测试矩阵乘法，使用参数化夹具"""
    input_tensor = tensor_setup
    # 执行矩阵乘法测试
    # ... 测试实现代码
```

### 缓存昂贵设置
```python
import tvm.testing
import time

@tvm.testing.fixture(cache_return_value=True)
def expensive_model_setup():
    """缓存昂贵的模型加载和编译过程"""
    print("正在加载和编译模型...")
    time.sleep(5)  # 模拟耗时的模型编译
    
    # 实际TVM代码：加载预训练模型并编译
    # mod = tvm.ir.load_json("model.json")
    # params = tvm.runtime.load_params("model.params")
    # built = tvm.build(mod, target="llvm")
    
    return {"model": "compiled_model", "params": "loaded_params"}

def test_model_inference(target, dev, expensive_model_setup):
    """测试模型推理，复用缓存的编译结果"""
    model_info = expensive_model_setup
    # 使用编译好的模型进行推理测试
    assert model_info["model"] == "compiled_model"
```

## 注意事项

### 缓存行为
- 当 `cache_return_value=True` 时，相同的夹具参数组合只会执行一次
- 可以通过设置环境变量 `TVM_TEST_DISABLE_CACHE=1` 强制禁用缓存功能
- 缓存的作用域为函数级别，确保测试间的独立性

### 与pytest集成
- 该函数是对 pytest 原生 `@pytest.fixture` 的封装，添加了 TVM 特定的功能
- 夹具的作用域固定为 "function"，确保每个测试函数都有独立的环境

### 参数化测试
- 夹具函数可以接受使用 `tvm.testing.parameter` 定义的参数
- 每个参数组合都会生成独立的夹具实例

### 设备管理
- 在 TVM 测试中，夹具经常与 `target` 和 `dev` 参数配合使用
- 确保测试在正确的目标设备和运行时上执行

## 相关函数

### 核心测试函数
- `tvm.testing.parameter` - 定义参数化测试的参数
- `tvm.testing.uses_gpu` - 检查测试是否使用GPU设备

### pytest集成
- `pytest.fixture` - 底层的pytest夹具装饰器
- `pytest.mark.parametrize` - pytest原生的参数化装饰器

### TVM测试工具
- `tvm.testing.assert_allclose` - 张量值比较断言
- `tvm.testing.measure_performance` - 性能测量工具