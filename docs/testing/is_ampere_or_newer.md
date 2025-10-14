---
title: is_ampere_or_newer
description: 检查目标环境是否具有NVIDIA Ampere架构或更新的GPU，用于TVM测试中的条件执行
---

# is_ampere_or_newer

## 概述

`is_ampere_or_newer` 是一个TVM测试工具函数，专门用于检测当前运行环境中的NVIDIA GPU计算能力。该函数通过查询CUDA计算版本，判断GPU是否为Ampere架构（计算能力8.x）或更新的架构。

在TVM测试框架中，此函数主要用于：
- **条件测试执行**：根据GPU架构决定是否运行特定的测试用例
- **功能兼容性检查**：确保测试只在支持特定特性的GPU上运行
- **性能基准测试**：针对不同GPU架构执行相应的性能测试

该函数是TVM设备目标检测工具链的重要组成部分，与`tvm.contrib.nvcc`模块紧密集成，为跨平台测试提供硬件能力识别支持。

## 函数签名

```python
def is_ampere_or_newer():
```

## 参数

此函数不接受任何参数。

## 返回值

**类型:** `bool`

返回布尔值，表示当前环境的GPU是否为Ampere架构或更新的架构：
- `True`：GPU计算能力主版本号 ≥ 8 且次版本号 ≠ 9
- `False`：GPU计算能力不满足上述条件

## 使用场景

### 单元测试
在编写与GPU架构相关的单元测试时，使用此函数确保测试只在兼容的硬件上运行。

### 集成测试
验证TVM在不同GPU架构上的编译和执行行为，特别是针对Ampere架构的新特性。

### 性能测试
针对特定GPU架构的性能优化测试，避免在不支持的设备上运行导致测试失败。

### 目标平台验证
在CI/CD流水线中自动检测测试环境的GPU能力，确保测试环境的正确配置。

## 使用示例

```python
import tvm.testing

# 基本用法：检查GPU架构
if tvm.testing.is_ampere_or_newer():
    print("当前环境支持Ampere或更新的GPU架构")
    # 执行Ampere架构特定的测试
    run_ampere_specific_tests()
else:
    print("当前GPU架构较旧，跳过Ampere特定测试")
    # 执行通用测试或跳过
    run_generic_tests()

# 在pytest中的条件跳过示例
@pytest.mark.skipif(
    not tvm.testing.is_ampere_or_newer(),
    reason="需要Ampere或更新的GPU架构"
)
def test_tensor_core_operations():
    """测试Ampere架构的Tensor Core操作"""
    # 测试代码...
    pass

# 在TVM测试框架中的实际应用
def test_cutlass_ampere_kernels():
    if not tvm.testing.is_ampere_or_newer():
        pytest.skip("测试需要Ampere架构GPU")
    
    # 编译和运行针对Ampere架构优化的kernel
    # ...
```

## 注意事项

- **CUDA环境要求**：函数需要正确配置的CUDA环境和可用的NVIDIA GPU
- **版本兼容性**：该函数依赖于`tvm.contrib.nvcc`模块，需要TVM编译时启用CUDA支持
- **计算能力排除**：特别排除了计算能力8.9的版本，这可能是预发布或特殊版本
- **错误处理**：如果CUDA环境不可用，底层函数可能抛出异常，建议在测试中适当处理
- **多GPU环境**：函数检测的是默认GPU的计算能力，在多GPU环境中可能需要额外处理

## 相关函数

- `tvm.contrib.nvcc.get_target_compute_version()` - 获取目标计算版本
- `tvm.contrib.nvcc.parse_compute_version()` - 解析计算版本字符串
- `tvm.testing.requires_cuda()` - 检查CUDA可用性的装饰器
- `tvm.testing.requires_gpu()` - 检查GPU可用性的装饰器

这些函数共同构成了TVM的设备能力检测工具集，为跨平台测试提供完整的硬件兼容性支持。