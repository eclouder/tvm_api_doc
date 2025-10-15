---
title: MetaScheduleTuneTIR
description: TVM Relax 转换 Pass，用于通过 MetaSchedule 自动调优 TIR PrimFunc。
---

# MetaScheduleTuneTIR

## 概述

`MetaScheduleTuneTIR` 是一个 TVM Relax 转换 Pass，专门用于对 TIR PrimFunc 进行自动性能调优。该 Pass 利用 TVM 的 MetaSchedule 框架，在指定的工作目录中搜索最优的算子实现方案，以提升计算性能。

主要功能：
- 自动调优 TIR PrimFunc 的性能实现
- 支持全局最大试验次数限制
- 生成调优记录供后续使用

## 函数签名

```cpp
Pass MetaScheduleTuneTIR(ffi::String work_dir, Integer max_trials_global)
```

## 参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `work_dir` | `ffi::String` | **必需**。调优过程中用于存储调优记录和日志的工作目录路径 |
| `max_trials_global` | `Integer` | **必需**。全局最大试验次数限制，控制调优过程的计算资源消耗 |

## 实现原理

### 核心逻辑

1. **目标设备获取**：通过 `Target::Current(false)` 获取当前编译目标设备信息
2. **调优器创建**：实例化 `MetaScheduleTuner`，配置目标设备、工作目录和试验次数限制
3. **PrimFunc 处理**：对每个 TIR PrimFunc 调用 `TuneTIR` 方法进行调优
4. **Pass 包装**：使用 `tir::transform::CreatePrimFuncPass` 创建可跟踪的转换 Pass

### 关键代码流程

```cpp
// 获取当前目标设备
Target target = Target::Current(false);

// 创建调优函数
auto pass_func = [=](tir::PrimFunc f, IRModule mod, PassContext ctx) {
    return MetaScheduleTuner(target, work_dir, max_trials_global, max_trials_global, std::nullopt)
        .TuneTIR(f, ctx);
};

// 创建并返回 PrimFunc Pass
return tir::transform::CreatePrimFuncPass(pass_func, 0, "MetaScheduleTuneTIR", {}, true);
```

## 优化效果

使用 `MetaScheduleTuneTIR` Pass 可以带来以下优化效果：

- **性能提升**：通过自动搜索最优的算子实现，显著提升计算性能
- **设备适配**：针对特定硬件目标生成优化的代码
- **资源利用**：在试验次数限制内平衡调优质量与时间成本

## 使用场景

### 适用场景

1. **性能关键应用**：对计算性能要求较高的深度学习模型推理
2. **新硬件适配**：在新硬件平台上部署模型时的性能优化
3. **算子优化**：针对特定算子的深度性能调优

### 使用时机

- 在模型编译流程的 TIR 优化阶段使用
- 在确定目标硬件设备后调用
- 在具有充足调优时间预算的情况下

## 示例代码

```python
import tvm
from tvm import meta_schedule as ms
from tvm.relax import transform

# 创建调优 Pass
tune_tir_pass = transform.MetaScheduleTuneTIR(
    work_dir="./tune_records",
    max_trials_global=1000
)

# 在优化流程中使用
seq = tvm.transform.Sequential([
    # ... 其他 Pass
    tune_tir_pass,
    # ... 其他 Pass
])

# 应用优化
optimized_mod = seq(mod)
```

## 相关 Pass

### 协同使用的 Pass

- **`MetaScheduleApplyDatabase`**：应用之前调优结果数据库
- **`LegalizeOps`**：算子合法化，为调优准备规范的算子形式
- **`FuseOps`**：算子融合，创建更大的调优单元

### 替代方案

- **手动调优**：通过 `meta_schedule.tune_tir` 手动调优特定函数
- **数据库复用**：使用 `MetaScheduleDatabase` 直接应用历史调优结果

### 注意事项

1. **调优时间**：该 Pass 可能显著增加编译时间，需合理设置 `max_trials_global`
2. **存储空间**：调优记录会占用磁盘空间，定期清理不必要的记录
3. **重现性**：相同的配置在不同环境下可能产生不同的调优结果