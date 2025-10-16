---
title: TVM Relax Analysis API 文档
description: TVM Relax 分析模块完整 API 文档索引
---

# TVM Relax Analysis API 文档

TVM Relax Analysis 模块提供了丰富的分析功能，用于分析和优化 Relax IR。本文档涵盖了所有主要的分析函数。

## 功能分类

### StructInfo 分析

结构信息相关的分析函数

- [`get_static_type`](./get_static_type.md) - Get the corresponding static type from a StructInfo
- [`erase_to_well_defined`](./erase_to_well_defined.md) - Erase sinfo into a well defined form
- [`struct_info_base_check`](./struct_info_base_check.md) - Run a base check to see if base subsumes derived
- [`derive_call_ret_struct_info`](./derive_call_ret_struct_info.md) - Derive the call's ret value struct info from inputs
- [`struct_info_lca`](./struct_info_lca.md) - Unify the two struct info to their least common ancestor
- [`tir_vars_in_struct_info`](./tir_vars_in_struct_info.md) - Get the TIR variables that appear in the input struct info
- [`definable_tir_vars_in_struct_info`](./definable_tir_vars_in_struct_info.md) - Get the TIR variables that may be defined from input struct info
- [`collect_non_negative_expressions`](./collect_non_negative_expressions.md) - Collect TIR expressions used in non-negative contexts

Get TIR variables that are non-negative within the context where
the struct info is used

### 变量分析

变量相关的分析函数

- [`defined_symbolic_vars`](./defined_symbolic_vars.md) - Get the TIR variables that defined in the input function
- [`free_symbolic_vars`](./free_symbolic_vars.md) - Get the TIR variables that are used but not defined in the input function
- [`bound_vars`](./bound_vars.md) - Return all bound variables from expression expr
- [`free_vars`](./free_vars.md) - Return all free variables from expression expr
- [`all_vars`](./all_vars.md) - Return all (local) variables from expression expr
- [`all_global_vars`](./all_global_vars.md) - Return all global variables from expression expr
- [`get_var2val`](./get_var2val.md) - Get a mapping from Var to Expr for each variable in the function
- [`computable_at_compile_time`](./computable_at_compile_time.md) - Collect variables whose value can be computed at compile-time

If a function has the `kNumInput` attribute, then the first
`kNumInput` parameters are provided at run-time, while all
remaining parameters may be known at compile-time

### 遍历分析

IR遍历相关的分析函数

- [`post_order_visit`](./post_order_visit.md) - Recursively visit the ir in post DFS order node,
apply fvisit

### 模块分析

模块级别的分析函数

- [`contains_impure_call`](./contains_impure_call.md) - Check if the given expression (likely a function body) contains any impure calls
- [`well_formed`](./well_formed.md) - Check if the IRModule is well formed
- [`detect_recursion`](./detect_recursion.md) - Find all sets of recursive or mutually recursive functions in the module

### 内存分析

内存使用相关的分析函数

- [`estimate_memory_usage`](./estimate_memory_usage.md) - Analysis function that estimates the memory usage of Relax functions
in an IRModule

### 优化分析

优化相关的分析函数

- [`has_reshape_pattern`](./has_reshape_pattern.md) - Check if the given PrimFunc is essentially doing a reshape operation
- [`suggest_layout_transforms`](./suggest_layout_transforms.md) - Suggest Layout transformations of blocks and buffers in a PrimFunc


## 快速开始

```python
import tvm
from tvm import relax
from tvm.relax.analysis import *

# 创建示例模块
mod = relax.frontend.from_pytorch(model, input_spec)

# 基本分析
is_well_formed = well_formed(mod)
memory_usage = estimate_memory_usage(mod)

# 变量分析
main_func = mod["main"]
bound_variables = bound_vars(main_func)
free_variables = free_vars(main_func)

# 遍历分析
def visit_func(node):
    print(f"访问节点: {type(node).__name__}")

post_order_visit(main_func, visit_func)
```

## 相关资源

- [TVM Relax 官方文档](https://tvm.apache.org/docs/reference/api/python/relax.html)
- [Relax Analysis 示例代码](../examples/)
- [TVM 社区论坛](https://discuss.tvm.apache.org/)
