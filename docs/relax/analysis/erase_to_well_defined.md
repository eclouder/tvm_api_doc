---
title: erase_to_well_defined
description: TVM Relax Analysis - erase_to_well_defined 函数 API 文档
---

# erase_to_well_defined

## 概述

`erase_to_well_defined` 是 TVM Relax 分析模块中的一个核心函数，主要用于将给定的 StructInfo 转换为良定义（well-defined）的形式。该函数通过擦除或替换未定义或符号化的变量，确保 StructInfo 在编译时具有明确的语义定义。

在 Relax IR 分析流程中，该函数通常位于类型推导和形状推断之后，用于清理和规范化 StructInfo，为后续的优化和代码生成阶段提供可靠的类型信息。它与 `get_struct_info`、`struct_info_lower` 等函数协同工作，共同构建完整的类型分析系统。

## 函数签名

```python
def erase_to_well_defined(
    sinfo: StructInfo,
    shape_var_map: Dict[tir.Var, tir.PrimExpr] = None,
    var_map: Dict[Var, Expr] = None
) -> StructInfo
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| sinfo | StructInfo | - | 需要转换为良定义形式的输入 StructInfo，可以是 TensorStructInfo、TupleStructInfo 等类型 |
| shape_var_map | Dict[tir.Var, tir.PrimExpr] | None | 形状变量映射表，用于将符号化的形状变量替换为具体的 PrimExpr 表达式 |
| var_map | Dict[Var, Expr] | None | 变量映射表，用于将 Relax 变量替换为具体的表达式 |

## 返回值

**类型:** `StructInfo`

返回经过擦除和规范化后的良定义 StructInfo。该 StructInfo 具有以下特点：
- 所有符号化的形状变量都被具体值或已知变量替换
- 未定义的变量被移除或替换
- 保持了原始 StructInfo 的语义完整性
- 适合用于编译时的类型检查和优化决策

## 使用场景

### IR 结构分析
在 Relax IR 转换过程中，当需要确保 StructInfo 不包含未定义的符号变量时使用。

### 变量依赖分析
用于分析并清理 StructInfo 中的变量依赖关系，消除循环依赖或未定义依赖。

### 内存使用分析
在内存分配和布局优化前，确保张量形状信息是良定义的。

### 优化决策支持
为后续的算子融合、内存优化等编译优化提供可靠的类型基础。

### 编译时检查
在代码生成前验证 StructInfo 的完整性和正确性。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import erase_to_well_defined
from tvm.relax import TensorStructInfo

# 创建包含符号变量的 TensorStructInfo
n = tir.Var("n", "int64")
tensor_sinfo = TensorStructInfo([n, 128], "float32")
print(f"原始 StructInfo: {tensor_sinfo}")

# 擦除到良定义形式
erased_sinfo = erase_to_well_defined(tensor_sinfo)
print(f"擦除后的 StructInfo: {erased_sinfo}")

# 使用形状变量映射
shape_var_map = {n: tir.IntImm("int64", 64)}
erased_with_map = erase_to_well_defined(tensor_sinfo, shape_var_map=shape_var_map)
print(f"使用映射后的 StructInfo: {erased_with_map}")

# 创建另一个 StructInfo 进行比较
tensor_sinfo2 = TensorStructInfo([10, 20], "float32")
erased_sinfo2 = erase_to_well_defined(tensor_sinfo2)
print(f"固定形状的擦除结果: {erased_sinfo2}")
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import erase_to_well_defined, get_struct_info
from tvm.relax import Var, TensorStructInfo, TupleStructInfo

# 结合其他分析函数的高级用法
def analyze_and_erase(expr: Expr):
    # 首先获取表达式的 StructInfo
    original_sinfo = get_struct_info(expr)
    print(f"原始 StructInfo: {original_sinfo}")
    
    # 然后擦除到良定义形式
    well_defined_sinfo = erase_to_well_defined(original_sinfo)
    print(f"良定义 StructInfo: {well_defined_sinfo}")
    
    return well_defined_sinfo

# 处理复杂嵌套结构
tensor1 = TensorStructInfo([32, 64], "float32")
tensor2 = TensorStructInfo([tir.Var("m", "int64"), 128], "float32")
tuple_sinfo = TupleStructInfo([tensor1, tensor2])

# 擦除嵌套结构中的未定义变量
erased_tuple = erase_to_well_defined(tuple_sinfo)
print(f"擦除后的元组 StructInfo: {erased_tuple}")
```

## 实现细节

`erase_to_well_defined` 函数的实现基于访问者模式，通过递归遍历 StructInfo 的各个组成部分：

1. **TensorStructInfo 处理**：检查形状维度中的符号变量，根据提供的映射表进行替换
2. **TupleStructInfo 处理**：递归处理元组中的每个元素
3. **FuncStructInfo 处理**：处理函数参数和返回值的 StructInfo
4. **ObjectStructInfo 处理**：处理不透明对象类型

算法核心是通过深度优先搜索遍历 StructInfo 树，在遇到符号变量时查找映射表进行替换，如果找不到对应的映射则保持原样或进行适当的默认处理。

## 相关函数

- [`get_struct_info`](./get_struct_info.md) - 获取表达式对应的 StructInfo
- [`struct_info_lower`](./struct_info_lower.md) - 将高级 StructInfo 转换为低级表示
- [`analyze_var2val`](./analyze_var2val.md) - 分析变量到值的映射关系

## 注意事项

### 性能考虑
- 对于复杂的嵌套 StructInfo，该函数可能涉及多次递归遍历
- 在大规模 IR 中使用时，建议缓存结果以避免重复计算

### 使用限制
- 如果提供了不完整的映射表，可能导致某些符号变量无法被正确替换
- 对于循环依赖的变量映射，函数可能无法正确处理

### 常见错误
- 未提供必要的变量映射导致符号变量残留
- 映射表中变量类型不匹配导致的替换错误

### 最佳实践
- 在使用前确保提供了完整的变量映射信息
- 结合 `get_struct_info` 使用以获得准确的输入 StructInfo
- 在优化管道的早期阶段使用，确保后续分析的可靠性