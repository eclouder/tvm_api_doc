---
title: definable_tir_vars_in_struct_info
description: TVM Relax Analysis - definable_tir_vars_in_struct_info 函数 API 文档
---

# definable_tir_vars_in_struct_info

## 概述

`definable_tir_vars_in_struct_info` 是 TVM Relax 分析模块中的一个重要函数，主要用于从结构信息（StructInfo）中提取可定义的 TIR 变量。该函数在 Relax IR 的类型系统和形状推断流程中扮演着关键角色，能够帮助编译器理解在特定结构信息上下文中哪些 TIR 变量可以被定义和使用。

该函数的主要用途包括：
- 分析结构信息中隐含的 TIR 变量定义能力
- 为后续的变量依赖分析和内存分配提供基础信息
- 支持编译时的形状推导和类型检查
- 在优化过程中识别可重用的变量定义

在 Relax IR 分析流程中，该函数通常位于类型推断和形状分析阶段，为后续的优化和代码生成提供必要的变量信息。

## 函数签名

```python
def definable_tir_vars_in_struct_info(sinfo: StructInfo) -> List[tir.Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| sinfo | StructInfo | 无 | 需要分析的结构信息对象。该参数包含了 Relax 表达式的类型和形状信息，函数将从中提取可定义的 TIR 变量。StructInfo 可以是 TensorType、TupleType、ShapeType 等类型。 |

## 返回值

**类型:** `List[tir.Var]`

返回一个包含 TIR 变量的列表，这些变量可以从输入的结构信息中定义。返回的列表已经过去重处理，确保每个 TIR 变量最多出现一次。这些变量代表了在给定结构信息上下文中可以被定义和使用的符号变量，通常用于表示张量的维度大小或其他编译时常量。

## 使用场景

该函数在以下场景中具有重要应用价值：

- **IR 结构分析**: 在解析 Relax IR 时，分析表达式的结构信息以确定可定义的符号变量
- **变量依赖分析**: 识别变量之间的依赖关系，为优化传递提供信息
- **内存使用分析**: 通过了解可定义的变量，更准确地估计内存使用情况
- **优化决策支持**: 为循环变换、并行化等优化决策提供变量定义信息
- **编译时检查**: 在编译阶段验证变量定义的合法性和一致性

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import definable_tir_vars_in_struct_info
from tvm.script import relax as R

# 创建一个包含 TIR 变量的结构信息
n = tvm.tir.Var("n", "int32")
m = tvm.tir.Var("m", "int32")
tensor_type = relax.TensorStructInfo([n, m], "float32")

# 分析结构信息中的可定义 TIR 变量
definable_vars = definable_tir_vars_in_struct_info(tensor_type)
print(f"可定义的 TIR 变量: {definable_vars}")
# 输出: 可定义的 TIR 变量: [n, m]
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import definable_tir_vars_in_struct_info

# 结合其他分析函数进行复杂结构分析
def analyze_complex_struct_info(sinfo):
    # 获取可定义的 TIR 变量
    definable_vars = definable_tir_vars_in_struct_info(sinfo)
    
    # 进一步分析变量属性
    var_info = []
    for var in definable_vars:
        var_info.append({
            'name': var.name,
            'dtype': var.dtype,
            'is_symbolic': hasattr(var, 'is_symbolic') and var.is_symbolic
        })
    
    return definable_vars, var_info

# 分析元组类型的结构信息
n = tvm.tir.Var("n", "int32")
tensor1 = relax.TensorStructInfo([n, 64], "float32")
tensor2 = relax.TensorStructInfo([32, n], "float32")
tuple_sinfo = relax.TupleStructInfo([tensor1, tensor2])

variables, info = analyze_complex_struct_info(tuple_sinfo)
print(f"发现的变量: {variables}")
print(f"变量信息: {info}")
```

## 实现细节

该函数通过调用底层的 C++ 实现 `_ffi_api.DefinableTIRVarsInStructInfo` 来完成核心分析逻辑。实现原理基于对 StructInfo 的递归遍历：

1. **TensorStructInfo**: 从形状维度中提取 TIR 变量
2. **TupleStructInfo**: 递归分析元组中的每个元素
3. **ShapeStructInfo**: 直接从形状值中提取变量
4. **其他 StructInfo 类型**: 根据具体类型特性进行相应处理

算法会自动处理重复变量，确保返回列表中的每个变量都是唯一的。

## 相关函数

- [`get_static_type`](./get_static_type.md) - 获取结构信息的静态类型信息
- [`analyze_var2val`](./analyze_var2val.md) - 分析变量到值的映射关系
- [`get_var2val`](./get_var2val.md) - 获取变量到值的映射

## 注意事项

使用该函数时需要注意以下事项：

- **性能考虑**: 对于复杂的嵌套结构信息，函数可能需要进行深度递归遍历，在处理大型 IR 时应注意性能影响
- **使用限制**: 函数只分析结构信息本身，不考虑上下文中的变量绑定关系
- **变量作用域**: 返回的 TIR 变量需要在合适的上下文中使用，避免作用域冲突
- **类型安全**: 确保输入的结构信息是有效的，否则可能导致分析错误
- **最佳实践**: 在优化管道中合理使用该函数，避免重复分析相同的结构信息

该函数是 TVM Relax 分析工具链中的重要组成部分，正确使用可以显著提高编译器的分析和优化能力。