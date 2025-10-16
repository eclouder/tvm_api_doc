---
title: tir_vars_in_struct_info
description: TVM Relax Analysis - tir_vars_in_struct_info 函数 API 文档
---

# tir_vars_in_struct_info

## 概述

`tir_vars_in_struct_info` 是 TVM Relax 分析模块中的一个重要函数，主要用于从 Relax 的结构信息（StructInfo）中提取所有出现的 TIR 变量。该函数在 Relax IR 的分析流程中扮演着关键角色，特别是在处理包含动态形状和符号变量的计算图时。

**主要功能：**
- 遍历给定的 StructInfo 对象，识别其中引用的所有 TIR 变量
- 自动对结果进行去重处理，确保每个 TIR 变量在返回列表中只出现一次
- 支持所有 StructInfo 子类型，包括 TensorStructInfo、TupleStructInfo 等

**在分析流程中的作用：**
- 位于 Relax IR 的形状和类型分析阶段
- 为后续的优化和代码生成提供符号变量信息
- 与形状推导、内存规划等分析函数协同工作

## 函数签名

```python
def tir_vars_in_struct_info(sinfo: StructInfo) -> List[tir.Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| sinfo | StructInfo | 无 | 需要分析的结构信息对象。可以是任意 StructInfo 子类型，如 TensorStructInfo、TupleStructInfo 等。该参数不能为 None。 |

## 返回值

**类型:** `List[tir.Var]`

返回一个包含所有在输入 StructInfo 中出现的 TIR 变量的列表。列表中的变量已经过去重处理，每个 TIR 变量只会出现一次。如果 StructInfo 中不包含任何 TIR 变量，则返回空列表。

## 使用场景

### IR 结构分析
- 分析 Relax 函数的输入输出形状信息中的符号变量
- 识别计算图中依赖于动态形状的操作

### 变量依赖分析
- 确定形状计算中使用的符号变量及其依赖关系
- 为形状约束求解提供必要的变量信息

### 内存使用分析
- 分析动态张量的内存分配需求
- 确定内存分配策略中需要考虑的符号维度

### 优化决策支持
- 帮助优化器识别可静态化的动态计算
- 为算子融合和布局优化提供形状信息

### 编译时检查
- 验证符号形状的一致性
- 检测未绑定的符号变量

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import tir_vars_in_struct_info
from tvm.script import relax as R

# 示例1：分析包含符号变量的 TensorStructInfo
n = tvm.tir.Var("n", "int64")
m = tvm.tir.Var("m", "int64")
tensor_sinfo = relax.TensorStructInfo([n, m, 3], "float32")

# 提取 TIR 变量
tir_vars = tir_vars_in_struct_info(tensor_sinfo)
print("找到的 TIR 变量:", [var.name for var in tir_vars])
# 输出: ['n', 'm']

# 示例2：分析嵌套的 TupleStructInfo
tuple_sinfo = relax.TupleStructInfo([
    relax.TensorStructInfo([n], "float32"),
    relax.TensorStructInfo([m, 64], "float32")
])

tir_vars = tir_vars_in_struct_info(tuple_sinfo)
print("元组中的 TIR 变量:", [var.name for var in tir_vars])
# 输出: ['n', 'm']
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import tir_vars_in_struct_info, get_static_type
from tvm.script import relax as R

# 结合其他分析函数进行完整的形状分析
def analyze_function_shape(func: relax.Function):
    """分析函数中使用的所有符号变量"""
    
    # 获取函数的返回类型信息
    ret_sinfo = func.ret_struct_info
    
    # 提取返回类型中的 TIR 变量
    output_vars = tir_vars_in_struct_info(ret_sinfo)
    print("输出形状中的符号变量:", [var.name for var in output_vars])
    
    # 分析函数体中的调用参数
    all_vars = set(output_vars)
    for call in func.body:
        if hasattr(call, 'args'):
            for arg in call.args:
                arg_sinfo = get_static_type(arg)
                arg_vars = tir_vars_in_struct_info(arg_sinfo)
                all_vars.update(arg_vars)
    
    print("函数中使用的所有符号变量:", [var.name for var in all_vars])
    return list(all_vars)

# 创建测试函数
@R.function
def test_func(x: R.Tensor(["n", "m"], "float32")) -> R.Tensor(["n", 64], "float32"):
    # 函数实现...
    return x

# 执行分析
symbolic_vars = analyze_function_shape(test_func)
```

## 实现细节

该函数通过调用底层的 C++ 实现 `_ffi_api.TIRVarsInStructInfo` 来完成实际的变量提取工作。实现原理是基于访问者模式遍历 StructInfo 的 AST，收集所有遇到的 TIR 变量节点。

**算法特点：**
- 深度优先遍历 StructInfo 结构
- 使用哈希集合进行自动去重
- 支持所有 StructInfo 变体的递归处理

## 相关函数

- [`get_static_type`](./get_static_type.md) - 获取表达式的静态类型信息
- [`analyze_symbolic_var_bounds`](./analyze_symbolic_var_bounds.md) - 分析符号变量的边界约束
- [`get_var_to_shape`](./get_var_to_shape.md) - 获取变量到形状的映射关系

## 注意事项

### 性能考虑
- 对于复杂的嵌套 StructInfo，函数可能需要遍历整个结构树
- 在处理大型计算图时，建议缓存分析结果以避免重复计算

### 使用限制
- 输入参数必须为有效的 StructInfo 对象，不能为 None
- 函数只识别直接出现在 StructInfo 中的 TIR 变量，不处理通过表达式间接引用的变量

### 常见错误
- 如果传入的对象不是 StructInfo 类型，会导致类型错误
- 未处理的符号变量可能导致后续编译阶段失败

### 最佳实践
- 在形状推导完成后调用此函数，确保 StructInfo 包含完整的形状信息
- 结合其他分析函数使用，获得更全面的符号变量信息
- 对结果进行排序或分类，便于后续处理