---
title: ConvertLayout Pass
description: TVM Relax 中用于转换算子数据布局的 DataflowBlockPass。
---

# ConvertLayout Pass

## 概述

`ConvertLayout` Pass 是 TVM Relax 中的一个数据流块级别转换 Pass，主要用于将计算图中的算子数据布局（Layout）转换为指定的目标布局格式。该 Pass 通过重写计算图中的算子调用，将输入张量的布局转换为期望的布局格式，从而优化计算性能或满足特定硬件后端的要求。

## 函数签名

```cpp
Pass ConvertLayout(ffi::Map<ffi::String, ffi::Array<ffi::String>> desired_layouts)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `desired_layouts` | `ffi::Map<ffi::String, ffi::Array<ffi::String>>` | 指定期望的布局映射表，键为算子名称（如 "relax.nn.conv2d"），值为期望的输入张量布局数组 |

**参数详细说明：**
- `desired_layouts` 是一个映射表，用于指定不同算子期望的数据布局
- 键（Key）：算子名称的字符串表示，例如 `"relax.nn.conv2d"`、`"relax.nn.linear"` 等
- 值（Value）：字符串数组，表示该算子每个输入张量期望的布局格式，如 `["NHWC", "OHWI"]`

## 实现原理

`ConvertLayout` Pass 的核心实现基于以下步骤：

1. **遍历数据流块**：Pass 遍历输入 DataflowBlock 中的所有算子调用
2. **布局匹配检查**：对于每个算子调用，检查其算子名称是否在 `desired_layouts` 映射表中
3. **布局转换**：如果找到匹配的算子，Pass 会：
   - 插入必要的布局转换操作（如 `relax.layout_transform`）
   - 将原始算子的输入张量转换为期望的布局格式
   - 保持算子输出的布局格式不变或进行相应的反向转换
4. **算子重写**：使用转换后的输入张量重新创建算子调用，替换原始调用
5. **布局传播**：在某些情况下，Pass 会尝试优化连续的布局转换，减少不必要的转换操作

## 优化效果

该 Pass 带来的主要优化效果包括：

- **性能提升**：将数据布局转换为硬件友好的格式，充分利用硬件特性（如 GPU 的纹理内存、张量核心等）
- **内存优化**：减少布局转换带来的内存拷贝开销
- **算子融合**：为后续的算子融合 Pass 创造更好的条件，使得更多算子能够被融合
- **后端兼容**：确保计算图布局与特定硬件后端的要求相匹配

## 使用场景

`ConvertLayout` Pass 适用于以下场景：

1. **GPU 优化**：将 NCHW 布局转换为 NHWC 布局以利用 GPU 的优化计算路径
2. **专用加速器**：为特定 AI 加速器转换数据布局格式
3. **模型部署**：在模型部署到不同硬件平台时进行布局适配
4. **性能调优**：作为性能优化流水线的一部分，探索不同布局对性能的影响

## 示例代码

以下示例展示了如何使用 `ConvertLayout` Pass：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建期望布局映射
desired_layouts = {
    "relax.nn.conv2d": ["NHWC", "OHWI"],  # 将卷积的输入和权重转换为 NHWC 和 OHWI 布局
    "relax.nn.linear": ["NHW", "OI"]      # 将全连接层的输入和权重转换为特定布局
}

# 创建并应用 ConvertLayout Pass
pass_obj = transform.ConvertLayout(desired_layouts)

# 应用 Pass 到 IRModule
mod_transformed = pass_obj(mod)
```

## 相关 Pass

- **FuseOps**：算子融合 Pass，布局转换后可能创造更多融合机会
- **CanonicalizeBindings**：规范化绑定，清理布局转换引入的中间变量
- **LegalizeOps**：算子合法化，与布局转换协同工作以确保算子支持目标布局
- **AlterOpLayout**：TVM 传统 Relay 中的类似布局转换 Pass

## 注意事项

1. **布局兼容性**：确保目标硬件后端支持所选的布局格式
2. **性能权衡**：布局转换本身有开销，需要权衡转换收益与开销
3. **调试支持**：可以使用 `PassContext` 的调试选项来跟踪布局转换过程
4. **自定义算子**：对于自定义算子，需要确保算子支持期望的布局格式或提供相应的布局转换实现