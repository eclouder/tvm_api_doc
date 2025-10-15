---
title: PartitionTransformParams Pass
description: TVM Relax 中用于分离变换参数的优化 Pass，将模型参数与计算逻辑分离以便更高效地部署。
---

# PartitionTransformParams Pass

## 概述

`PartitionTransformParams` 是 TVM Relax 中的一个变换 Pass，主要功能是将模型中的变换参数（如权重参数）从计算图中分离出来。该 Pass 通过识别和提取模型中的可提升参数，创建独立的运行时函数和变换函数，从而优化模型的部署和执行效率。

## 函数签名

```cpp
Pass PartitionTransformParams(ffi::Variant<Bool, ffi::Array<ffi::String>> shared_transform)
```

## 参数说明

### shared_transform
- **类型**: `ffi::Variant<Bool, ffi::Array<ffi::String>>`
- **描述**: 控制参数共享策略的配置选项
  - 当为 `Bool` 类型时：
    - `true`: 启用全局参数共享，所有目标函数共享同一个变换参数函数
    - `false`: 禁用全局参数共享，每个函数生成独立的变换参数函数
  - 当为 `ffi::Array<ffi::String>` 类型时：指定要应用该 Pass 的特定函数名称列表

## 实现原理

该 Pass 的核心实现逻辑分为以下几个步骤：

### 1. 目标函数识别
通过 `GetTargetFunctions` 函数根据 `shared_transform` 参数识别需要处理的目标函数集合。

### 2. 全局收集信息构建（可选）
当启用全局参数共享时（`shared_transform` 为 `true`），调用 `MakeGlobalLiftPlan` 函数构建全局的可提升参数信息，用于跨函数共享参数变换逻辑。

### 3. 局部收集信息收集
对于每个目标函数，使用 `LocalLiftableBindingCollector::Collect` 收集函数内部的局部可提升绑定信息：
- 识别函数中的常量参数和可提升的中间结果
- 如果启用了全局收集，会参考全局信息进行更优化的参数提取

### 4. 运行时函数生成
基于收集到的局部信息，为每个函数生成更新后的运行时函数：
```cpp
auto new_runtime_func = info.MakeRuntimeFunction();
updated_runtime_functions->Add(gvar, new_runtime_func);
```

### 5. 变换函数生成
根据是否启用全局共享，生成不同的变换参数函数：
- **全局共享模式**: 生成统一的 `transform_params` 函数
- **局部模式**: 为每个函数生成独立的 `{function_name}_transform_params` 函数

## 优化效果

该 Pass 带来的主要优化效果包括：

1. **内存优化**: 将参数从计算图中分离，减少运行时内存占用
2. **部署优化**: 分离的参数可以预先处理或优化，提高部署效率
3. **代码复用**: 在全局共享模式下，多个函数可以共享参数变换逻辑
4. **执行效率**: 简化后的运行时函数执行更高效

## 使用场景

`PartitionTransformParams` Pass 适用于以下场景：

1. **模型部署**: 在将模型部署到目标设备前，分离参数以便更好地管理内存
2. **多函数模块**: 处理包含多个相关函数的模块，优化参数共享
3. **参数预处理**: 需要对模型参数进行特定变换或优化的场景
4. **边缘设备**: 在资源受限的设备上部署模型时，优化内存使用

## 示例代码

```python
import tvm
from tvm import relax

# 创建示例模块
mod = tvm.IRModule()

# 应用 PartitionTransformParams Pass
# 方式1: 启用全局参数共享
pass_with_global = relax.transform.PartitionTransformParams(True)
mod_global = pass_with_global(mod)

# 方式2: 为特定函数应用
target_functions = tvm.ffi.Array.String(["func1", "func2"])
pass_with_targets = relax.transform.PartitionTransformParams(target_functions)
mod_targeted = pass_with_targets(mod)

# 方式3: 禁用全局共享
pass_no_shared = relax.transform.PartitionTransformParams(False)
mod_local = pass_no_shared(mod)
```

## 相关 Pass

- **`LiftTransformParams`**: 基础的参数提升 Pass，提供类似的参数分离功能
- **`FuseOps`**: 操作融合 Pass，可与参数分离 Pass 配合使用优化计算图
- **`DeadCodeElimination`**: 死代码消除，在参数分离后清理无用代码
- **`ConstantFolding`**: 常量折叠，优化分离后的参数处理

该 Pass 通常作为模型优化流水线的一部分，与其他优化 Pass 协同工作以获得最佳性能。