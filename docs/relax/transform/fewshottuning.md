---
title: FewShotTuning
description: TVM Relax 的 FewShotTuning Pass 通过少量样本调优来优化未调度的 PrimFunc。
---

# FewShotTuning

## 概述

FewShotTuning Pass 是 TVM Relax 中的一个模块级变换 Pass，主要用于对未调度的 PrimFunc 进行少量样本调优。该 Pass 通过尝试有限次数的不同调度策略，从中选择性能最优的实现，特别适用于需要快速获得较好性能但不需要完全详尽搜索的场景。

## 函数签名

```cpp
Pass FewShotTuning(int valid_count, bool benchmark)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `valid_count` | `int` | 有效的调优试验次数，必须为正整数。该参数控制调优过程中尝试的不同调度策略数量。 |
| `benchmark` | `bool` | 是否进行基准测试。当设置为 `true` 时，会对调优结果进行性能基准测试，此时 `valid_count` 必须至少为 2。 |

**注意事项：**
- `valid_count` 必须大于 0
- 当 `benchmark` 为 `true` 时，`valid_count` 必须大于 1，以确保有足够的样本进行性能比较

## 实现原理

FewShotTuning Pass 的核心实现逻辑如下：

1. **输入验证**：首先检查 `valid_count` 参数的合法性，确保其为正整数，并在启用基准测试时确保有足够的试验次数。

2. **目标获取**：从当前的 PassContext 中获取目标设备信息，该信息将用于后续的调优过程。

3. **函数遍历与筛选**：遍历 IRModule 中的所有函数，仅对满足以下条件的 PrimFunc 进行处理：
   - 必须是 `tir::PrimFunc` 类型
   - 不能已经具有调度（即不具有 `tir::attr::kIsScheduled` 属性）

4. **少量样本调优**：对筛选出的 PrimFunc 调用 `FewShotTunePrimFunc` 函数进行调优，该函数会：
   - 生成 `valid_count` 个不同的调度变体
   - 根据 `benchmark` 参数决定是否进行性能测试
   - 选择性能最优的调度实现

5. **结果构建**：将调优后的函数与未处理的函数一起构建新的 IRModule，保持原有的源映射和属性。

## 优化效果

FewShotTuning Pass 的主要优化效果包括：

- **性能提升**：通过尝试多种调度策略并选择最优解，可以显著提高计算性能
- **编译时间优化**：相比完全自动调优，FewShotTuning 只尝试有限次数的调度，大大减少了编译时间
- **质量保证**：在启用基准测试的情况下，可以确保选择的调度在实际硬件上具有良好的性能

## 使用场景

FewShotTuning Pass 适用于以下场景：

1. **快速原型开发**：在开发初期需要快速获得相对优化的实现
2. **资源受限环境**：当计算资源有限，无法进行完全调优时
3. **中等性能需求**：对性能有一定要求，但不需要极致优化的场景
4. **批量处理**：需要对多个未调度的 PrimFunc 进行统一调优处理

**使用时机建议：**
- 在初始调度生成之后、详细优化之前使用
- 适用于对编译时间敏感但仍有性能要求的应用

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import FewShotTuning

# 创建 IRModule
mod = tvm.IRModule.from_expr(...)

# 应用 FewShotTuning Pass
# 尝试 5 种不同的调度策略，并进行基准测试
pass_obj = FewShotTuning(valid_count=5, benchmark=True)
optimized_mod = pass_obj(mod)

# 或者作为管道的一部分使用
with tvm.transform.PassContext(opt_level=3):
    seq = tvm.transform.Sequential([
        # ... 其他 Pass
        FewShotTuning(valid_count=3, benchmark=False),
        # ... 其他 Pass
    ])
    optimized_mod = seq(mod)
```

## 相关 Pass

- **AutoSchedule**：完全自动调度 Pass，进行更彻底的调度空间探索
- **MetaSchedule**：基于机器学习的自动调度框架
- **ScheduleBuilder**：手动调度构建相关的 Pass
- **FunctionPass**：函数级变换 Pass 的基类

**与其他 Pass 的关系：**
- FewShotTuning 通常位于调度生成 Pass 之后，详细优化 Pass 之前
- 可以作为 MetaSchedule 的轻量级替代方案，在编译时间和性能之间取得平衡