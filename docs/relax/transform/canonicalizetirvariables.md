---
title: CanonicalizeTIRVariables Pass
description: TVM Relax 中用于规范化 TIR 变量的函数级变换 Pass
---

# CanonicalizeTIRVariables Pass

## 概述

`CanonicalizeTIRVariables` 是一个函数级别的变换 Pass，主要用于规范化 Relax 函数中的 TIR（TensorIR）变量。该 Pass 通过重命名和标准化 TIR 变量，确保生成的代码具有一致的变量命名约定，从而提高后续优化 Pass 的效果和代码的可读性。

## 函数签名

```cpp
Pass CanonicalizeTIRVariables()
```

**返回值：**
- `Pass`：一个 TVM Pass 对象，可在 Pass 流水线中执行

## 参数说明

此 Pass 不接受任何显式参数，它是一个无状态的变换 Pass，在 TVM Pass 上下文中自动执行。

## 实现原理

`CanonicalizeTIRVariables` Pass 的核心实现基于以下逻辑：

1. **函数遍历**：Pass 以 Relax 函数作为输入，遍历函数中的所有绑定（Bindings）

2. **TIR 变量识别**：在遍历过程中，识别出所有与 TIR 相关的变量，包括：
   - 循环迭代变量
   - 块迭代变量
   - 归约变量
   - 其他 TIR 计算中使用的临时变量

3. **规范化处理**：对识别出的 TIR 变量进行规范化处理，包括：
   - 变量重命名：按照统一的命名约定重命名变量
   - 作用域处理：确保变量在正确的作用域内
   - 冲突解决：处理可能的变量名冲突

4. **函数重构**：基于规范化后的变量重新构建 Relax 函数

## 优化效果

该 Pass 带来的主要优化效果包括：

- **代码一致性**：统一的变量命名提高了代码的可读性和可维护性
- **优化友好**：标准化的变量命名使得后续优化 Pass 更容易识别和处理相关模式
- **调试便利**：规范的变量名简化了调试过程
- **降低冲突**：减少了变量名冲突的可能性

## 使用场景

`CanonicalizeTIRVariables` Pass 通常在以下场景中使用：

1. **TIR 生成后**：在从高级表示生成 TIR 代码后立即应用
2. **优化流水线早期**：作为优化流水线的早期步骤，为后续优化做准备
3. **代码生成前**：在最终代码生成之前确保变量命名的规范性
4. **跨平台部署**：确保在不同目标平台上变量命名的一致性

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建示例 Relax 函数
@relax.function
def example_function(x: relax.Tensor):
    # 包含非规范 TIR 变量的计算
    with relax.dataflow():
        # 假设这里有一些包含非规范 TIR 变量的操作
        y = relax.op.add(x, x)
        z = relax.op.multiply(y, y)
        return z

# 构建 IRModule
mod = tvm.IRModule({"main": example_function})

# 应用 CanonicalizeTIRVariables Pass
mod_optimized = transform.CanonicalizeTIRVariables()(mod)

# 查看优化后的模块
print(mod_optimized)
```

## 相关 Pass

- **`LegalizeOps`**：将高级算子转换为低级 TIR 实现
- **`FuseTIR`**：融合相邻的 TIR 函数
- **`LowerTIR`**：将 TIR 函数降低到目标特定的表示
- **`CanonicalizeBindings`**：规范化 Relax 绑定表达式

这些 Pass 通常与 `CanonicalizeTIRVariables` 一起在完整的优化流水线中协同工作，共同完成从高级 Relax 表示到优化后的低级代码的转换过程。