---
title: detect_recursion
description: TVM Relax Analysis - detect_recursion 函数 API 文档
---

# detect_recursion

## 概述

`detect_recursion` 是 TVM Relax 分析模块中的一个关键函数，专门用于检测 IRModule 中的递归和相互递归函数关系。该函数通过分析函数间的引用关系，识别出所有形成循环引用的函数组，为后续的编译优化和代码生成提供重要的结构信息。

在 Relax IR 分析流程中，该函数通常位于中间表示（IR）转换和优化阶段之前，帮助编译器理解函数间的依赖关系，特别是递归调用模式。这对于避免无限递归、优化尾递归、以及进行正确的内存分配等编译决策至关重要。

该函数与 `call_graph` 分析密切相关，但专注于检测循环引用模式，是函数依赖分析的重要组成部分。

## 函数签名

```python
def detect_recursion(mod: tvm.IRModule) -> List[List[GlobalVar]]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| mod | tvm.IRModule | 无 | 要分析的 Relax IR 模块，包含需要检测递归关系的函数定义。该模块必须包含完整的函数定义和全局变量信息。 |

## 返回值

**类型:** `List[List[GlobalVar]]`

返回一个列表，其中每个元素都是一个 `GlobalVar` 列表，表示一组相互递归的函数。如果函数是简单的自递归（不与其他函数形成相互递归），则会作为单元素列表出现在结果中。每个 `GlobalVar` 代表模块中的一个全局函数，可以通过 `name_hint` 属性获取函数名。

## 使用场景

### IR 结构分析
- 识别模块中的递归调用模式，为后续的 IR 转换提供结构信息
- 分析函数间的复杂依赖关系，特别是循环引用

### 优化决策支持
- 为尾递归优化提供检测基础
- 帮助编译器决定是否需要为递归函数生成特殊处理代码
- 在内存分配优化中考虑递归调用的栈使用情况

### 编译时检查
- 检测潜在的无限递归风险
- 验证函数调用关系的正确性
- 为调试和验证提供递归关系信息

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import detect_recursion

# 创建一个包含递归函数的模块
mod = tvm.IRModule({
    "factorial": relax.Function(
        params=[n],
        body=relax.IfThenElse(
            condition=(n == 0),
            then_block=relax.const(1),
            else_block=relax.Call("factorial", [n - 1]) * n
        ),
        ret_struct_info=relax.ObjectStructInfo()
    ),
    "mutual_a": relax.Function(
        params=[x],
        body=relax.Call("mutual_b", [x - 1]),
        ret_struct_info=relax.ObjectStructInfo()
    ),
    "mutual_b": relax.Function(
        params=[y],
        body=relax.Call("mutual_a", [y + 1]),
        ret_struct_info=relax.ObjectStructInfo()
    )
})

# 检测递归函数
recursive_functions = detect_recursion(mod)
print(f"递归函数组: {len(recursive_functions)}")
for i, group in enumerate(recursive_functions):
    print(f"  组 {i+1}: {[func.name_hint for func in group]}")
```

输出示例：
```
递归函数组: 2
  组 1: ['factorial']
  组 2: ['mutual_a', 'mutual_b']
```

### 高级用法

```python
# 结合其他分析函数进行综合优化分析
from tvm.relax.analysis import call_graph, has_impure_ops

def analyze_recursive_patterns(mod):
    """综合分析模块中的递归模式"""
    
    # 检测递归函数
    recursive_groups = detect_recursion(mod)
    
    # 分析调用图
    cg = call_graph(mod)
    
    # 分析每个递归组的特性
    for group in recursive_groups:
        group_names = [func.name_hint for func in group]
        print(f"递归组: {group_names}")
        
        # 检查是否包含副作用操作
        for func_name in group_names:
            func = mod[func_name]
            if has_impure_ops(func):
                print(f"  - {func_name} 包含副作用操作")
        
        # 分析调用关系
        for caller in group_names:
            for callee in group_names:
                if caller != callee and callee in cg[caller]:
                    print(f"  - {caller} -> {callee}")

# 使用综合分析
analyze_recursive_patterns(mod)
```

## 实现细节

`detect_recursion` 函数基于图论中的强连通分量（Strongly Connected Components, SCC）算法实现。具体步骤包括：

1. **构建函数引用图**：将模块中的函数作为节点，函数间的引用关系（包括调用和返回）作为有向边
2. **检测强连通分量**：使用 Tarjan 算法或 Kosaraju 算法找到图中的所有强连通分量
3. **过滤有效递归组**：只保留包含多个节点或自引用的强连通分量作为递归组

该实现能够处理各种复杂的递归模式，包括：
- 直接递归：函数直接调用自身
- 间接递归：通过中间函数形成的递归链
- 相互递归：多个函数形成的循环调用

## 相关函数

- [`call_graph`](./call_graph.md) - 构建完整的函数调用图，提供详细的调用关系信息
- [`has_impure_ops`](./has_impure_ops.md) - 检测函数是否包含副作用操作，对递归函数优化很重要
- [`well_formed`](./well_formed.md) - 验证 IR 的结构正确性，包括递归关系的合理性

## 注意事项

### 性能考虑
- 对于大型模块，该函数的时间复杂度为 O(V+E)，其中 V 是函数数量，E 是引用关系数量
- 建议在需要时调用，避免在编译流程中重复调用

### 使用限制
- 只能检测显式的函数引用关系，无法分析通过高阶函数或动态分发实现的递归
- 对于包含外部函数调用的模块，结果可能不完整

### 最佳实践
- 在优化递归函数之前总是先调用此函数确认递归模式
- 结合 `call_graph` 分析获得更完整的调用关系信息
- 对于检测到的递归组，考虑使用尾递归优化或迭代重写来提高性能

### 常见错误
- 忽略单元素递归组（自递归），这些同样需要特殊处理
- 未考虑函数引用（非调用）形成的递归关系
- 在模块转换后未重新检测递归关系，导致使用过时的信息