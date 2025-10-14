---
title: requires_nvcc_version
description: 用于标记需要特定版本NVCC编译器的TVM测试用例的装饰器函数
---

# requires_nvcc_version

## 概述

`requires_nvcc_version` 是 TVM 测试框架中的一个装饰器函数，主要用于在单元测试中标记对 NVCC 编译器版本的要求。该函数的主要作用是：

- **版本检查**：自动检测系统中安装的 NVCC 版本，并与指定的最低版本要求进行比较
- **条件跳过**：当系统不满足指定的 NVCC 版本要求时，自动跳过相关测试用例
- **CUDA 依赖**：隐式标记测试用例需要 CUDA 支持，继承 `requires_cuda` 的所有功能

该装饰器在 TVM 的 GPU 相关测试中扮演重要角色，确保测试用例只在具备足够新版本的 NVCC 编译器的环境中执行，避免因编译器版本不兼容导致的测试失败。

## 函数签名

```python
def requires_nvcc_version(major_version, minor_version=0, release_version=0):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| major_version | int | NVCC 版本号的主版本号，如 11.0 中的 11 | 无默认值（必需） |
| minor_version | int | NVCC 版本号的次版本号，如 11.0 中的 0 | 0 |
| release_version | int | NVCC 版本号的发布版本号，通常用于补丁版本 | 0 |

## 返回值

**类型:** `function` (装饰器)

返回一个 pytest 装饰器，该装饰器会包装原始测试函数，添加版本检查逻辑和 CUDA 依赖标记。

## 使用场景

该函数主要应用于以下 TVM 测试场景：

- **CUDA 功能测试**：测试需要特定 CUDA 版本支持的新功能
- **编译器特性验证**：验证依赖新版本 NVCC 特性的 TVM 功能
- **版本兼容性测试**：确保 TVM 在不同 NVCC 版本下的行为一致性
- **GPU 代码生成测试**：测试依赖特定 NVCC 版本的 GPU 内核生成功能

## 使用示例

```python
import tvm.testing
import pytest

# 基本用法：要求 NVCC 11.0 或更高版本
@tvm.testing.requires_nvcc_version(11, 0)
def test_cuda_11_feature():
    """测试需要 CUDA 11.0 及以上版本的功能"""
    # 测试代码实现
    pass

# 精确版本要求：要求 NVCC 11.2.1 或更高版本
@tvm.testing.requires_nvcc_version(11, 2, 1)
def test_specific_cuda_feature():
    """测试需要 CUDA 11.2.1 及以上版本的特定功能"""
    # 测试代码实现
    pass

# 与其他测试装饰器组合使用
@tvm.testing.requires_nvcc_version(11, 0)
@pytest.mark.parametrize("dtype", ["float32", "float64"])
def test_cuda_kernels_with_dtypes(dtype):
    """测试不同数据类型的 CUDA 内核生成"""
    # 测试代码实现
    pass
```

## 注意事项

- **自动 CUDA 依赖**：使用此装饰器会自动包含 `requires_cuda` 的所有要求，无需额外添加 CUDA 依赖标记
- **版本比较逻辑**：版本比较使用标准的元组比较 `(major, minor, release)`，要求系统版本 >= 指定版本
- **NVCC 检测失败**：如果无法检测到 NVCC 版本，函数会假定版本为 (0, 0, 0)，导致测试被跳过
- **测试跳过原因**：当测试被跳过时，pytest 会显示清晰的原因信息，如 "Requires NVCC >= 11.0"
- **平台限制**：此装饰器主要在 Linux 和 Windows 平台上有效，需要正确配置 CUDA 环境变量

## 相关函数

- **requires_cuda**：标记需要 CUDA 支持的测试用例
- **requires_gpu**：标记需要 GPU 设备的测试用例  
- **skipif**：pytest 的条件跳过装饰器
- **parametrize**：pytest 的参数化测试装饰器

该装饰器通常与上述函数配合使用，构建完整的 TVM GPU 测试套件。