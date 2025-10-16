---
title: collect_non_negative_expressions
description: TVM Relax Analysis - collect_non_negative_expressions 函数 API 文档
---

# collect_non_negative_expressions

## 概述

`collect_non_negative_expressions` 函数用于从 Relax 的 StructInfo 中收集在非负上下文中使用的 TIR 表达式。该函数在 TVM Relax 的静态分析流程中扮演重要角色，主要用于识别和提取那些在语义上保证为非负值的 TIR 变量和表达式。

在深度学习编译器的优化过程中，许多优化决策（如内存分配、循环变换、并行化策略）都依赖于对张量形状和索引变量范围的准确理解。该函数能够帮助编译器确定哪些表达式在特定上下文中具有非负性质，从而支持更精确的优化和验证。

该函数与 Relax IR 的类型系统和形状推导紧密集成，是构建可靠编译时分析的基础工具之一。

## 函数签名

```python
def collect_non_negative_expressions(sinfo: StructInfo) -> List[tir.PrimExpr]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| sinfo | StructInfo | 无 | 需要分析的结构信息对象。可以是 TensorStructInfo、TupleStructInfo 或其他 StructInfo 子类，包含了 Relax 表达式的类型和形状信息。 |

## 返回值

**类型:** `List[tir.PrimExpr]`

返回一个包含 TIR 表达式的列表，这些表达式在给定的 StructInfo 上下文中被保证为非负值。例如，用作张量形状的维度表达式、循环边界等。返回的列表经过去重处理，每个 TIR 表达式最多出现一次，且按照在 StructInfo 中出现的顺序排列。

## 使用场景

### IR 结构分析
- 分析 Relax 函数的签名和返回值类型，识别形状相关的非负表达式
- 在函数内联和特化时，验证和传播形状约束

### 变量依赖分析  
- 识别形状计算中使用的变量依赖关系
- 支持基于形状的优化决策

### 编译时检查
- 验证形状表达式的合法性（如确保维度大小为非负）
- 在编译阶段捕获潜在的形状错误

### 优化决策支持
- 为内存分配、循环变换等优化提供形状信息
- 支持基于形状的代码生成策略选择

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import collect_non_negative_expressions
from tvm.script import relax as R

# 创建 TensorStructInfo 并分析非负表达式
tensor_sinfo = relax.TensorStructInfo(
    shape=[n, m, 16], 
    dtype="float32"
)

# 收集非负表达式
non_negative_exprs = collect_non_negative_expressions(tensor_sinfo)
print("非负表达式:", non_negative_exprs)
# 输出可能包含: [n, m] (假设 n, m 是 TIR 变量)
```

### 高级用法

```python
import tvm
from tvm import relax, tir
from tvm.relax.analysis import collect_non_negative_expressions

def analyze_function_shape(func: relax.Function):
    """分析函数中所有形状相关的非负表达式"""
    
    # 分析函数返回类型的非负表达式
    ret_sinfo = func.struct_info.ret
    ret_non_negative = collect_non_negative_expressions(ret_sinfo)
    
    # 分析函数参数的非负表达式
    param_non_negative = []
    for param in func.params:
        param_non_negative.extend(
            collect_non_negative_expressions(param.struct_info)
        )
    
    # 合并并去重
    all_non_negative = list(set(ret_non_negative + param_non_negative))
    
    print("函数中所有非负表达式:", all_non_negative)
    return all_non_negative

# 结合其他分析函数进行综合形状分析
from tvm.relax.analysis import get_var2val

def comprehensive_shape_analysis(func: relax.Function):
    """综合形状分析，结合变量绑定信息"""
    var2val = get_var2val(func)
    
    # 获取所有绑定变量的结构信息
    shape_constraints = []
    for var, value in var2val.items():
        if hasattr(value, 'struct_info'):
            constraints = collect_non_negative_expressions(value.struct_info)
            shape_constraints.extend(constraints)
    
    return list(set(shape_constraints))
```

## 实现细节

该函数通过 TVM 的 FFI 接口调用底层的 C++ 实现 `_ffi_api.CollectNonNegativeExpressions`。底层实现会遍历 StructInfo 的 AST，识别在以下上下文中使用的 TIR 表达式：

- 张量形状维度
- 结构体大小计算
- 其他保证为非负的表达式上下文

算法采用深度优先遍历，维护一个访问集合来确保返回结果的唯一性，同时保持表达式在原始 StructInfo 中的出现顺序。

## 相关函数

- [`get_var2val`](./get_var2val.md) - 获取变量到值的映射，用于结合变量绑定信息进行形状分析
- [`struct_inference`](./struct_inference.md) - 结构信息推导，为分析提供输入的结构信息
- [`bind_params`](./bind_params.md) - 参数绑定，影响 StructInfo 中的表达式分析

## 注意事项

### 性能考虑
- 对于复杂的嵌套 StructInfo，函数可能需要遍历较大的 AST，建议在需要时调用
- 结果缓存可能有助于重复分析相同或相似的 StructInfo

### 使用限制
- 函数仅分析 StructInfo 中显式出现的表达式，不进行符号推导或约束求解
- 返回的表达式的非负性仅在给定的 StructInfo 上下文中成立

### 常见错误
- 传入非 StructInfo 类型的参数会导致运行时错误
- 忽略返回表达式的上下文依赖性可能导致错误的分析结论

### 最佳实践
- 在形状推导完成后调用此函数，以获得最完整的表达式集合
- 结合其他分析函数（如 `get_var2val`）进行综合的形状分析
- 对结果进行适当的验证，特别是在涉及用户输入的表达式时