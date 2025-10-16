---
title: all_vars
description: TVM Relax Analysis - all_vars 函数 API 文档
---

# all_vars

## 概述

`all_vars` 函数是 TVM Relax Analysis 模块中的核心变量分析工具，用于从 Relax IR 表达式中提取所有的局部变量。该函数在深度学习编译器的中间表示分析阶段发挥着重要作用，能够帮助开发者理解 IR 结构中的变量分布和依赖关系。

**主要功能：**
- 遍历 Relax IR 表达式，收集所有局部变量节点
- 按照后序深度优先搜索（Post-DFS）顺序返回变量列表
- 为后续的变量依赖分析、内存优化和编译时检查提供基础数据

**在分析流程中的位置：**
- 位于 Relax IR 分析流程的前端，为更复杂的分析（如数据流分析、类型推断）提供变量信息
- 与 `all_global_vars` 函数形成互补，分别处理局部变量和全局变量

**适用场景：**
- IR 结构分析和可视化
- 变量使用情况统计
- 内存分配优化
- 编译时语义检查

## 函数签名

```python
def all_vars(expr: Expr) -> List[Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| expr | tvm.relax.Expr | 无 | 需要分析的 Relax IR 表达式。可以是函数、绑定块、序列表达式或任何包含变量节点的 IR 结构。该参数不能为 None，必须是有效的 Relax IR 表达式。 |

## 返回值

**类型:** `List[tvm.relax.Var]`

返回包含表达式中所有局部变量的列表，变量按照后序深度优先搜索（Post-DFS）顺序排列。这种顺序确保了在变量依赖关系中，被依赖的变量会出现在依赖它的变量之前，便于进行依赖分析和拓扑排序。

**返回值特点：**
- 只包含局部变量，不包括全局变量
- 列表中的变量按照 Post-DFS 顺序排列
- 不包含重复变量（每个变量只出现一次）
- 如果表达式不包含任何变量，返回空列表

## 使用场景

### IR 结构分析
分析 Relax IR 函数的变量组成，了解函数的结构复杂度和变量使用模式。

### 变量依赖分析
结合变量的定义和使用信息，构建变量依赖图，用于优化和变换验证。

### 内存使用分析
统计函数中使用的变量数量和类型，为内存分配和优化提供依据。

### 优化决策支持
为编译器优化过程（如公共子表达式消除、死代码删除）提供变量使用信息。

### 编译时检查
验证 IR 的语义正确性，如检查未定义变量、变量作用域等。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import all_vars, all_global_vars
from tvm.script import relax as R

# 定义一个简单的 Relax 函数
@R.function
def main(x: R.Tensor((32, 64), "float32"), y: R.Tensor((64, 128), "float32")) -> R.Tensor:
    with R.dataflow():
        # 定义局部变量
        lv0 = R.matmul(x, y)
        lv1 = R.nn.relu(lv0)
        gv = R.add(lv1, lv0)
        R.output(gv)
    return gv

# 分析函数中的所有局部变量
all_variables = all_vars(main)
print(f"所有变量 ({len(all_variables)}): {[var.name_hint for var in all_variables]}")

# 对比全局变量分析
global_variables = all_global_vars(main)
print(f"全局变量: {[var.name_hint for var in global_variables]}")
```

输出示例：
```
所有变量 (4): ['x', 'y', 'lv0', 'lv1', 'gv']
全局变量: ['main']
```

### 高级用法

```python
# 结合其他分析函数进行综合变量分析
from tvm.relax.analysis import free_vars, defined_vars

def comprehensive_variable_analysis(func: relax.Function):
    """综合变量分析函数"""
    
    # 获取所有变量
    all_vars_list = all_vars(func)
    free_vars_list = free_vars(func)
    defined_vars_list = defined_vars(func)
    
    print("=== 综合变量分析 ===")
    print(f"总变量数: {len(all_vars_list)}")
    print(f"自由变量: {[var.name_hint for var in free_vars_list]}")
    print(f"定义变量: {[var.name_hint for var in defined_vars_list]}")
    print(f"所有变量 (Post-DFS顺序): {[var.name_hint for var in all_vars_list]}")
    
    # 分析变量使用模式
    local_vars = [var for var in all_vars_list if var not in free_vars_list]
    print(f"局部变量数: {len(local_vars)}")

# 使用综合分析
comprehensive_variable_analysis(main)
```

## 实现细节

`all_vars` 函数通过 TVM 的 FFI（Foreign Function Interface）调用底层的 C++ 实现。核心算法采用后序深度优先搜索（Post-DFS）遍历 Relax IR 表达式树：

1. **遍历策略**：后序 DFS 确保子节点在父节点之前被访问
2. **变量收集**：在遍历过程中识别并收集所有 `Var` 类型的节点
3. **去重处理**：自动处理重复变量，确保每个变量只出现一次
4. **顺序保证**：严格按照遍历顺序返回变量列表

这种实现方式保证了变量列表的拓扑顺序，便于后续的依赖分析和优化处理。

## 相关函数

- [`all_global_vars`](./all_global_vars.md) - 提取所有全局变量
- [`free_vars`](./free_vars.md) - 提取自由变量（未绑定的变量）
- [`defined_vars`](./defined_vars.md) - 提取已定义的变量
- [`udchain`](./udchain.md) - 构建变量的使用-定义链

## 注意事项

### 性能考虑
- 对于大型 IR 表达式，该函数需要遍历整个表达式树，时间复杂度为 O(n)
- 在性能敏感的场景中，建议缓存分析结果避免重复计算

### 使用限制
- 只识别 Relax IR 中的局部变量，不包含全局变量
- 返回的变量列表不包含类型信息，需要结合其他函数获取完整变量信息
- 对于嵌套作用域，会返回所有作用域中的变量

### 常见错误
- 传入 None 或无效表达式会导致运行时错误
- 混淆局部变量和全局变量可能导致分析结果不准确

### 最佳实践
- 结合 `all_global_vars` 使用以获得完整的变量视图
- 在 IR 变换前后使用该函数验证变量一致性
- 利用 Post-DFS 顺序进行依赖分析和拓扑排序