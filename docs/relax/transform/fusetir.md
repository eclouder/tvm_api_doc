---
title: FuseTIR
description: TVM Relax 的模块级 Pass，用于融合 TIR 函数以优化计算图执行效率。
---

# FuseTIR

## 概述

FuseTIR 是 TVM Relax 的一个模块级变换 Pass，主要功能是将多个 TIR（TensorIR）函数融合成一个更大的 TIR 函数。通过减少函数调用开销和增加数据局部性，该 Pass 能够显著提升模型在目标设备上的执行效率。

该 Pass 特别适用于优化包含多个小规模计算操作的模型，通过操作融合来减少内核启动次数和中间结果的存储开销。

## 函数签名

```cpp
Pass FuseTIR()
```

**返回值**: `tvm::transform::Pass` - 一个可执行的模块级变换 Pass

## 参数说明

FuseTIR 函数本身不接受任何参数，它返回一个配置好的 Pass 对象。在 Pass 执行过程中，会自动处理以下内容：

- **输入**: `IRModule` - 包含 Relax 和 TIR 函数的中间表示模块
- **输出**: `IRModule` - 经过 TIR 函数融合优化后的模块

## 实现原理

FuseTIR Pass 的实现采用多阶段流水线设计：

1. **展开元组参数** (`ExpandTupleArguments`)
   - 将函数调用中的元组参数展开为多个独立参数
   - 为后续的融合操作准备标准化的函数接口

2. **移除未使用参数** (`RemoveUnusedParameters`)
   - 清理函数签名中未被使用的参数
   - 简化函数接口，减少不必要的参数传递

3. **核心融合处理** (`FuseTIRInner`)
   - 分析计算图中的数据依赖关系
   - 识别可融合的 TIR 函数序列
   - 将多个小规模的 TIR 函数合并为单个复合函数
   - 保持计算语义不变的同时优化执行结构

4. **死代码消除** (`DeadCodeElimination`)
   - 移除融合后不再被引用的原始函数
   - 清理优化过程中产生的冗余代码

## 优化效果

应用 FuseTIR Pass 后，模型可以获得以下优化效果：

- **减少函数调用开销**: 将多个内核调用合并为单个调用，显著降低调度开销
- **提升数据局部性**: 融合后的函数可以在共享内存中直接传递中间结果，减少全局内存访问
- **增强并行度**: 更大的计算单元为硬件调度器提供更多优化机会
- **降低内存占用**: 减少中间结果的存储需求

## 使用场景

FuseTIR Pass 适用于以下场景：

1. **计算密集型模型优化**
   - 包含大量逐元素操作（element-wise operations）的模型
   - 具有规则数据依赖关系的计算图

2. **内存带宽受限场景**
   - 当模型性能受限于内存带宽而非计算能力时
   - 需要减少中间结果写入/读取的场景

3. **端侧部署优化**
   - 针对资源受限的边缘设备
   - 需要最小化内核启动开销的部署环境

**使用时机**: 建议在算子分解和规范化之后、最终代码生成之前应用此 Pass。

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import FuseTIR

# 构建原始 IRModule
original_mod = tvm.IRModule({
    "main": relax.Function(...)
})

# 应用 FuseTIR Pass
seq = tvm.transform.Sequential([
    # ... 其他前置 Pass
    FuseTIR(),
    # ... 其他后置 Pass
])

optimized_mod = seq(original_mod)

# 或者单独使用
fused_mod = FuseTIR()(original_mod)
```

## 相关 Pass

### 前置依赖 Pass
- **ExpandTupleArguments**: 准备函数接口用于融合
- **RemoveUnusedParameters**: 简化函数签名

### 协同工作 Pass
- **FuseOps**: Relax 层面的算子融合，与 TIR 融合协同工作
- **FuseTIR**: 本文档描述的 TIR 函数融合 Pass

### 后续优化 Pass
- **DeadCodeElimination**: 清理融合后的冗余代码
- **LegalizeOps**: 将融合后的操作合法化为目标后端支持的操作

这些 Pass 共同构成了 TVM Relax 的完整优化流水线，在不同的抽象层次上进行计算图优化。