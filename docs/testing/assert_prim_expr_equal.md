---
title: assert_prim_expr_equal
description: 用于断言两个TIR原始表达式在数学上相等的测试工具函数
---

# assert_prim_expr_equal

## 概述

`assert_prim_expr_equal` 是 TVM 测试框架中的一个核心断言函数，专门用于验证两个 TIR (Tensor Intermediate Representation) 原始表达式在数学上的等价性。该函数通过 TVM 的内置算术分析器对表达式进行形式化验证，确保编译器优化前后的表达式在数学语义上保持一致。

在 TVM 测试流程中，该函数主要应用于：
- **表达式等价性验证**：确保优化变换不会改变程序的数学语义
- **编译器正确性测试**：验证 TIR 变换和优化的正确性
- **跨平台一致性检查**：保证不同目标平台上的表达式行为一致

## 函数签名

```python
def assert_prim_expr_equal(lhs, rhs):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| lhs | tvm.tir.PrimExpr | 要比较的左侧原始表达式 | 无 |
| rhs | tvm.tir.PrimExpr | 要比较的右侧原始表达式 | 无 |

## 返回值

**类型:** `None`

该函数没有返回值，当两个表达式相等时正常执行，不相等时抛出 `ValueError` 异常。

## 使用场景

### 单元测试
验证单个 TIR 变换或优化过程的正确性

### 集成测试
确保多个优化过程组合后仍保持表达式语义

### 目标平台测试
验证不同硬件目标（CPU、GPU、加速器）上的表达式等价性

### 性能回归测试
确保性能优化不会引入语义错误

## 使用示例

```python
import tvm
from tvm import tir
from tvm.testing import assert_prim_expr_equal

# 基本算术表达式验证
a = tir.Var("a", "int32")
b = tir.Var("b", "int32")

# 验证交换律
expr1 = a + b
expr2 = b + a
assert_prim_expr_equal(expr1, expr2)

# 验证结合律
expr3 = (a + b) + a
expr4 = a + (b + a) 
assert_prim_expr_equal(expr3, expr4)

# 验证常量折叠
expr5 = a * 2 + a * 2
expr6 = a * 4
assert_prim_expr_equal(expr5, expr6)

# 验证复杂表达式
c = tir.Var("c", "int32")
expr7 = (a + b) * c - b * c
expr8 = a * c
assert_prim_expr_equal(expr7, expr8)
```

## 注意事项

- **表达式复杂度**：对于非常复杂的表达式，分析器可能需要较长的验证时间
- **数学等价性**：函数验证的是数学等价性，而非语法等价性
- **异常处理**：当表达式不相等时，函数会抛出 `ValueError` 并显示具体的表达式差异
- **符号变量**：表达式中使用的符号变量应在分析器的知识范围内
- **TVM版本**：该函数的行为可能随 TVM 版本更新而变化

## 相关函数

- `tvm.arith.Analyzer.can_prove_equal` - 底层使用的表达式等价性证明函数
- `tvm.testing.assert_allclose` - 数值张量的近似相等断言
- `tvm.ir.assert_structural_equal` - IR 模块的结构相等性断言
- `tvm.testing.main` - TVM 测试框架的主入口函数

## 内部实现原理

该函数基于 TVM 的算术分析器 (`tvm.arith.Analyzer`) 实现，分析器使用符号计算和定理证明技术来验证表达式的数学等价性。这种方法比简单的语法比较更加鲁棒，能够识别数学上等价但语法不同的表达式形式。