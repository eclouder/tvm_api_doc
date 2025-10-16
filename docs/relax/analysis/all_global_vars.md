---
title: all_global_vars
description: TVM Relax Analysis - all_global_vars 函数 API 文档
---

# all_global_vars

## 概述

`all_global_vars` 函数是 TVM Relax 分析模块中的一个重要工具函数，主要用于从 Relax IR 表达式中提取所有的全局变量。该函数在 IR 结构分析和依赖分析中扮演着关键角色。

**主要功能：**
- 遍历给定的 Relax IR 表达式，识别并收集其中引用的所有全局变量
- 按照后序深度优先搜索（Post-DFS）的顺序返回全局变量列表
- 支持对函数调用、变量引用等 IR 节点的全面分析

**在分析流程中的位置：**
- 位于 Relax IR 分析流程的前期阶段，为后续的依赖分析、优化决策和内存分析提供基础数据
- 与 `free_vars`、`bound_vars` 等变量分析函数协同工作，构建完整的变量使用视图

**适用场景：**
- 模块级别的依赖关系分析
- 函数调用图的构建
- 跨函数优化决策支持
- 编译时符号解析和验证

## 函数签名

```python
def all_global_vars(expr: Expr) -> List[GlobalVar]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| expr | tvm.relax.Expr | 无 | 需要分析的 Relax IR 表达式。可以是函数定义、函数调用、序列表达式等各种 IR 节点类型。该表达式将被递归遍历以查找所有全局变量引用。 |

## 返回值

**类型:** `List[GlobalVar]`

返回一个包含所有在表达式中出现的全局变量的列表。列表中的全局变量按照**后序深度优先搜索（Post-DFS）**的顺序排列，这种顺序确保了在遍历过程中，子节点总是在父节点之前被访问，便于进行依赖分析和处理。

每个 `GlobalVar` 对象包含以下重要属性：
- `name_hint`: 全局变量的名称标识符
- `checked_type_`: 变量的类型信息（如果已进行类型推断）
- `struct_info_`: 变量的结构信息

## 使用场景

### IR 结构分析
分析函数体或模块中对外部全局函数的依赖关系，了解代码的结构组织。

### 变量依赖分析
识别函数之间的调用关系，构建函数依赖图，用于后续的优化和调度。

### 内存使用分析
通过全局变量引用分析，了解跨函数的数据流动和内存使用模式。

### 优化决策支持
为内联优化、函数特化等编译优化提供决策依据，基于实际的函数调用关系。

### 编译时检查
验证模块中全局变量的正确性，检测未定义的函数引用或循环依赖。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import all_global_vars
from tvm.script import relax as R

# 构建一个包含多个全局函数调用的 Relax IR 模块
@tvm.script.ir_module
class MyModule:
    @R.function
    def helper1(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
        return R.add(x, x)
    
    @R.function
    def helper2(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
        return R.multiply(x, x)
    
    @R.function
    def main(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
        # 调用多个全局函数
        y = helper1(x)
        z = helper2(y)
        return z

# 分析主函数中的全局变量引用
mod = MyModule
main_func = mod["main"]
global_variables = all_global_vars(main_func)

print(f"全局变量数量: {len(global_variables)}")
print(f"全局变量名称: {[var.name_hint for var in global_variables]}")
# 输出: 全局变量数量: 2
# 输出: 全局变量名称: ['helper1', 'helper2']
```

### 高级用法

```python
# 结合其他分析函数进行完整的模块分析
from tvm.relax.analysis import free_vars, bound_vars

def analyze_module_dependencies(mod: tvm.ir.IRModule):
    """分析模块中所有函数的依赖关系"""
    dependency_graph = {}
    
    for gvar, func in mod.functions.items():
        # 获取函数中引用的所有全局变量
        called_globals = all_global_vars(func)
        
        # 获取自由变量和绑定变量
        free_vars_list = free_vars(func)
        bound_vars_list = bound_vars(func)
        
        dependency_graph[gvar.name_hint] = {
            'called_functions': [gv.name_hint for gv in called_globals],
            'free_vars': [str(var) for var in free_vars_list],
            'bound_vars': [str(var) for var in bound_vars_list]
        }
    
    return dependency_graph

# 使用示例
deps = analyze_module_dependencies(mod)
for func_name, info in deps.items():
    print(f"函数 {func_name}:")
    print(f"  调用的函数: {info['called_functions']}")
    print(f"  自由变量: {info['free_vars']}")
    print(f"  绑定变量: {info['bound_vars']}")
```

## 实现细节

`all_global_vars` 函数通过 TVM 的 FFI 接口调用底层的 C++ 实现，该实现基于 Relax IR 的访问者模式（Visitor Pattern）进行递归遍历。

**算法原理：**
1. 采用后序深度优先搜索（Post-DFS）遍历 IR 表达式树
2. 对于每个 IR 节点，检查是否为 `GlobalVar` 节点或包含 `GlobalVar` 引用
3. 在遇到 `Call` 节点时，递归分析被调用函数
4. 收集所有发现的全局变量，并按遍历顺序返回

**性能特点：**
- 时间复杂度：O(n)，其中 n 是 IR 表达式中的节点数量
- 空间复杂度：O(m)，其中 m 是调用栈深度，最坏情况下为树的高度

## 相关函数

- [`free_vars`](./free_vars.md) - 获取表达式中的自由变量（未绑定的变量）
- [`bound_vars`](./bound_vars.md) - 获取表达式中的绑定变量（局部定义的变量）
- [`udchain`](./udchain.md) - 构建变量的使用-定义链分析
- [`call_tir`](./call_tir.md) - 分析 TIR 函数调用关系

## 注意事项

### 性能考虑
- 对于大型的 IR 模块，该函数可能需要遍历大量的节点，建议在需要时调用，避免重复分析
- 如果只需要检查是否存在全局变量引用，可考虑使用更轻量级的检查方法

### 使用限制
- 函数仅返回直接出现在表达式中的全局变量，不会解析间接的函数调用
- 对于动态函数调用（通过变量进行的函数调用），可能无法准确识别所有全局变量

### 常见错误
- 如果传入的表达式包含未定义的全局变量引用，函数仍会正常返回，但后续使用这些变量可能导致错误
- 确保传入的表达式是有效的 Relax IR，否则可能得到不可预期的结果

### 最佳实践
- 在模块优化前后分别调用此函数，对比分析优化效果
- 结合其他分析函数使用，获得更全面的变量使用信息
- 对于复杂的分析需求，考虑使用 Relax 提供的更高级的分析工具