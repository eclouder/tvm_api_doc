---
title: device_enabled
description: 检查指定目标设备是否在TVM测试环境中启用，用于条件执行设备相关的测试代码
---

# device_enabled

## 概述

`device_enabled` 是TVM测试框架中的一个核心工具函数，主要用于在测试过程中动态检查特定的目标设备是否在当前测试环境中可用和启用。该函数在TVM的跨平台测试策略中扮演重要角色，允许测试代码根据实际可用的硬件设备条件执行相应的测试逻辑。

在TVM的测试生态中，该函数通常与 `@tvm.testing.uses_gpu` 等装饰器配合使用，实现测试代码在不同目标设备（如CPU、GPU、加速器等）上的条件执行。通过解析目标字符串并与当前环境中实际可运行的设备进行匹配，确保测试只在具备相应硬件支持的节点上运行。

## 函数签名

```python
def device_enabled(target):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| target | str | 目标设备字符串，如 "cuda"、"llvm"、"opencl" 等 | 无 |

## 返回值

**类型:** `bool`

返回布尔值，表示指定的目标设备是否在当前测试环境中启用。`True` 表示设备可用且已启用，`False` 表示设备不可用或未启用。

## 使用场景

### 单元测试
在编写设备相关的单元测试时，使用该函数确保测试代码只在支持的目标设备上执行，避免在不支持的设备上出现测试失败。

### 集成测试
在跨设备集成测试中，根据实际可用的硬件资源动态调整测试范围，提高测试的灵活性和可移植性。

### 目标平台测试
在验证TVM对不同硬件后端的支持时，使用该函数进行设备可用性检查，确保测试套件能够适应不同的部署环境。

### 性能测试
在设备相关的性能基准测试中，只在实际可用的设备上运行性能测试代码。

## 使用示例

```python
import tvm.testing

# 基本用法：检查设备是否启用
def test_device_availability():
    if tvm.testing.device_enabled("cuda"):
        print("CUDA设备可用，执行GPU相关测试")
        # 执行CUDA特定的测试逻辑
    else:
        print("CUDA设备不可用，跳过GPU测试")

# 在参数化测试中使用
@tvm.testing.uses_gpu
def test_matrix_operations():
    targets_to_test = ["llvm", "cuda", "opencl"]
    
    for target in targets_to_test:
        if tvm.testing.device_enabled(target):
            print(f"在 {target} 设备上运行测试")
            # 构建针对该目标的测试计算图
            # 执行设备特定的验证逻辑
        else:
            print(f"跳过 {target} 设备测试")

# 与pytest参数化结合使用
import pytest

@pytest.mark.parametrize("target", ["llvm", "cuda", "vulkan"])
def test_compile_and_run(target):
    if not tvm.testing.device_enabled(target):
        pytest.skip(f"目标设备 {target} 未启用")
    
    # 只有设备启用时才执行测试主体
    # 编译和运行TVM计算图
```

## 注意事项

- **目标字符串格式**：函数会自动解析目标字符串，只检查目标种类（target kind），忽略额外的编译标志。例如，对于 "cuda -arch=sm_70"，函数只检查 "cuda" 部分。
- **测试环境依赖**：函数的返回值完全依赖于当前测试环境的设备配置，同一测试代码在不同环境中可能有不同的行为。
- **推荐使用模式**：建议优先使用 `tvm.testing.parametrize_targets` 装饰器进行目标参数化，而不是手动调用此函数。
- **性能考虑**：在循环中频繁调用此函数可能影响测试性能，建议在测试开始时进行设备检查并缓存结果。
- **TVM版本兼容性**：该函数在TVM 0.8及以上版本中保持稳定，但内部实现可能随TVM设备管理机制的改进而优化。

## 相关函数

- **`tvm.testing.parametrize_targets`**：推荐的目标参数化装饰器，自动处理设备启用检查
- **`tvm.testing.uses_gpu`**：标记测试需要使用GPU设备的装饰器
- **`_get_targets()`**：内部函数，获取当前环境中所有可运行的目标设备列表
- **`tvm.testing.enabled_targets()`**：获取所有已启用的目标设备列表

该函数是TVM测试框架中设备感知测试的基础构建块，为编写健壮的跨平台测试代码提供了重要支持。