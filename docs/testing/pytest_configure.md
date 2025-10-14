---
title: pytest_configure
description: 在pytest配置阶段执行，用于注册TVM测试标记和输出测试环境信息
---

# pytest_configure

## 概述

`pytest_configure` 是TVM测试框架与pytest集成的核心配置函数，在pytest初始化配置阶段自动调用。该函数主要负责：

- **注册TVM功能标记**：为所有TVM支持的功能特性（如CUDA、OpenCL、Metal等）在pytest中注册相应的标记（markers）
- **输出测试环境信息**：在测试开始时打印当前启用的目标平台和pytest标记表达式，便于调试和验证测试配置
- **测试框架集成**：作为TVM测试插件的一部分，确保TVM特定的测试功能能够与pytest框架无缝协作

该函数在TVM测试流程的初始化阶段执行，为后续的测试用例执行提供必要的环境配置和标记支持。

## 函数签名

```python
def pytest_configure(config):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| config | `pytest.Config` | pytest配置对象，用于访问和修改pytest的配置选项 | 无 |

## 返回值

**类型:** `None`

该函数不返回任何值，其主要作用是通过副作用完成测试环境的配置。

## 使用场景

### 单元测试和集成测试
- 在运行TVM单元测试时自动配置测试环境
- 为不同的硬件后端（CPU、GPU等）注册相应的测试标记

### 目标平台测试
- 支持多平台测试，根据可用硬件自动启用相应的测试标记
- 在测试输出中显示当前激活的目标平台，便于问题诊断

### 功能特性测试
- 为TVM的各种功能特性（如自动调度、量化等）提供标记支持
- 允许通过pytest标记表达式选择性运行特定功能测试

## 使用示例

```python
# 该函数由pytest自动调用，无需手动调用
# 但在运行测试时可以通过命令行查看其效果

# 运行所有启用了CUDA的测试
# pytest -m "cuda" tvm/tests/python/relay/

# 运行时会看到类似输出：
# enabled targets: llvm; cuda
# pytest marker: cuda

# 查看所有可用的TVM测试标记
# pytest --markers tvm/tests/python/relay/
```

## 注意事项

- **自动执行**：该函数由pytest框架自动调用，开发者通常不需要手动调用
- **配置时机**：在pytest初始化阶段执行，早于任何测试用例的运行
- **标记注册**：所有TVM功能特性的标记都在此阶段注册，确保测试用例可以使用这些标记
- **环境依赖**：输出的"enabled targets"取决于当前环境的硬件配置和TVM编译选项

## 相关函数

- `tvm.testing.utils.enabled_targets()` - 获取当前环境中启用的目标平台列表
- `tvm.testing.utils.Feature` - TVM功能特性管理类
- `pytest` 框架的相关配置函数

## 与TVM目标平台的关系

该函数输出的"enabled targets"信息直接反映了TVM在当前测试环境中支持的目标平台：
- **LLVM**：CPU后端支持
- **CUDA**：NVIDIA GPU支持  
- **OpenCL**：跨平台GPU支持
- **Metal**：Apple设备GPU支持
- **Vulkan**：新一代图形API支持

这些目标平台信息对于理解和调试TVM在不同硬件上的测试行为至关重要。