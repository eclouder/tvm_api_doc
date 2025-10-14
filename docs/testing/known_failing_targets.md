---
title: known_failing_targets
description: 用于标记在特定目标平台上已知会失败的测试用例的装饰器函数
---

# known_failing_targets

## 概述

`known_failing_targets` 是 TVM 测试框架中的一个装饰器函数，主要用于处理跨多个目标平台和设备（包括 CPU 和 GPU 设备）运行测试时，某些特定目标平台存在已知问题的情况。该函数通过为指定的目标平台应用 `pytest.mark.xfail` 标记，允许测试在这些平台上预期失败但仍然继续执行，从而确保测试套件能够全面覆盖所有目标平台，同时准确反映各平台的当前支持状态。

在 TVM 的测试流程中，该函数位于目标设备和平台测试层，与 TVM 的自动化测试基础设施紧密集成。它特别适用于新开发的功能或运行时环境尚未完全支持所有特性的过渡期，帮助开发团队识别和跟踪特定平台的兼容性问题。

## 函数签名

```python
def known_failing_targets(*args):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| *args | str | 可变参数，接受一个或多个目标平台名称字符串，指定已知会失败的测试目标 | 无 |

## 返回值

**类型:** `function`

返回一个装饰器函数，该装饰器会为被装饰的测试函数添加 `tvm_known_failing_targets` 属性，记录已知失败的目标平台列表。TVM 的测试框架会在运行时读取此属性，并为相应的目标平台应用预期的失败标记。

## 使用场景

### 单元测试与集成测试
- 当新功能仅在部分目标平台上实现完整支持时
- 在开发过程中识别特定硬件后端的限制

### 目标平台兼容性测试
- 验证不同后端（如 LLVM、CUDA、OpenCL 等）的功能支持度
- 跟踪各平台的功能实现进度和问题状态

### 持续集成环境
- 在 CI/CD 流水线中确保测试能够全面运行，即使某些平台存在已知问题
- 提供清晰的测试结果报告，区分真正的失败和预期的失败

## 使用示例

```python
import tvm.testing

# 标记在 CUDA 平台上已知会失败的测试
@tvm.testing.known_failing_targets("cuda")
def test_tensor_operations(target, dev):
    # 测试张量操作的代码
    # 在除 CUDA 外的其他平台上正常测试
    # 在 CUDA 平台上会被标记为预期失败
    pass

# 标记在多个平台上已知会失败的测试
@tvm.testing.known_failing_targets("llvm", "cuda", "opencl")
def test_runtime_feature(target, dev):
    # 测试新运行时特性的代码
    # 在指定的三个平台上会被标记为预期失败
    # 在其他支持的平台上正常执行
    pass

# 与参数化测试结合使用
@pytest.mark.parametrize("target,dev", tvm.testing.enabled_targets())
@tvm.testing.known_failing_targets("vulkan")
def test_complex_kernel(target, dev):
    # 在所有启用的目标平台上运行测试
    # 但在 Vulkan 平台上预期会失败
    # 这有助于识别 Vulkan 后端的特定问题
    pass
```

## 注意事项

- **测试函数格式要求**: 被装饰的测试函数必须遵循 `def test_xxxxxxxxx(target, dev):` 的签名格式，其中 `xxxxxxxxx` 可以是任何有效的测试名称
- **目标平台名称**: 使用的目标平台名称必须与 TVM 支持的目标名称一致，如 "llvm"、"cuda"、"rocm"、"opencl"、"metal"、"vulkan" 等
- **预期失败 vs 实际失败**: 被标记的测试在指定平台上会显示为预期失败（xfail），而不是测试失败，这有助于区分已知问题和新增问题
- **测试覆盖完整性**: 即使某些平台存在已知问题，使用此装饰器仍能确保测试在所有平台上运行，保持测试覆盖的完整性

## 相关函数

- **`tvm.testing.skipif`**: 根据条件跳过测试的执行
- **`tvm.testing.parametrize_targets`**: 为测试函数参数化不同的目标平台
- **`tvm.testing.enabled_targets`**: 获取当前启用的目标平台列表
- **`pytest.mark.xfail`**: pytest 原生的预期失败标记函数

该函数与 TVM 的目标设备管理系统紧密配合，确保测试框架能够准确反映各硬件后端的实际支持状态，为开发人员提供清晰的平台兼容性视图。