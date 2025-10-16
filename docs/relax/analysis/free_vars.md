---
title: free_vars
description: TVM Relax Analysis - free_vars 函数 API 文档
---

# free_vars

## 概述

`free_vars` 函数是 TVM Relax 分析模块中的核心变量分析工具，用于提取 Relax IR 表达式中的所有自由变量。自由变量是指在表达式中未被任何 VarBinding 或函数参数绑定的变量，这些变量通常来自外部作用域，对理解表达式的依赖关系和变量作用域至关重要。

在 Relax IR 分析流程中，该函数位于变量分析阶段，主要用于识别表达式中对外部变量的依赖。它与 `all_vars`、`bound_vars` 等函数配合使用，共同构成完整的变量分析工具集。该函数在以下场景中特别有用：依赖分析、作用域验证、内存分配优化和编译器优化决策。

## 函数签名

```python
def free_vars(expr: Expr) -> List[Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| expr | Expr | 无 | 需要分析自由变量的 Relax IR 表达式。可以是任何 Relax IR 节点类型，包括函数、绑定块、序列表达式等。该参数不能为 None。 |

## 返回值

**类型:** `List[Var]`

返回表达式中所有自由变量的列表，按照后序深度优先搜索（Post-DFS）顺序排列。每个变量都是 `tvm.relax.Var` 类型的实例，包含变量的名称、类型信息和其他属性。列表中的变量顺序对于保持分析结果的一致性很重要，特别是在涉及变量依赖关系的场景中。

## 使用场景

### IR 结构分析
- 分析函数体对外部变量的依赖关系
- 识别闭包中捕获的外部变量
- 验证 IR 结构的正确性

### 变量依赖分析
- 确定表达式计算所需的输入变量
- 分析数据流依赖关系
- 识别潜在的未初始化变量使用

### 内存使用分析
- 确定需要分配内存的变量集合
- 分析变量的生命周期和作用域

### 优化决策支持
- 为内联优化提供依赖信息
- 支持死代码消除和常量传播
- 辅助函数特化和部分求值

### 编译时检查
- 检测未声明变量的使用
- 验证变量作用域规则
- 检查闭包的正确性

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import free_vars, all_vars
from tvm.script import relax as R

# 创建一个简单的 Relax 函数
@R.function
def main(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 外部变量 y 在函数内部使用，是自由变量
    y = R.add(x, x)
    z = R.multiply(y, R.const(2.0, "float32"))
    return z

# 分析自由变量
free_variables = free_vars(main)
print(f"自由变量 ({len(free_variables)}): {[var.name_hint for var in free_variables]}")

# 对比所有变量
all_variables = all_vars(main)
print(f"所有变量 ({len(all_variables)}): {[var.name_hint for var in all_variables]}")
```

### 高级用法

```python
# 结合其他分析函数进行复杂分析
from tvm.relax.analysis import bound_vars

def analyze_function_dependencies(func):
    """分析函数的变量依赖关系"""
    free_vars_list = free_vars(func)
    bound_vars_list = bound_vars(func)
    all_vars_list = all_vars(func)
    
    print("=== 函数依赖分析 ===")
    print(f"自由变量: {[var.name_hint for var in free_vars_list]}")
    print(f"绑定变量: {[var.name_hint for var in bound_vars_list]}")
    print(f"所有变量: {[var.name_hint for var in all_vars_list]}")
    
    # 计算依赖比率
    dependency_ratio = len(free_vars_list) / len(all_vars_list) if all_vars_list else 0
    print(f"外部依赖比率: {dependency_ratio:.2f}")
    
    return {
        'free_vars': free_vars_list,
        'bound_vars': bound_vars_list,
        'all_vars': all_vars_list,
        'dependency_ratio': dependency_ratio
    }

# 分析闭包场景
@R.function
def outer_func(a: R.Tensor((16,), "float32")):
    @R.function
    def inner_func(b: R.Tensor((16,), "float32")):
        # a 是自由变量，b 是参数
        return R.add(a, b)
    return inner_func

# 分析内层函数的自由变量
inner_func = outer_func.body
analysis_result = analyze_function_dependencies(inner_func)
```

## 实现细节

`free_vars` 函数通过 TVM 的 FFI 接口调用底层的 C++ 实现，使用后序深度优先搜索（Post-DFS）算法遍历 Relax IR 表达式。算法会跳过以下情况中的变量：
- 在 VarBinding 中被绑定的变量
- 函数参数中声明的变量
- 在局部作用域内定义的变量

该实现确保了分析的高效性和准确性，能够处理复杂的嵌套 IR 结构。

## 相关函数

- [`all_vars`](./all_vars.md) - 获取表达式中所有变量的集合
- [`bound_vars`](./bound_vars.md) - 获取表达式中被绑定的变量
- [`defined_vars`](./defined_vars.md) - 获取表达式中已定义的变量

## 注意事项

### 性能考虑
- 对于大型 IR 表达式，该函数可能需要较长的计算时间
- 建议在需要时调用，避免在性能关键路径中重复调用

### 使用限制
- 只能分析 Relax IR 表达式，不支持其他类型的输入
- 对于循环和条件表达式中的变量，分析结果可能包含预期的自由变量

### 常见错误
- 传入 None 或无效表达式会导致运行时错误
- 混淆自由变量和所有变量的概念

### 最佳实践
- 在优化通道之前进行变量分析
- 结合其他分析函数获得完整的变量信息
- 注意变量列表的顺序可能影响后续处理逻辑

该函数在 TVM Relax 编译器中广泛应用于优化决策、内存管理和代码生成阶段，是理解 Relax IR 变量依赖关系的重要工具。