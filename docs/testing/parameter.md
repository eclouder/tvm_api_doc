---
title: parameter
description: 用于定义pytest参数化测试fixture的便捷函数，特别适用于无设置成本的简单参数值
---

# parameter

## 概述

`tvm.testing.parameter` 是TVM测试框架中的一个核心工具函数，专门用于简化pytest参数化测试的创建过程。该函数允许开发者通过声明式的方式定义测试参数，自动生成对应的pytest fixture，使得测试函数能够针对不同的参数值自动运行多次。

在TVM测试流程中，该函数主要用于：
- 为算子测试提供不同的输入形状和数据类型
- 为设备后端测试配置不同的目标平台
- 为性能测试设置不同的工作负载大小
- 简化多参数组合测试的编写

该函数与 `tvm.testing.fixture` 形成互补，前者适用于无设置成本的简单参数，后者适用于需要复杂初始化或资源管理的场景。

## 函数签名

```python
def parameter(*values, ids=None, by_dict=None):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| values | Any | 参数值列表，测试函数将针对每个参数值运行一次 | - |
| ids | List[str], optional | 参数名称列表，用于在测试报告中标识不同的参数值 | None |
| by_dict | Dict[str, Any] | 通过字典形式同时设置参数值和名称，键为参数名，值为参数值 | None |

## 返回值

**类型:** `function`

返回一个pytest fixture函数，该函数可以在测试函数中作为参数使用。当测试运行时，pytest会自动为每个参数值调用一次测试函数。

## 使用场景

### 单元测试
为TVM算子测试提供不同的输入配置，如数据类型、张量形状等。

### 设备测试
测试在不同目标设备（CPU、GPU、CUDA、OpenCL等）上的行为一致性。

### 性能测试
通过不同规模的工作负载测试编译器的性能表现。

### 集成测试
验证TVM在不同配置下的端到端工作流程。

## 使用示例

### 基本用法
```python
import tvm.testing

# 定义简单的数值参数
batch_size = tvm.testing.parameter(1, 4, 16)

def test_matmul(batch_size):
    # 使用batch_size参数创建测试数据
    A = tvm.nd.array(np.random.rand(batch_size, 64, 128))
    B = tvm.nd.array(np.random.rand(batch_size, 128, 256))
    # 执行矩阵乘法测试
    # ...
```

### 使用ids参数提高可读性
```python
import tvm.testing

# 定义不同目标设备
target = tvm.testing.parameter(
    "llvm", 
    "cuda", 
    "opencl",
    ids=['cpu', 'gpu_cuda', 'gpu_opencl']
)

def test_device_specific_kernel(target):
    # 针对不同设备编译和运行内核
    with tvm.target.Target(target):
        # 编译和测试代码
        # ...
```

### 使用字典形式定义参数
```python
import tvm.testing

# 通过字典定义复杂参数
dtype_config = tvm.testing.parameter(by_dict={
    'float32': 'float32',
    'float16': 'float16', 
    'int8': 'int8'
})

def test_dtype_operations(dtype_config):
    # 测试不同数据类型的操作
    data = tvm.nd.array(np.random.rand(10, 10).astype(dtype_config))
    # 执行数据类型相关的测试
    # ...
```

### 多参数组合测试
```python
import tvm.testing

# 定义多个参数
data_type = tvm.testing.parameter('float32', 'float16')
tensor_shape = tvm.testing.parameter((32, 32), (64, 64))
target_device = tvm.testing.parameter('llvm', 'cuda')

def test_tensor_operations(data_type, tensor_shape, target_device):
    # 这个测试将运行 2 × 2 × 2 = 8 次
    # 测试不同数据类型、形状和设备组合
    A = tvm.nd.array(np.random.rand(*tensor_shape).astype(data_type))
    B = tvm.nd.array(np.random.rand(*tensor_shape).astype(data_type))
    
    with tvm.target.Target(target_device):
        # 编译和执行操作
        # ...
```

## 注意事项

- **性能考虑**: 仅适用于无设置成本或设置成本很低的参数，如基本数据类型、元组、字符串等。对于需要复杂初始化或资源分配的场景，请使用 `tvm.testing.fixture`

- **作用域**: 定义的参数具有session级别的作用域，在整个测试会话中共享

- **参数覆盖**: 如果特定测试需要不同的参数值，可以使用 `@pytest.mark.parametrize` 标记来覆盖模块级别的参数定义

- **参数冲突**: `by_dict` 参数不能与位置参数同时使用，否则会抛出 `RuntimeError`

- **TVM版本兼容性**: 该函数在TVM 0.8及以上版本中稳定可用

## 相关函数

- [`tvm.testing.fixture`](./fixture): 用于定义需要复杂设置或资源管理的测试fixture
- [`tvm.testing.uses_gpu`](./uses_gpu): 标记需要GPU设备的测试
- [`tvm.testing.skip_if`](./skip_if): 根据条件跳过特定测试
- `pytest.mark.parametrize`: pytest原生的参数化装饰器，用于更细粒度的参数控制