---
title: contains_impure_call
description: TVM Relax Analysis - contains_impure_call 函数 API 文档
---

# contains_impure_call

## 概述

`contains_impure_call` 是 TVM Relax 分析模块中的一个关键函数，用于检测给定的 Relax IR 表达式是否包含具有可见副作用的函数调用（即不纯调用）。该函数在编译优化过程中起着重要作用，帮助编译器识别可能影响程序行为的副作用操作。

**主要功能：**
- 检测表达式中的不纯函数调用
- 支持递归函数的分析，可忽略自调用
- 基于 StructInfo 注解进行纯度判断

**在 Relax IR 分析流程中的位置：**
该函数通常在 IR 规范化之后使用，作为优化前的分析步骤，帮助确定哪些函数或表达式可能包含副作用，从而影响优化策略的选择。

## 函数签名

```python
def contains_impure_call(expr: Expr, own_name: Optional[Union[Var, GlobalVar]] = None) -> bool
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| expr | Expr | 无 | 要检查的 Relax IR 表达式。如果表达式是一个函数，函数会自动检查其函数体。 |
| own_name | Optional[Union[Var, GlobalVar]] | None | 对于递归函数，可以指定函数自身的名称，分析时会忽略这些自调用，避免误判为不纯调用。 |

## 返回值

**类型:** `bool`

返回一个布尔值，表示给定的表达式是否包含不纯调用：
- `True`: 表达式中存在至少一个具有可见副作用的函数调用
- `False`: 表达式中没有检测到不纯调用

## 使用场景

### IR 结构分析
在优化 Relax IR 时，需要识别哪些部分包含副作用操作，以便：
- 确定重排序优化的安全性
- 识别不可消除的函数调用
- 验证函数纯度假设

### 优化决策支持
编译器优化器使用此函数来判断：
- 是否可以安全地进行死代码消除
- 是否可以进行函数内联
- 循环和表达式重排序的可行性

### 编译时检查
在编译过程中验证程序的语义正确性，确保副作用操作得到正确处理。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import contains_impure_call
from tvm.script import relax as R

# 创建一个简单的 Relax 函数
@R.function
def pure_function(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 纯操作 - 没有副作用
    y = R.add(x, x)
    return y

@R.function  
def impure_function(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 假设这是一个有副作用的操作
    # 在实际使用中，这可能是打印、文件操作等
    y = R.print(x)  # 假设的副作用操作
    z = R.add(x, x)
    return z

# 检查函数纯度
is_pure = contains_impure_call(pure_function)
is_impure = contains_impure_call(impure_function)

print(f"纯函数检测结果: {is_pure}")      # 输出: False
print(f"不纯函数检测结果: {is_impure}")  # 输出: True
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import contains_impure_call
from tvm.script import relax as R

# 递归函数分析示例
@R.function
def recursive_function(n: R.Tensor((), "int32"), x: R.Tensor((32,), "float32")) -> R.Tensor((32,), "float32"):
    # 递归函数，包含自调用但可能没有其他副作用
    cond = R.equal(n, R.const(0, "int32"))
    with R.if_scope(cond):
        return x
    with R.else_scope():
        new_n = R.subtract(n, R.const(1, "int32"))
        # 递归调用 - 这不是副作用操作
        return recursive_function(new_n, x)

# 检查递归函数，忽略自调用
func_var = recursive_function  # 获取函数变量
is_impure = contains_impure_call(recursive_function, own_name=func_var)

print(f"递归函数不纯调用检测: {is_impure}")  # 如果只有自调用，应该返回 False

# 结合其他分析函数使用
from tvm.relax.analysis import well_formed

# 先验证 IR 格式正确性，再进行纯度分析
if well_formed(recursive_function):
    purity_result = contains_impure_call(recursive_function, own_name=func_var)
    print(f"格式正确的递归函数纯度: {not purity_result}")
```

## 实现细节

`contains_impure_call` 函数基于 Relax IR 的 StructInfo 注解系统进行纯度分析。其核心实现通过 TVM 的 C++ FFI 接口调用底层分析逻辑：

1. **遍历 IR 结构**: 递归遍历给定的表达式，识别所有的函数调用节点
2. **副作用检测**: 对于每个函数调用，检查其 StructInfo 中是否标记为具有副作用
3. **递归处理**: 对于复合表达式（如 SeqExpr、If 等），递归检查所有子表达式
4. **自调用过滤**: 当提供 `own_name` 参数时，忽略对自身函数的调用

## 相关函数

- [`well_formed`](./well_formed.md) - 检查 Relax IR 格式正确性
- [`analyze_side_effect`](./analyze_side_effect.md) - 详细的副作用分析
- [`get_struct_info`](./get_struct_info.md) - 获取表达式的结构信息

## 注意事项

### 前置条件
- **必须进行 IR 规范化**: 函数依赖于 StructInfo 注解，确保在使用前对模块进行了规范化处理
- **格式正确的 IR**: 建议先使用 `well_formed` 检查 IR 格式正确性

### 使用限制
- **嵌套函数**: 嵌套函数中的不纯调用不会影响外层函数的纯度判断，除非嵌套函数被实际调用
- **动态调度**: 对于动态调度的函数调用，纯度判断可能不够精确

### 最佳实践
1. 在优化前使用此函数验证纯度假设
2. 对于递归函数，始终提供 `own_name` 参数以避免误判
3. 结合其他分析函数进行全面的 IR 验证

### 性能考虑
- 该函数需要遍历整个表达式树，对于大型 IR 可能有性能开销
- 建议在需要时调用，避免在性能关键路径中频繁使用