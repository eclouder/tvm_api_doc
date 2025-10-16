---
title: estimate_memory_usage
description: TVM Relax Analysis - estimate_memory_usage 函数 API 文档
---

# estimate_memory_usage

## 概述

`estimate_memory_usage` 是 TVM Relax 分析模块中的一个内存分析函数，主要用于估算 Relax 函数在 IRModule 中的内存使用情况。该函数能够分析内存规划前后的内存分配需求，帮助开发者理解内存优化的效果。

主要功能包括：
- 统计所有 `alloc_tensor` 和 `alloc_storage` 操作的内存使用总量
- 区分常量大小和动态大小的张量分配
- 提供内存规划前后的内存使用对比
- 生成易于阅读的内存使用估算报告

该函数在 Relax IR 分析流程中位于内存优化阶段，主要用于评估内存规划算法的效果，为编译器的内存优化决策提供数据支持。

## 函数签名

```python
def estimate_memory_usage(mod: Union[IRModule, Function]) -> str
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| mod | Union[IRModule, Function] | 无 | 输入的 IRModule 或 Function 对象。如果输入是单个 Function，会自动包装为名为 "main" 的 IRModule |

## 返回值

**类型:** `str`

返回一个格式化的字符串，包含内存使用估算的详细信息。字符串内容包括：
- 内存规划前的常量大小内存分配数量和总大小（以 GB 为单位）
- 动态大小内存分配数量（如果存在）
- 内存规划后的内存分配数量和总大小
- 内存规划带来的内存减少比例

## 使用场景

### IR 结构分析
- 分析 Relax 函数中的内存分配模式
- 识别常量大小和动态大小的张量分配

### 内存使用分析  
- 评估内存规划算法的优化效果
- 比较不同内存分配策略的性能差异

### 优化决策支持
- 为编译器选择合适的内存规划策略提供依据
- 帮助开发者理解内存瓶颈所在

### 编译时检查
- 验证内存分配的正确性
- 检测潜在的内存使用问题

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import estimate_memory_usage

# 估算内存使用
memory_est = estimate_memory_usage(mod)
print("内存使用估算结果:")
print(memory_est)
```

### 高级用法

```python
import tvm
from tvm import relax
from tvm.relax.analysis import estimate_memory_usage
from tvm.relax.analysis.estimate_memory_usage import MemoryEstimator
import numpy as np

# 自定义内存估算器
class CustomMemoryEstimator(MemoryEstimator):
    def generate_est_string(self, func_name: str) -> str:
        # 自定义输出格式
        return f"自定义格式: {func_name} - 内存使用: {self.total_alloc_tensor_mem} 字节"

# 直接使用估算器
mod = tvm.IRModule.from_expr(some_relax_function)
estimator = CustomMemoryEstimator()
result = estimator.estimate(mod)
print(result)
```

## 实现细节

### 算法原理
函数通过访问者模式遍历 Relax IR，识别三种关键操作：
- `relax.builtin.alloc_tensor`: 内存规划前的张量分配
- `relax.memory.alloc_tensor`: 内存规划后的张量分配  
- `relax.memory.alloc_storage`: 内存规划后的存储分配

### 内存计算
对于每个张量分配，计算其内存大小的公式为：
```
size = (product of shape dimensions) * ((dtype.bits + 7) // 8) * dtype.lanes
```

### 统计分类
- **常量大小张量**: 形状在编译时完全确定
- **动态大小张量**: 形状包含运行时确定的维度

## 相关函数

- [`relax.transform.MemoryPlan`](../transform/memory_plan.md) - 内存规划转换过程
- [`relax.analysis.detect_recursion`](./detect_recursion.md) - 递归检测分析
- [`relax.analysis.udchain`](./udchain.md) - 使用定义链分析

## 注意事项

### 性能考虑
- 该函数会遍历整个 IRModule，对于大型模型可能会有性能开销
- 建议在开发调试阶段使用，生产环境中谨慎使用

### 使用限制
- 估算结果可能偏高，因为静态分析不考虑控制流（如 if 语句和跨函数调用）
- 只统计显式的 `alloc_tensor` 和 `alloc_storage` 操作
- 动态形状的张量无法精确计算大小，只统计数量

### 常见错误
- 输入非 Relax Function 时可能产生意外结果
- 形状表达式不是 `ShapeExpr` 类型时会抛出 `TypeError`

### 最佳实践
- 在应用内存规划转换前后分别调用此函数，对比优化效果
- 结合其他分析函数（如 `udchain`）获得更全面的内存使用视图
- 对于动态形状模型，关注动态分配数量而非具体大小