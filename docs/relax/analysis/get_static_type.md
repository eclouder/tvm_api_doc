---
title: get_static_type
description: TVM Relax Analysis - get_static_type 函数 API 文档
---

# get_static_type

## 概述

`get_static_type` 函数是 TVM Relax 分析模块中的核心工具函数，主要用于从 Relax IR 的结构信息（StructInfo）中提取对应的静态类型信息。该函数在 Relax 编译器的类型推导和静态分析阶段发挥着关键作用。

**主要功能：**
- 将动态的 StructInfo 转换为静态的类型表示
- 为编译时的类型检查和优化提供基础类型信息
- 连接 Relax 的动态类型系统和 TVM 的静态类型系统

**在分析流程中的位置：**
该函数通常在 Relax IR 的预处理阶段被调用，用于获取变量的静态类型信息，为后续的类型检查、内存分配和优化变换提供必要的类型基础。

## 函数签名

```python
def get_static_type(sinfo: StructInfo) -> Type
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| sinfo | StructInfo | 无 | 输入的 Relax 结构信息对象，可以是 TensorStructInfo、TupleStructInfo、ShapeStructInfo 等任何 StructInfo 子类。该参数不能为 None。 |

## 返回值

**类型:** `Type`

返回与输入 StructInfo 对应的静态类型对象。返回值是 TVM 类型系统中的具体类型实例，如：
- `TensorType`：对应 TensorStructInfo
- `TupleType`：对应 TupleStructInfo  
- 其他具体的 TVM 类型

## 使用场景

### IR 结构分析
在分析 Relax IR 时，需要将动态的结构信息转换为静态类型表示，以便进行类型安全的变换和优化。

### 编译时检查
在编译阶段验证操作的输入输出类型一致性，确保 IR 变换的类型安全性。

### 优化决策支持
基于静态类型信息做出优化决策，如内存布局选择、算子融合策略等。

### 类型推导系统
作为类型推导管道的一部分，将 Relax 的高级类型信息降级为底层的静态类型。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import get_static_type

# 示例1：获取张量结构信息的静态类型
tensor_sinfo = relax.TensorStructInfo(
    shape=[1, 3, 224, 224], 
    dtype="float32"
)
static_type = get_static_type(tensor_sinfo)
print(f"静态类型: {static_type}")
# 输出: TensorType([1, 3, 224, 224], float32)

# 示例2：处理元组结构信息
tuple_sinfo = relax.TupleStructInfo([
    relax.TensorStructInfo(shape=[10], dtype="int32"),
    relax.TensorStructInfo(shape=[], dtype="float16")
])
tuple_type = get_static_type(tuple_sinfo)
print(f"元组静态类型: {tuple_type}")
# 输出: TupleType([TensorType([10], int32), TensorType([], float16)])
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import get_static_type, erase_to_well_defined

# 结合类型擦除函数进行复杂类型分析
def analyze_complex_type(sinfo):
    # 首先擦除到良定义形式
    well_defined_sinfo = erase_to_well_defined(sinfo)
    
    # 然后获取静态类型
    static_type = get_static_type(well_defined_sinfo)
    
    # 进行类型相关的分析
    if isinstance(static_type, tvm.ir.TensorType):
        print(f"张量维度: {len(static_type.shape)}")
        print(f"数据类型: {static_type.dtype}")
    elif isinstance(static_type, tvm.ir.TupleType):
        print(f"元组包含 {len(static_type.fields)} 个元素")
    
    return static_type

# 使用示例
complex_sinfo = relax.TensorStructInfo(
    shape=relax.ShapeExpr([1, 3, 224, 224]),
    dtype="float32"
)
result_type = analyze_complex_type(complex_sinfo)
```

## 实现细节

`get_static_type` 函数通过调用底层的 C++ 实现 `_ffi_api.GetStaticType` 来完成类型转换。该函数内部实现了从 Relax StructInfo 到 TVM Type 的映射逻辑：

- 对于 `TensorStructInfo`，转换为 `TensorType`
- 对于 `TupleStructInfo`，转换为 `TupleType` 
- 对于 `ShapeStructInfo`，转换为对应的整数类型
- 其他 StructInfo 子类也有相应的转换规则

## 相关函数

- [`erase_to_well_defined`](./erase_to_well_defined.md) - 将 StructInfo 擦除为良定义形式，常用于预处理
- [`struct_info_like`](./struct_info_like.md) - 基于现有值创建相似的 StructInfo
- [`get_struct_info`](./get_struct_info.md) - 从 Relax 表达式获取 StructInfo

## 注意事项

### 性能考虑
- 该函数调用涉及 FFI 边界跨越，在性能敏感的热点路径中应谨慎使用
- 考虑缓存结果以避免重复的类型转换

### 使用限制
- 输入参数必须是非空的 StructInfo 实例
- 某些复杂的 StructInfo（如包含符号变量的）可能无法完全转换为静态类型

### 常见错误
- 传入 `None` 会导致运行时错误
- 不支持的 StructInfo 类型会抛出 TypeError

### 最佳实践
- 在类型推导管道的早期阶段使用此函数
- 结合 `erase_to_well_defined` 预处理不确定的结构信息
- 对结果类型进行适当的空值检查