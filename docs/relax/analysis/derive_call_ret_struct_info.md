---
title: derive_call_ret_struct_info
description: TVM Relax Analysis - derive_call_ret_struct_info 函数 API 文档
---

# derive_call_ret_struct_info

## 概述

`derive_call_ret_struct_info` 是 TVM Relax 分析模块中的核心函数，专门用于推导函数调用的返回结构信息。该函数在 Relax IR 的编译时分析阶段起着关键作用，能够根据函数签名和具体的调用参数，精确推断出函数调用的返回值类型和形状信息。

在 TVM Relax 的分析流程中，该函数主要用于：
- 在构建 Relax IR 时进行类型推导和验证
- 支持编译时的结构信息传播
- 为后续的优化和代码生成提供准确的类型信息
- 确保函数调用在语义上的正确性

## 函数签名

```python
def derive_call_ret_struct_info(
    func_sinfo: FuncStructInfo, 
    call: Call, 
    ctx: 'tvm.relax.BlockBuilder'
) -> StructInfo
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| func_sinfo | FuncStructInfo | 无 | 被调用函数的结构信息，包含函数的参数类型、返回类型等签名信息 |
| call | Call | 无 | Relax IR 中的函数调用节点，包含实际的调用参数和上下文信息 |
| ctx | tvm.relax.BlockBuilder | 无 | Relax IR 构建器上下文，用于访问当前构建状态和环境信息 |

## 返回值

**类型:** `StructInfo`

返回推导出的函数调用结果的结构信息。这包括：
- 张量的数据类型（dtype）和形状（shape）
- 元组的结构信息（如果返回的是元组）
- 其他 Relax 数据类型的具体信息
- 可能的符号变量和约束条件

## 使用场景

### IR结构分析
在 Relax IR 构建过程中，用于分析函数调用的返回类型，确保类型一致性。

### 变量依赖分析
推导返回值中可能包含的符号变量和它们的依赖关系。

### 内存使用分析
通过返回值结构信息，预估函数调用所需的内存分配。

### 优化决策支持
为后续的优化pass提供准确的类型信息，支持优化决策。

### 编译时检查
在编译时验证函数调用的正确性，提前发现类型不匹配等问题。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import derive_call_ret_struct_info
from tvm.script import relax as R

# 创建一个简单的函数调用场景
@R.function
def simple_function(x: R.Tensor([16, 32], "float32")) -> R.Tensor([16, 32], "float32"):
    return x

# 获取函数的结构信息
func_sinfo = simple_function.struct_info

# 创建调用节点（在实际使用中，这通常由BlockBuilder自动处理）
# 这里简化示例，实际使用时需要构建完整的Call节点

# 推导返回结构信息
# result = derive_call_ret_struct_info(func_sinfo, call_node, block_builder)
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import derive_call_ret_struct_info

# 结合符号形状分析的高级用法
@R.function
def advanced_function(x: R.Tensor(["n", "m"], "float32")) -> R.Tensor(["n", "m"], "float32"):
    return x

# 在实际的IR构建过程中，该函数会自动被调用来推导返回类型
# 支持符号形状的传播和推导

# 结合其他分析函数进行完整的IR验证
def analyze_function_call(func_sinfo, call_node, ctx):
    # 推导返回结构信息
    ret_sinfo = derive_call_ret_struct_info(func_sinfo, call_node, ctx)
    
    # 进行进一步的分析
    # ... 其他分析操作
    
    return ret_sinfo
```

## 实现细节

该函数的实现基于 Relax IR 的类型系统，主要处理以下情况：

1. **函数签名匹配**：将实际的调用参数与函数签名进行匹配
2. **类型推导**：根据参数类型推导返回类型
3. **符号传播**：处理符号形状的传播和约束求解
4. **错误检测**：检测类型不匹配等语义错误

算法核心是通过遍历函数签名的参数和返回类型，将具体的调用参数信息传播到返回类型中。

## 相关函数

- [`get_struct_info`](./get_struct_info.md) - 获取 Relax 表达式的结构信息
- [`analyze_symbolic_vars`](./analyze_symbolic_vars.md) - 分析表达式中的符号变量
- [`normalize_func`](./normalize_func.md) - 规范化函数结构信息

## 注意事项

### 性能考虑
- 该函数在 IR 构建过程中会被频繁调用，应确保实现的高效性
- 对于复杂的符号形状推导，可能需要较多的计算资源

### 使用限制
- 只能用于推导 Relax 函数调用的返回结构信息
- 需要完整的函数签名信息和调用上下文
- 不支持运行时动态类型的推导

### 常见错误
- 函数签名与实际调用参数不匹配
- 符号形状约束无法满足
- 类型推导过程中出现循环依赖

### 最佳实践
- 在 IR 构建阶段尽早调用该函数进行类型检查
- 结合其他分析函数进行完整的语义验证
- 对于自定义算子，确保提供准确的函数签名信息