---
title: bound_vars
description: TVM Relax Analysis - bound_vars 函数 API 文档
---

# bound_vars

## 概述

`bound_vars` 函数是 TVM Relax 分析模块中的核心变量分析工具，用于提取 Relax IR 表达式中的所有绑定变量。绑定变量是指在表达式内部声明和定义的变量，这些变量的作用域仅限于该表达式内部，不能在其外部使用。

在 TVM Relax 分析流程中，该函数主要用于：
- 识别表达式内部的局部变量定义
- 分析变量的作用域范围
- 支持变量依赖性和数据流分析
- 为后续的优化和编译决策提供变量使用信息

该函数与 `free_vars` 函数形成互补关系，`bound_vars` 关注内部定义的变量，而 `free_vars` 关注外部引用的变量，两者共同构成了完整的变量使用分析。

## 函数签名

```python
def bound_vars(expr: Expr) -> List[Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| expr | tvm.relax.Expr | 无 | 需要分析的 Relax IR 表达式。可以是函数、绑定块、序列表达式等各种 Relax IR 节点类型。该表达式将用于提取其中所有绑定的变量。 |

## 返回值

**类型:** `List[tvm.relax.Var]`

返回包含表达式中所有绑定变量的列表。变量按照后序深度优先搜索（Post-DFS）的顺序排列，这种顺序确保了在变量依赖关系中，被依赖的变量会出现在依赖它的变量之前。返回的列表可能包含重复的变量（如果同一变量在多个位置被绑定），但通常每个变量只出现一次。

## 使用场景

### IR 结构分析
- 分析函数体内部的局部变量定义
- 识别绑定块（BindingBlock）中的中间变量
- 理解 Relax IR 表达式的变量作用域结构

### 变量依赖分析
- 与 `free_vars` 结合使用，分析变量的完整使用模式
- 识别变量之间的依赖关系链
- 支持数据流分析和优化

### 内存使用分析
- 分析局部变量的内存分配需求
- 支持内存优化和重用策略

### 编译时检查
- 验证变量作用域的正确性
- 检测未定义变量或作用域违规使用
- 支持类型推断和验证

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import bound_vars, free_vars
from tvm.script import relax as R

# 创建一个简单的 Relax 函数
@R.function
def main_func(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 绑定变量 y
    y = R.add(x, x)
    # 绑定变量 z
    z = R.multiply(y, R.const(2.0, "float32"))
    return z

# 分析绑定变量
bound_variables = bound_vars(main_func)
print(f"绑定变量数量: {len(bound_variables)}")
print(f"绑定变量名称: {[var.name_hint for var in bound_variables]}")

# 对比分析自由变量
free_variables = free_vars(main_func)
print(f"自由变量数量: {len(free_variables)}")
print(f"自由变量名称: {[var.name_hint for var in free_variables]}")
```

### 高级用法

```python
# 结合其他分析函数进行完整的变量分析
from tvm.relax.analysis import all_vars, defined_vars

def comprehensive_variable_analysis(func):
    """执行全面的变量分析"""
    all_vars_list = all_vars(func)
    bound_vars_list = bound_vars(func)
    free_vars_list = free_vars(func)
    defined_vars_list = defined_vars(func)
    
    print("=== 变量分析报告 ===")
    print(f"所有变量: {[v.name_hint for v in all_vars_list]}")
    print(f"绑定变量: {[v.name_hint for v in bound_vars_list]}")
    print(f"自由变量: {[v.name_hint for v in free_vars_list]}")
    print(f"定义变量: {[v.name_hint for v in defined_vars_list]}")
    
    # 分析变量使用模式
    bound_set = set(var.name_hint for var in bound_vars_list)
    free_set = set(var.name_hint for var in free_vars_list)
    
    print(f"纯局部变量: {bound_set - free_set}")
    print(f"输入输出变量: {free_set & bound_set}")

# 执行分析
comprehensive_variable_analysis(main_func)
```

## 实现细节

`bound_vars` 函数通过 TVM 的 FFI 接口调用底层的 C++ 实现。算法采用后序深度优先搜索（Post-DFS）遍历 Relax IR 表达式树，收集所有在表达式内部绑定的变量。这种遍历顺序确保了变量按照其定义和使用的自然顺序出现，便于后续的分析和处理。

底层实现会处理各种 Relax IR 节点类型，包括：
- 变量绑定（VarBinding）
- 函数定义（Function）
- 序列表达式（SeqExpr）
- 绑定块（BindingBlock）
- 等各种表达式节点

## 相关函数

- [`free_vars`](./free_vars.md) - 提取表达式中引用的自由变量（外部变量）
- [`all_vars`](./all_vars.md) - 提取表达式中所有出现的变量
- [`defined_vars`](./defined_vars.md) - 提取在表达式作用域内定义的变量

## 注意事项

### 性能考虑
- 对于大型的 Relax IR 表达式，该函数需要遍历整个表达式树，时间复杂度为 O(n)，其中 n 是表达式节点数量
- 在性能敏感的分析流程中，建议缓存分析结果以避免重复计算

### 使用限制
- 函数只分析静态的 Relax IR 结构，不涉及运行时行为
- 返回的变量列表可能包含在后续优化中被消除的临时变量
- 对于复杂的控制流结构，变量的绑定关系可能需要结合数据流分析来理解

### 常见错误
- 误将绑定变量当作全局变量使用
- 忽略变量的作用域限制
- 未正确处理重复绑定的变量

### 最佳实践
- 结合 `free_vars` 进行完整的变量分析
- 在变量优化前后对比绑定变量的变化
- 使用变量分析结果指导内存分配和优化策略