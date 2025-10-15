---
title: RemoveUnusedParameters
description: TVM Relax 中用于移除未使用函数参数的优化 Pass
---

# RemoveUnusedParameters

## 概述

`RemoveUnusedParameters` 是 TVM Relax 中的一个变换 Pass，主要功能是识别并移除函数中未被使用的参数。该 Pass 通过静态分析函数体，检测哪些参数在函数执行过程中从未被引用，然后生成新的函数版本，这些新版本只包含实际被使用的参数。

## 函数签名

```cpp
Pass RemoveUnusedParameters()
```

该函数不接受任何参数，返回一个 TVM Pass 对象。

## 参数说明

此 Pass 函数本身没有参数，但在内部执行时会处理以下数据：

- `IRModule mod`：输入的 IR 模块，包含需要优化的函数
- `PassContext pc`：Pass 执行上下文，提供配置选项和环境信息

## 实现原理

### 核心算法

1. **函数分析阶段**：
   - 遍历模块中的所有函数
   - 对每个函数调用 `AnalyzeCallee` 进行分析，识别未使用的参数
   - 生成新的函数定义，只保留被实际使用的参数

2. **调用站点更新**：
   - 为每个被修改的函数创建调用站点更新器
   - 更新器负责将旧函数的调用转换为新函数的调用，并调整参数列表

3. **模块更新**：
   - 首先移除所有需要修改的旧函数定义
   - 然后添加优化后的新函数定义，避免命名冲突
   - 使用 `CallSiteMutator` 更新所有调用站点

### 关键数据结构

```cpp
PMap<GlobalVar, std::function<Call(Call)>> callsite_updaters;
```

这个映射表存储了从旧函数到新函数的转换规则，以及对应的参数更新逻辑。

## 优化效果

### 性能提升
- **减少内存分配**：移除未使用的参数可以减少函数调用时的内存分配
- **提升缓存效率**：更小的参数列表可以提高数据局部性
- **降低传输开销**：在分布式计算中减少参数传输量

### 代码精简
- 生成更简洁的中间表示
- 减少后续优化 Pass 的处理复杂度

## 使用场景

### 适用情况
1. **模型剪枝后**：当模型经过剪枝优化后，某些参数可能变得不再使用
2. **死代码消除后**：死代码消除可能使得某些参数变得冗余
3. **函数特化**：当函数被特化到特定上下文时，部分参数可能不再需要

### 使用时机
建议在以下 Pass 之后使用：
- 死代码消除（Dead Code Elimination）
- 操作符融合（Operator Fusion）
- 模型剪枝相关 Pass

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建包含未使用参数的 Relax 函数
@relax.function
def example_func(x, y, z):
    # 参数 z 未被使用
    return relax.op.add(x, y)

# 构建 IRModule
mod = tvm.IRModule({"example": example_func})

# 应用 RemoveUnusedParameters Pass
seq = tvm.transform.Sequential([
    transform.RemoveUnusedParameters()
])
optimized_mod = seq(mod)

# 优化后的函数将只包含 x 和 y 两个参数
```

## 相关 Pass

### 协同工作 Pass
- **DeadCodeElimination**：死代码消除，可能产生更多未使用的参数
- **FuseOps**：操作符融合，可能改变函数调用图
- **LambdaLift**：lambda 提升，影响函数参数结构

### 依赖关系
- 通常在其他优化 Pass 之后执行
- 依赖于准确的函数调用图分析
- 可能影响后续的数据布局优化

## 注意事项

1. **结构信息更新**：Pass 会自动更新函数的 `struct_info` 以反映参数变化
2. **私有函数处理**：特别处理私有子程序，确保名称不冲突
3. **调用一致性**：确保所有调用站点都正确更新，保持程序语义不变
4. **错误检查**：包含完整性检查，确保更新器应用于正确的函数调用