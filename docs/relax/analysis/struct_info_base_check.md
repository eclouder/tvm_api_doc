---
title: struct_info_base_check
description: TVM Relax Analysis - struct_info_base_check 函数 API 文档
---

# struct_info_base_check

## 概述

`struct_info_base_check` 是 TVM Relax 分析模块中的核心函数，用于执行结构信息的基类检查。该函数的主要功能是验证给定的基础结构信息（base）是否能够包含（subsume）派生结构信息（derived）。

在 Relax IR 的分析流程中，该函数扮演着重要的类型系统验证角色：
- 用于检查类型兼容性和子类型关系
- 在编译时验证操作符的输入输出类型约束
- 支持类型推导和类型推断过程
- 与其他结构信息分析函数（如 `struct_info_lca`）协同工作，构建完整的类型分析体系

该函数适用于各种需要验证结构信息关系的场景，特别是在编译器优化、代码生成和静态分析阶段。

## 函数签名

```python
def struct_info_base_check(base: StructInfo, derived: StructInfo) -> BaseCheckResult
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| base | StructInfo | 无 | 基础结构信息，作为检查的基准类型。必须是有效的 StructInfo 对象，如 TensorStructInfo、TupleStructInfo 等 |
| derived | StructInfo | 无 | 派生结构信息，需要检查是否能够被基础结构信息包含。必须与 base 参数类型兼容 |

## 返回值

**类型:** `BaseCheckResult`

返回一个 `BaseCheckResult` 枚举值，表示基类检查的结果。可能的取值包括：
- `PASS`: 基础结构信息完全包含派生结构信息
- `FAIL`: 基础结构信息无法包含派生结构信息  
- `INCONCLUSIVE`: 检查结果不确定，需要进一步分析

## 使用场景

### IR 结构分析
在 Relax IR 转换和优化过程中，验证操作符的输入输出类型是否符合预期约束。

### 变量依赖分析
检查变量赋值和传播过程中类型信息的一致性，确保类型安全。

### 编译时检查
在编译阶段验证函数签名、操作符重载和类型转换的合法性。

### 优化决策支持
为编译器优化策略提供类型信息支持，如内存布局优化、操作符融合等。

### 类型系统验证
构建 Relax 类型系统的子类型关系，支持多态和类型推导。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import struct_info_base_check

# 创建两个张量结构信息
tensor_sinfo = relax.TensorStructInfo(
    shape=[1, 3, 224, 224], 
    dtype="float32"
)
tensor_sinfo2 = relax.TensorStructInfo(
    shape=[1, 3, 224, 224], 
    dtype="float32"
)

# 执行基础检查
check_result = struct_info_base_check(tensor_sinfo, tensor_sinfo2)
print(f"基础检查结果: {check_result}")

# 结合最小公共祖先函数使用
from tvm.relax.analysis import struct_info_lca
lca_result = struct_info_lca(tensor_sinfo, tensor_sinfo2)
```

### 高级用法

```python
# 在自定义分析流程中使用
def analyze_type_compatibility(func: relax.Function):
    """分析函数中类型兼容性"""
    # 获取函数的返回类型信息
    ret_sinfo = func.struct_info.ret
    
    # 检查函数体中的表达式类型
    for block in func.body.blocks:
        for binding in block.bindings:
            if isinstance(binding, relax.VarBinding):
                var_sinfo = binding.var.struct_info
                value_sinfo = binding.value.struct_info
                
                # 使用 struct_info_base_check 验证类型一致性
                check_result = struct_info_base_check(var_sinfo, value_sinfo)
                if check_result == BaseCheckResult.FAIL:
                    print(f"类型不匹配: {binding.var.name_hint}")
                
# 在优化过程中使用
def optimize_with_type_check(expr: relax.Expr):
    """基于类型检查的优化"""
    original_sinfo = expr.struct_info
    
    # 应用某些优化转换
    optimized_expr = apply_optimization(expr)
    optimized_sinfo = optimized_expr.struct_info
    
    # 验证优化后类型兼容性
    if struct_info_base_check(original_sinfo, optimized_sinfo) == BaseCheckResult.PASS:
        return optimized_expr
    else:
        # 回退到原始表达式
        return expr
```

## 实现细节

`struct_info_base_check` 函数通过调用底层的 C++ 实现 (`_ffi_api.StructInfoBaseCheck`) 来执行实际的类型检查。该实现基于 Relax 的类型系统规则，考虑了以下因素：

- **张量维度兼容性**: 检查形状、数据类型、内存布局等
- **元组结构兼容性**: 验证元组元素的数量和类型匹配
- **对象类型兼容性**: 处理对象引用和内存分配
- **形状符号推理**: 支持符号形状的包含关系检查

算法采用递归下降的方式遍历结构信息树，确保所有嵌套层次都满足包含关系。

## 相关函数

- [`struct_info_lca`](./struct_info_lca.md) - 计算两个结构信息的最小公共祖先
- [`struct_info_equals`](./struct_info_equals.md) - 检查两个结构信息是否相等
- [`struct_info_is_base_of`](./struct_info_is_base_of.md) - 判断一个结构信息是否是另一个的基类

## 注意事项

### 性能考虑
- 对于复杂的嵌套结构信息，检查可能涉及递归遍历，需要注意性能影响
- 在热点路径中频繁调用时，建议缓存检查结果

### 使用限制
- 只能检查编译时已知的结构信息
- 对于动态形状和运行时类型信息支持有限

### 常见错误
- 传递无效的 StructInfo 对象会导致运行时错误
- 忽略检查结果可能导致后续分析阶段出现类型错误

### 最佳实践
- 在关键路径上预先验证类型兼容性
- 结合其他分析函数构建完整的类型验证流程
- 在处理用户输入或外部数据时始终进行类型检查