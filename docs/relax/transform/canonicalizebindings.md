---
title: CanonicalizeBindings
description: TVM Relax 的规范化绑定转换 Pass，用于标准化 Relax 函数中的变量和绑定结构。
---

# CanonicalizeBindings

## 概述

`CanonicalizeBindings` 是一个 TVM Relax 转换 Pass，属于 SequentialPass 类型。该 Pass 的主要功能是对 Relax 函数中的变量命名和绑定结构进行规范化处理，消除中间表示中的冗余和不一致，提高后续优化 Pass 的效果和可靠性。

通过组合两个子 Pass - `CanonicalizeTIRVariables` 和 `CanonicalizeRelaxBindings`，该 Pass 能够系统性地处理 TIR 变量和 Relax 绑定的规范化问题。

## 函数签名

```cpp
Pass CanonicalizeBindings()
```

**返回值：**
- `tvm::transform::Pass`：一个顺序执行 Pass 对象，依次执行两个规范化子 Pass。

## 参数说明

该 Pass 不接受任何参数，是一个无参的工厂函数。

## 实现原理

`CanonicalizeBindings` 的实现基于顺序执行模式，包含两个核心子 Pass：

### 1. CanonicalizeTIRVariables
- **功能**：规范化 TIR（TensorIR）变量命名
- **处理内容**：
  - 重命名 TIR 表达式中的变量，消除命名冲突
  - 统一变量命名规则，提高可读性和一致性
  - 处理变量作用域和生命周期管理

### 2. CanonicalizeRelaxBindings  
- **功能**：规范化 Relax 绑定结构
- **处理内容**：
  - 优化绑定表达式的结构
  - 消除冗余绑定操作
  - 标准化绑定模式，便于后续分析和优化

两个子 Pass 按顺序执行，首先处理底层的 TIR 变量规范化，然后处理上层的 Relax 绑定规范化。

## 优化效果

应用 `CanonicalizeBindings` Pass 后，可以带来以下优化效果：

1. **代码规范化**：统一的变量命名和绑定结构，提高代码一致性
2. **消除歧义**：解决变量命名冲突和作用域问题
3. **优化友好**：为后续优化 Pass 提供更规整的中间表示
4. **调试便利**：标准化的命名便于调试和分析
5. **性能提升**：通过消除冗余绑定，可能减少运行时开销

## 使用场景

该 Pass 适用于以下场景：

1. **编译流程早期**：在复杂优化之前进行规范化处理
2. **代码生成前**：确保生成的代码具有一致的命名规范
3. **跨模块集成**：当合并多个 Relax 模块时，解决命名冲突
4. **调试和分析**：需要标准化中间表示以便于分析时
5. **Pass 开发**：作为其他转换 Pass 的前置处理步骤

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建 Relax 模块
@relax.function
def example_function(x: relax.Tensor((32, 64), "float32")):
    # 可能存在非规范化的绑定
    y = relax.add(x, x)
    z = relax.multiply(y, y)
    return z

mod = tvm.IRModule()
mod["main"] = example_function

# 应用 CanonicalizeBindings Pass
seq = transform.Sequential([
    transform.CanonicalizeBindings(),
    # 其他优化 Pass...
])

mod_optimized = seq(mod)
```

## 相关 Pass

### 前置 Pass
- **无特定前置要求**：通常作为编译流程的早期 Pass

### 后续 Pass
- **FuseOps**：绑定规范化后便于算子融合
- **DeadCodeElimination**：可能暴露出更多的死代码消除机会
- **LegalizeOps**：规范化后的绑定更易于合法化处理

### 相关子 Pass
- `CanonicalizeTIRVariables`：处理 TIR 变量规范化
- `CanonicalizeRelaxBindings`：处理 Relax 绑定规范化

### 协同工作 Pass
- `Normalize`：整体规范化流程的组成部分
- `FoldConstant`：常量折叠可能受益于规范化的绑定结构