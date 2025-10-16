---
title: free_symbolic_vars
description: TVM Relax Analysis - free_symbolic_vars 函数 API 文档
---

# free_symbolic_vars

## 概述

`free_symbolic_vars` 函数是 TVM Relax 分析模块中的重要工具，用于识别 Relax 函数中使用的但未定义的 TIR 符号变量。该函数的主要作用是：

- **符号变量分析**：检测函数体中引用的外部符号变量，这些变量通常在函数外部定义，用于表示动态形状、循环边界等编译时常量
- **依赖关系识别**：帮助编译器理解函数对输入形状和其他符号参数的依赖关系
- **编译优化支持**：为后续的优化过程（如内存分配、循环变换等）提供必要的符号信息

在 Relax IR 分析流程中，该函数通常位于中间表示转换和优化阶段，与其他分析函数（如 `bound_vars`、`all_vars`）配合使用，共同构建完整的变量依赖图。

## 函数签名

```python
def free_symbolic_vars(func: Function) -> List[Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| func | Function | 无 | 需要分析的 Relax 函数对象。必须是有效的 Relax Function 类型，包含完整的函数定义和主体。 |

## 返回值

**类型:** `List[Var]`

返回一个去重后的 TIR 变量列表，包含所有在函数中使用但未在函数内部定义的符号变量。每个变量在列表中只出现一次，列表顺序不保证特定的语义。

## 使用场景

### IR 结构分析
- 分析函数对符号形状的依赖关系
- 识别需要从外部传入的符号参数

### 变量依赖分析  
- 构建符号变量的使用-定义链
- 检测潜在的未定义变量使用

### 编译时检查
- 验证函数符号依赖的完整性
- 确保所有使用的符号变量都有相应的定义

### 优化决策支持
- 为动态形状推理提供输入
- 指导内存分配和循环优化策略

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import free_symbolic_vars
from tvm.script import relax as R

# 创建一个包含符号变量的 Relax 函数
@R.function
def example_func(x: R.Tensor(["n", "m"], "float32")) -> R.Tensor(["n", "m"], "float32"):
    # 使用符号变量 n, m，但未在函数内部定义
    return x

# 分析函数的自由符号变量
func = example_func
free_vars = free_symbolic_vars(func)

print("自由符号变量:", free_vars)
# 输出: [Var(n), Var(m)]
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import free_symbolic_vars, bound_vars
from tvm.script import relax as R

# 结合其他分析函数进行完整的变量分析
@R.function  
def complex_func(x: R.Tensor(["batch", "seq_len"], "float32"), 
                y: R.Tensor(["seq_len", "hidden"], "float32")) -> R.Tensor:
    # 使用外部定义的符号变量
    z = R.matmul(x, y)  # 输出形状: [batch, hidden]
    return z

func = complex_func

# 分析自由符号变量
free_sym_vars = free_symbolic_vars(func)
print("自由符号变量:", free_sym_vars)
# 输出: [Var(batch), Var(seq_len), Var(hidden)]

# 结合绑定变量分析进行对比
bound_vars_list = bound_vars(func)
print("绑定变量:", bound_vars_list)
```

## 实现细节

该函数通过遍历 Relax 函数的 AST（抽象语法树）来实现符号变量分析：

1. **变量收集**：遍历函数体中的所有表达式，收集使用的所有 TIR 变量
2. **定义过滤**：过滤掉在函数内部定义的变量（如参数、局部变量）
3. **去重处理**：确保返回的列表中每个符号变量只出现一次
4. **类型检查**：验证收集到的变量确实是 TIR 符号变量类型

底层实现依赖于 TVM 的 FFI 接口调用 C++ 实现的分析函数，确保了分析的高效性和准确性。

## 相关函数

- [`bound_vars`](./bound_vars.md) - 获取函数中定义的所有变量
- [`all_vars`](./all_vars.md) - 获取函数中使用的所有变量
- [`defined_symbolic_vars`](./defined_symbolic_vars.md) - 获取函数中定义的符号变量

## 注意事项

### 性能考虑
- 对于大型函数，该函数的分析可能有一定的性能开销
- 建议在需要时调用，避免在性能关键路径中频繁使用

### 使用限制
- 只能分析完整的 Relax Function 对象，不能用于部分表达式
- 返回的变量列表不包含重复项，但顺序可能不稳定

### 常见错误
- 如果传入的不是 Function 类型，会抛出类型错误
- 对于包含复杂控制流的函数，分析结果可能不包含所有路径的变量

### 最佳实践
- 在形状推理和内存规划阶段使用该函数
- 结合其他变量分析函数获得完整的变量使用情况
- 对分析结果进行适当的空值检查