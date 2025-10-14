---
title: requires_cuda_compute_version
description: 用于标记需要特定CUDA计算能力的TVM单元测试的装饰器函数
---

# requires_cuda_compute_version

## 概述

`requires_cuda_compute_version` 是TVM测试框架中的一个装饰器函数，主要用于根据CUDA GPU的计算能力版本对测试用例进行条件性执行控制。该函数会检查当前环境的CUDA计算架构版本，如果低于指定的最低要求版本，则自动跳过相应的测试用例。

在TVM测试流程中，该函数位于测试用例筛选和条件执行的关键环节，与`requires_cuda`等其他测试装饰器协同工作，确保测试用例只在具备足够计算能力的CUDA设备上运行。这对于测试依赖于特定硬件特性的功能（如Tensor Core操作、特定架构的优化等）尤为重要。

## 函数签名

```python
def requires_cuda_compute_version(major_version, minor_version=0):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| major_version | int | CUDA计算架构的主版本号，表示所需的最低计算能力主版本 | 无 |
| minor_version | int | CUDA计算架构的次版本号，表示所需的最低计算能力次版本 | 0 |

## 返回值

**类型:** `function`

返回一个装饰器函数，该装饰器会将原测试函数包装为仅在满足CUDA计算版本要求时执行的测试用例。如果计算版本不满足要求，测试将被标记为跳过。

## 使用场景

### 单元测试
在编写依赖于特定CUDA架构特性的单元测试时使用，确保测试只在支持该特性的硬件上运行。

### 目标平台测试
验证TVM在不同CUDA计算能力设备上的正确性和性能表现。

### 功能验证测试
测试TVM中依赖于特定CUDA计算版本的功能，如：
- Ampere架构的稀疏张量支持
- Volta架构的Tensor Core操作
- Pascal架构的FP16支持

## 使用示例

```python
import tvm.testing
import pytest

# 测试需要CUDA计算能力7.0及以上（Volta架构）
@tvm.testing.requires_cuda_compute_version(7, 0)
def test_tensor_core_operations():
    """测试依赖于Volta架构Tensor Core的操作"""
    # 使用TVM构建和运行Tensor Core相关的计算图
    # 如果GPU计算能力低于7.0，此测试将自动跳过
    
# 测试需要CUDA计算能力8.0及以上（Ampere架构）
@tvm.testing.requires_cuda_compute_version(8, 0)
def test_sparse_tensor_operations():
    """测试Ampere架构的稀疏张量支持"""
    # 稀疏张量操作代码
    # 如果GPU计算能力低于8.0，此测试将自动跳过

# 组合使用多个装饰器
@pytest.mark.parametrize("dtype", ["float16", "float32"])
@tvm.testing.requires_cuda_compute_version(7, 0)
def test_mixed_precision_operations(dtype):
    """参数化测试与计算版本要求的组合使用"""
    # 测试代码
```

## 注意事项

- **硬件依赖**: 该装饰器仅在具有CUDA GPU的环境中有效，在没有GPU的环境中所有相关测试都会被跳过
- **版本检查**: 函数会自动检测当前GPU的CUDA计算版本，并与指定版本进行比较
- **组合使用**: 可以与其他pytest装饰器（如`@pytest.mark.parametrize`）组合使用，但需要注意装饰器的应用顺序
- **错误处理**: 如果无法检测到GPU或解析计算版本，函数会默认将计算版本设为(0, 0)，导致测试被跳过
- **TVM版本兼容性**: 该功能依赖于`tvm.contrib.nvcc`模块，确保使用的TVM版本包含完整的CUDA支持

## 相关函数

- **requires_cuda**: 检查CUDA可用性的基础装饰器
- **requires_gpu**: 检查GPU可用性的通用装饰器  
- **@pytest.mark.skipif**: pytest原生的条件跳过装饰器
- **tvm.contrib.nvcc.get_target_compute_version()**: 获取CUDA目标计算版本的底层函数

该装饰器通过自动化的硬件能力检测，大大简化了TVM跨不同CUDA架构的测试管理，确保了测试的准确性和可靠性。