---
title: static_shape_tuning_pipeline
description: TVM Relax Pipeline - static_shape_tuning_pipeline 函数 API 文档
---

# static_shape_tuning_pipeline

## 概述

`static_shape_tuning_pipeline` 是 TVM Relax 模块中的一个静态形状模型调优流水线函数。该函数主要用于对静态形状的深度学习模型进行自动调优（AutoTVM/MetaSchedule），并将调优结果存储到数据库中，以优化模型在目标设备上的运行性能。

## 函数签名

```python
def static_shape_tuning_pipeline(
    total_trials: int, 
    target: Union[str, tvm.target.Target], 
    work_dir: str = 'tuning_logs', 
    cpu_weight_prepack: bool = False
)
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| total_trials | int | 无 | 运行的调优试验总次数。如果设为0，则跳过调优阶段 |
| target | Union[str, tvm.target.Target] | 无 | 模型调优的目标设备，可以是字符串或TVM Target对象 |
| work_dir | str | 'tuning_logs' | 存储调优日志文件的目录路径 |
| cpu_weight_prepack | bool | False | 是否启用CPU权重预打包功能，可提升CPU性能但会改变部署接口 |

## 返回值

**类型:** `tvm.transform.ModulePass`

返回一个TVM模块转换流水线，该流水线可以应用于IRModule以执行静态形状模型的调优和优化。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax import pipeline

# 创建模型并应用静态形状调优流水线
mod = tvm.IRModule()  # 你的模型IRModule

# 应用调优流水线
tuned_mod = pipeline.static_shape_tuning_pipeline(
    total_trials=1000,
    target="llvm -num-cores 4",
    work_dir="./tuning_logs",
    cpu_weight_prepack=False
)(mod)
```

### 启用CPU权重预打包功能

```python
import tvm
from tvm import relax
import numpy as np

# 启用CPU权重预打包
mod = relax.pipeline.static_shape_tuning_pipeline(
    total_trials=1000,
    target="llvm -num-cores 16",
    work_dir="tuning_logs",
    cpu_weight_prepack=True,
)(mod)

# 编译模型
ex = tvm.compile(mod, target=target)
vm = relax.VirtualMachine(ex, device=tvm.cpu())

# 使用变换后的参数进行推理
# 注意：函数名应为 f"{func_name}_transform_params"
params = vm["main_transform_params"](params["main"])

input_data = tvm.runtime.tensor(np.random.randn(1, 3, 224, 224).astype("float32"))
out = vm["main"](input_data, *params).numpy()
```

## 实现细节

该函数实现了一个完整的静态形状模型调优流水线，主要包括以下步骤：

1. **预处理阶段**：
   - 操作分解（`DecomposeOpsForInference`）
   - 绑定规范化（`CanonicalizeBindings`）
   - 零优化流水线（`zero_pipeline`）

2. **布局重写**（仅在启用CPU权重预打包时）：
   - 预调优：附加布局自由缓冲区属性
   - 后调优：布局重写预处理、参数变换提升、常量折叠

3. **调优阶段**：
   - 当`total_trials > 0`时，执行MetaSchedule调优
   - 应用调优数据库中的优化结果

4. **后处理阶段**：
   - 应用布局重写后处理（如果启用CPU权重预打包）

## 相关函数

- [`MetaScheduleTuneIRMod`](./metaschedule_tune_irmod.md) - MetaSchedule IR模块调优功能
- [`MetaScheduleApplyDatabase`](./metaschedule_apply_database.md) - 应用调优数据库结果
- [`LiftTransformParams`](./lift_transform_params.md) - 提升参数变换操作

## 注意事项

- **性能与兼容性权衡**：启用`cpu_weight_prepack`可以显著提升CPU性能，但会改变模型的部署接口，需要额外的参数变换步骤
- **调优次数选择**：`total_trials`设为0时跳过调优，适用于只想应用已有调优结果的场景
- **存储空间**：调优日志会占用磁盘空间，建议定期清理不需要的`work_dir`目录
- **目标设备匹配**：确保`target`参数与实际运行设备匹配，否则调优结果可能不适用

## 错误处理

- 如果`target`参数格式不正确，TVM会抛出`TVMError`异常
- 当`work_dir`目录无法创建或写入时，会抛出`IOError`异常
- 如果模型结构不支持某些优化pass，可能会在流水线执行过程中抛出转换错误
- 启用`cpu_weight_prepack`但未正确调用参数变换函数会导致运行时错误

---