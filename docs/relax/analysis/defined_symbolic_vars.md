---
title: defined_symbolic_vars
description: TVM Relax Analysis - defined_symbolic_vars 函数 API 文档
---

# defined_symbolic_vars

## 概述

`defined_symbolic_vars` 是 TVM Relax 分析模块中的一个重要函数，主要用于提取 Relax 函数中定义的所有符号变量（TIR 变量）。这些符号变量通常用于表示张量的动态维度，如批量大小、序列长度等动态形状参数。

在 TVM Relax 的分析流程中，该函数扮演着以下关键角色：
- **符号变量识别**：自动识别函数中所有显式定义的符号变量
- **去重处理**：确保返回的变量列表中每个符号变量只出现一次
- **IR 分析基础**：为后续的形状推导、内存分配和优化决策提供基础信息
- **编译时支持**：在编译阶段帮助确定动态形状的计算图结构

该函数与 `bound_symbolic_vars`、`free_symbolic_vars` 等函数协同工作，共同构成 Relax IR 中符号变量的完整分析体系。

## 函数签名

```python
def defined_symbolic_vars(func: Function) -> List[Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| func | Function | 无 | 需要分析的 Relax 函数对象。必须是有效的 Relax Function 类型，包含完整的 IR 结构信息。 |

## 返回值

**类型:** `List[Var]`

返回一个包含所有在输入函数中定义的符号变量的列表。列表中的每个元素都是 `tvm.tir.Var` 类型，表示一个符号变量。返回的列表经过去重处理，确保每个符号变量在列表中只出现一次。如果函数中没有定义任何符号变量，则返回空列表。

## 使用场景

### IR 结构分析
在分析 Relax IR 的结构时，需要了解函数中定义的所有符号变量，以便理解计算图的动态形状特性。

### 变量依赖分析
通过获取定义的符号变量，可以分析变量之间的依赖关系，为后续的优化传递提供信息。

### 内存使用分析
符号变量直接影响张量的内存分配，该函数帮助确定动态形状下所需的内存大小。

### 优化决策支持
在编译优化阶段，了解定义的符号变量有助于做出更准确的内联、融合等优化决策。

### 编译时检查
在编译时验证符号变量的使用是否合理，避免运行时错误。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.script import relax as R
from tvm.relax.analysis import defined_symbolic_vars

# 创建一个包含符号变量的 Relax 函数
@R.function
def example_func(x: R.Tensor(["n", "m"], "float32")) -> R.Tensor(["n", "m"], "float32"):
    n = T.int64()
    m = T.int64()
    y = R.add(x, x)
    return y

# 获取函数中定义的符号变量
func = example_func
symbolic_vars = defined_symbolic_vars(func)

print("定义的符号变量:")
for var in symbolic_vars:
    print(f"  - {var.name}: {var}")

# 输出:
# 定义的符号变量:
#   - n: n
#   - m: m
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import defined_symbolic_vars, free_symbolic_vars

# 结合其他分析函数进行完整的符号变量分析
@R.function  
def complex_func(x: R.Tensor(["batch", "seq_len"], "float32")):
    batch = T.int64()
    seq_len = T.int64()
    hidden = T.int64()
    
    # 一些计算操作
    weight = R.ones((hidden, seq_len), "float32")
    output = R.matmul(x, weight)
    return output

func = complex_func

# 获取所有定义的符号变量
defined_vars = defined_symbolic_vars(func)
print("定义的符号变量:", [var.name for var in defined_vars])

# 结合其他分析函数
from tvm.relax.analysis import bound_symbolic_vars
bound_vars = bound_symbolic_vars(func)
print("绑定的符号变量:", [var.name for var in bound_vars])

# 输出:
# 定义的符号变量: ['batch', 'seq_len', 'hidden']
# 绑定的符号变量: ['batch', 'seq_len']
```

## 实现细节

`defined_symbolic_vars` 函数通过调用底层的 C++ 实现 (`_ffi_api.DefinedSymbolicVars`) 来执行实际的符号变量提取。其核心算法包括：

1. **IR 遍历**：深度优先遍历 Relax 函数的 IR 结构
2. **变量收集**：识别所有 `PrimFunc` 中通过 `T.int64()` 等形式定义的符号变量
3. **去重处理**：基于变量的唯一标识符进行去重
4. **类型验证**：确保收集的变量都是有效的 TIR 变量类型

该实现能够正确处理嵌套函数、控制流等复杂 IR 结构中的符号变量定义。

## 相关函数

- [`bound_symbolic_vars`](./bound_symbolic_vars.md) - 获取函数中绑定的符号变量
- [`free_symbolic_vars`](./free_symbolic_vars.md) - 获取函数中自由的符号变量
- [`defined_vars`](./defined_vars.md) - 获取函数中定义的所有变量（包括非符号变量）

## 注意事项

### 性能考虑
- 该函数需要对整个 IR 进行遍历，对于非常大的计算图可能会有性能开销
- 建议在需要时调用，避免在性能关键路径中频繁使用

### 使用限制
- 只能分析完整的 Relax Function 对象，不能用于部分 IR 片段
- 返回的符号变量列表不包含隐式定义的变量

### 常见错误
- 如果传入的不是有效的 Function 对象，会抛出类型错误
- 在 IR 结构不完整的情况下调用可能导致意外结果

### 最佳实践
- 在形状推导阶段之前调用此函数
- 结合其他符号变量分析函数以获得完整的信息
- 对返回结果进行空值检查，处理无符号变量的情况