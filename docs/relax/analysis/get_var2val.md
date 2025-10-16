---
title: get_var2val
description: TVM Relax Analysis - get_var2val 函数 API 文档
---

# get_var2val

## 概述

`get_var2val` 是 TVM Relax 分析模块中的一个核心函数，主要用于提取 Relax 函数中变量到其绑定表达式的映射关系。该函数在 Relax IR 的结构分析中扮演着重要角色，能够帮助开发者理解函数内部变量的定义和使用情况。

**主要功能：**
- 遍历 Relax 函数的绑定序列，收集所有变量与其对应表达式的映射
- 提供变量定义点的完整视图，便于后续的依赖分析和优化决策
- 作为其他高级分析（如活性分析、依赖分析）的基础工具

**在分析流程中的位置：**
该函数通常位于 Relax IR 分析流程的前期阶段，为后续的优化和转换提供必要的变量定义信息。

## 函数签名

```python
def get_var2val(func: Function) -> Dict[Var, Expr]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| func | Function | 无 | 需要分析的 Relax 函数。必须是有效的 Relax Function 对象，包含完整的绑定序列和变量定义。 |

## 返回值

**类型:** `Dict[Var, Expr]`

返回一个字典，其中：
- **键 (Key):** `Var` 类型的变量对象，表示函数中定义的变量
- **值 (Value):** `Expr` 类型的表达式对象，表示该变量绑定的具体表达式

字典包含了函数中所有显式绑定的变量及其对应的表达式，但不包括函数参数。

## 使用场景

### IR 结构分析
- 分析函数的变量定义结构
- 理解变量之间的依赖关系

### 变量依赖分析
- 作为构建变量使用-定义链的基础
- 支持数据流分析和控制流分析

### 优化决策支持
- 为常量折叠、死代码消除等优化提供变量定义信息
- 辅助内存布局优化决策

### 编译时检查
- 验证变量定义的完整性
- 检测未定义变量或重复定义

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import get_var2val
from tvm.script import relax as R

# 定义一个简单的 Relax 函数
@R.function
def simple_function(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 定义几个变量绑定
    y = R.add(x, x)
    z = R.multiply(y, R.const(2.0, "float32"))
    w = R.subtract(z, x)
    return w

# 获取变量到表达式的映射
var2val = get_var2val(simple_function)

# 打印映射结果
for var, expr in var2val.items():
    print(f"Variable: {var.name_hint}")
    print(f"Expression type: {type(expr).__name__}")
    print("---")
```

### 高级用法

```python
# 结合其他分析函数进行综合变量分析
from tvm.relax.analysis import used_vars, undefined_vars

def comprehensive_variable_analysis(func):
    """综合变量分析函数"""
    # 获取变量定义映射
    var2val = get_var2val(func)
    
    # 分析使用的变量
    used = used_vars(func)
    
    # 分析未定义的变量
    undefined = undefined_vars(func)
    
    analysis_result = {
        'definitions': var2val,
        'used_variables': used,
        'undefined_variables': undefined,
        'definition_count': len(var2val)
    }
    
    return analysis_result

# 执行综合分析
analysis = comprehensive_variable_analysis(simple_function)
print(f"函数中共定义了 {analysis['definition_count']} 个变量")
```

## 实现细节

`get_var2val` 函数通过调用底层的 C++ 实现 (`_ffi_api.get_var2val`) 来高效地遍历 Relax 函数的绑定序列。其核心算法包括：

1. **遍历绑定序列：** 按顺序处理函数中的所有绑定语句
2. **变量收集：** 对于每个 `BindingBlock`，提取其中的变量定义
3. **映射构建：** 将变量与其对应的表达式建立映射关系
4. **结果返回：** 返回完整的变量-表达式字典

该实现确保了线性时间复杂度 O(n)，其中 n 是函数中绑定的数量。

## 相关函数

- [`used_vars`](./used_vars.md) - 分析函数中使用的所有变量
- [`undefined_vars`](./undefined_vars.md) - 找出函数中未定义的变量
- [`dead_code_elimination`](./dead_code_elimination.md) - 基于变量使用信息进行死代码消除

## 注意事项

### 性能考虑
- 对于大型函数，该操作的时间复杂度与绑定数量成正比
- 建议在需要时调用，避免在性能关键路径中重复调用

### 使用限制
- 仅适用于完整的 Relax Function 对象
- 不处理函数参数，只关注函数体内的变量绑定
- 返回的映射不包含变量作用域信息

### 常见错误
- 如果传入的不是有效的 Function 对象，会抛出类型错误
- 对于空函数，返回空字典而不是 None

### 最佳实践
- 在进行分析前确保函数已经过规范化处理
- 结合其他分析函数以获得更全面的变量使用情况
- 在处理结果时注意变量的生命周期和作用域