---
title: computable_at_compile_time
description: TVM Relax Analysis - computable_at_compile_time 函数 API 文档
---

# computable_at_compile_time

## 概述

`computable_at_compile_time` 是 TVM Relax Analysis 模块中的一个重要分析函数，专门用于识别在编译时即可确定其值的变量。该函数的主要用途是分析 Relax 函数中哪些变量的值可以在编译阶段被计算出来，这对于优化编译过程和运行时性能至关重要。

在 Relax IR 分析流程中，该函数位于变量依赖分析和常量传播阶段，帮助编译器识别那些不依赖于运行时输入的可预先计算的表达式。通过分析函数的参数依赖关系，该函数能够构建变量之间的依赖图，并提取出仅依赖于编译时常量的变量绑定。

该函数与 `kNumInput` 属性紧密配合，当函数具有此属性时，前 `kNumInput` 个参数被视为运行时输入，而其余参数则可能在编译时已知。这种机制使得混合了编译时和运行时参数的函数能够被有效分析。

## 函数签名

```python
def computable_at_compile_time(func: Function) -> List[Var]
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| func | Function | 无 | 需要分析的 Relax 函数对象。必须是有效的 `relax.Function` 实例，包含完整的函数定义和绑定信息。 |

## 返回值

**类型:** `List[Var]`

返回一个变量列表，包含所有可以在编译时计算的变量。这些变量按照它们在函数中出现的顺序排列，保持了依赖关系的拓扑顺序。每个变量都是 `relax.Var` 类型的实例，可以通过 `name_hint` 属性获取变量名。

## 使用场景

### IR 结构分析
- 分析函数中变量的依赖关系图
- 识别编译时常量传播的路径

### 变量依赖分析  
- 构建变量之间的依赖链
- 确定哪些变量仅依赖于编译时已知的参数

### 优化决策支持
- 为常量折叠优化提供输入
- 支持编译时内存分配决策
- 辅助内联和函数特化优化

### 编译时检查
- 验证函数参数的使用是否符合预期
- 检测潜在的编译时计算错误

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import computable_at_compile_time
from tvm.script import relax as R

# 创建一个包含编译时参数的 Relax 函数
@R.function
def main(x: R.Tensor((32, 64), "float32"), 
         compile_time_param: R.Tensor((), "int32")) -> R.Tensor((32, 64), "float32"):
    # 标记前1个参数为运行时输入，其余为编译时参数
    R.func_attr({"kNumInput": 1})
    
    # 基于编译时参数的计算
    scale_factor = R.add(compile_time_param, R.const(1, "int32"))
    scaled_x = R.multiply(x, scale_factor)
    return scaled_x

# 获取函数并进行分析
mod = tvm.IRModule({"main": main})
main_func = mod["main"]
computable_vars = computable_at_compile_time(main_func)

print(f"编译时可计算变量 ({len(computable_vars)}): {[var.name_hint for var in computable_vars]}")
# 输出: 编译时可计算变量 (2): ['compile_time_param', 'scale_factor']
```

### 高级用法

```python
# 结合其他分析函数进行综合优化分析
from tvm.relax.analysis import used_vars, name_to_binding

def comprehensive_compile_time_analysis(func):
    """综合的编译时分析函数"""
    
    # 获取编译时可计算变量
    computable_vars = computable_at_compile_time(func)
    
    # 获取所有使用的变量
    all_used_vars = used_vars(func)
    
    # 构建变量名到绑定的映射
    var_bindings = name_to_binding(func)
    
    # 分析编译时变量的使用模式
    compile_time_usage = {}
    for var in computable_vars:
        if var.name_hint in var_bindings:
            binding = var_bindings[var.name_hint]
            compile_time_usage[var.name_hint] = {
                'type': type(binding).__name__,
                'computable': True
            }
    
    return {
        'computable_vars': computable_vars,
        'compile_time_usage': compile_time_usage,
        'total_computable': len(computable_vars)
    }

# 使用综合分析
analysis_result = comprehensive_compile_time_analysis(main_func)
print(f"可编译时计算的变量数量: {analysis_result['total_computable']}")
```

## 实现细节

该函数的实现基于以下算法原理：

1. **参数分析**: 首先检查函数是否具有 `kNumInput` 属性，如果有，则前 `kNumInput` 个参数被视为运行时输入，其余参数为潜在的编译时参数。

2. **依赖图构建**: 构建变量之间的依赖关系图，其中节点表示变量，边表示变量之间的依赖关系。

3. **可达性分析**: 从编译时参数出发，进行图遍历，标记所有可以直接或间接从编译时参数到达的变量。

4. **拓扑排序**: 将标记的变量按照它们在函数中出现的拓扑顺序进行排序，确保依赖关系得到保持。

该算法的时间复杂度为 O(V + E)，其中 V 是变量数量，E 是依赖关系边的数量。

## 相关函数

- [`used_vars`](./used_vars.md) - 分析函数中所有被使用的变量
- [`name_to_binding`](./name_to_binding.md) - 构建变量名到绑定的映射
- [`free_vars`](./free_vars.md) - 识别函数中的自由变量

## 注意事项

### 性能考虑
- 对于包含大量变量绑定的复杂函数，该分析可能消耗较多计算资源
- 建议在需要时调用，避免在性能关键路径中频繁使用

### 使用限制
- 函数必须具有完整的绑定信息
- 仅支持分析单函数，不直接支持跨函数分析
- 依赖于准确的 `kNumInput` 属性设置

### 常见错误
- 如果函数缺少必要的绑定信息，可能抛出分析异常
- 不正确的 `kNumInput` 值可能导致错误的编译时变量识别

### 最佳实践
- 在优化管道中尽早使用该分析，以便后续优化阶段可以利用编译时信息
- 结合其他分析函数使用，获得更全面的优化决策支持
- 验证分析结果是否与预期一致，特别是在处理复杂依赖关系时