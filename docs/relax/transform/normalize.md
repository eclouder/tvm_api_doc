---
title: Normalize Pass
description: TVM Relax 中的 Normalize Pass 用于对函数表达式进行规范化处理，确保 IR 符合预期的结构形式。
---

# Normalize Pass

## 概述

Normalize Pass 是 TVM Relax 中的一个函数级变换 Pass，主要功能是对 Relax 函数进行规范化处理。该 Pass 通过应用一系列的规范化规则，确保中间表示（IR）符合编译器预期的标准结构形式，为后续的优化 Pass 提供统一的输入格式。

## 函数签名

```cpp
Pass Normalize()
```

## 参数说明

此 Pass 为无参数工厂函数，返回一个 `Pass` 对象。在 TVM 的 Pass 基础设施中，该 Pass 会被自动应用到 IRModule 中的所有函数。

## 实现原理

Normalize Pass 的核心实现基于 `Normalize` 函数，其主要处理逻辑包括：

1. **表达式规范化**：对函数体中的各种表达式进行标准化处理
2. **类型推导**：确保所有表达式都有正确的类型注解
3. **结构统一**：将不同形式的表达式转换为统一的标准形式
4. **常量折叠**：对可计算的常量表达式进行预计算

实现代码：
```cpp
Pass Normalize() {
  auto pass_func = [=](Function f, IRModule m, PassContext pc) {
    return Downcast<Function>(Normalize(f));
  };
  return CreateFunctionPass(pass_func, 1, "Normalize", {});
}
```

该 Pass 被设计为函数级 Pass（FunctionPass），优化级别为 1，会按顺序处理 IRModule 中的每个函数。

## 优化效果

Normalize Pass 主要带来以下优化效果：

- **IR 一致性**：确保所有函数都符合统一的 IR 规范
- **后续优化准备**：为依赖标准 IR 形式的后续优化 Pass 提供合格的输入
- **错误检测**：在规范化过程中能够早期发现 IR 结构问题
- **调试友好**：标准化的 IR 形式更易于调试和分析

## 使用场景

Normalize Pass 通常在以下场景中使用：

1. **前端转换后**：在从前端模型（如 ONNX、PyTorch）转换到 Relax IR 后立即应用
2. **自定义变换前**：在执行用户自定义的 IR 变换之前
3. **优化流水线中**：作为优化流水线的早期阶段，确保后续 Pass 的输入格式正确
4. **调试阶段**：当需要检查 IR 结构是否符合规范时

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 构建示例 IRModule
@relax.function
def example_func(x: relax.Tensor((32, 64), "float32")) -> relax.Tensor:
    y = relax.add(x, x)
    z = relax.multiply(y, relax.const(2.0, "float32"))
    return z

mod = tvm.IRModule({"example": example_func})

# 应用 Normalize Pass
seq = transform.Sequential([
    transform.Normalize()
])
mod_normalized = seq(mod)

print("规范化后的模块：")
print(mod_normalized)
```

## 相关 Pass

- **CanonicalizeBindings**：规范化绑定表达式
- **FuseOps**：操作符融合，依赖规范化的 IR 输入
- **DeadCodeElimination**：死代码消除，在规范化后更有效
- **LegalizeOps**：操作符合法化，通常跟在规范化之后

Normalize Pass 在 TVM Relax 的优化流水线中扮演着基础性的角色，为后续的高级优化提供了标准化的 IR 基础。