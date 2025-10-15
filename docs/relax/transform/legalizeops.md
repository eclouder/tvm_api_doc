---
title: LegalizeOps
description: TVM Relax 的算子合法化转换 Pass，用于将 Relax 算子转换为目标后端支持的算子形式。
---

# LegalizeOps

## 概述

LegalizeOps Pass 是 TVM Relax 中的一个模块级转换 Pass，主要功能是将 Relax 前端算子转换为目标后端支持的算子形式。该 Pass 通过算子映射表将高层次的 Relax 算子替换为特定后端（如 CUDA、Metal、OpenCL 等）优化的算子实现，确保模型能够在不同硬件平台上高效运行。

## 函数签名

```cpp
Pass LegalizeOps(ffi::Optional<ffi::Map<ffi::String, ffi::Function>> cmap, bool enable_warning)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `cmap` | `ffi::Optional<ffi::Map<ffi::String, ffi::Function>>` | 可选的算子映射表，用于指定特定算子的合法化函数。如果未提供，将使用默认的合法化规则。 |
| `enable_warning` | `bool` | 是否启用警告信息。当设置为 `true` 时，在遇到无法合法化的算子时会输出警告信息。 |

## 实现原理

LegalizeOps Pass 的核心实现基于 `LegalizeMutator` 类，其主要工作原理如下：

1. **配置检查**：首先检查 Pass 上下文中的 `relax.transform.apply_legalize_ops` 配置选项，确定是否应用合法化转换（默认为 `true`）。

2. **算子遍历**：通过 `LegalizeMutator` 遍历 IRModule 中的所有函数，识别需要合法化的 Relax 算子。

3. **算子替换**：
   - 对于每个算子，查找对应的合法化函数
   - 如果提供了自定义的 `cmap` 映射表，优先使用其中的合法化函数
   - 否则使用内置的默认合法化规则
   - 将原始算子替换为合法化后的算子实现

4. **警告机制**：当 `enable_warning` 为 `true` 时，对于无法找到合法化实现的算子，会输出警告信息帮助用户诊断问题。

## 优化效果

LegalizeOps Pass 的主要优化效果包括：

- **硬件兼容性**：确保 Relax 模型能够在各种硬件后端上执行
- **性能优化**：将通用算子替换为针对特定硬件优化的实现
- **代码可移植性**：通过统一的合法化接口，支持多平台部署
- **开发效率**：允许前端使用简洁的算子表示，后端负责具体实现

## 使用场景

LegalizeOps Pass 在以下场景中特别有用：

1. **模型部署**：在将 Relax 模型部署到特定硬件平台之前
2. **后端优化**：针对不同硬件特性进行算子级优化
3. **自定义算子**：当需要为特定算子提供自定义实现时
4. **跨平台支持**：确保模型在多个硬件平台上的一致性行为

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import LegalizeOps

# 创建 IRModule
mod = tvm.IRModule.from_expr(relax.add(x, y))

# 应用 LegalizeOps Pass
# 使用默认合法化规则
legalized_mod = LegalizeOps()(mod)

# 使用自定义算子映射表
custom_map = {
    "relax.add": custom_add_legalize_func
}
legalized_mod = LegalizeOps(cmap=custom_map, enable_warning=True)(mod)
```

## 相关 Pass

- **FuseOps**：算子融合 Pass，与 LegalizeOps 配合使用可以进一步提高性能
- **ToMixedPrecision**：混合精度转换，可能在合法化前后应用
- **AnnotateTIROpPattern**：TIR 算子模式标注，为后续优化提供信息
- **AlterOpImpl**：算子实现替换，与 LegalizeOps 有相似的替换逻辑但关注点不同

LegalizeOps 通常在算子融合和硬件特定优化之前应用，是 Relax 编译流水线中的重要环节。