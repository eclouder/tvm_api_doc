---
title: MetaScheduleApplyDatabase
description: TVM Relax 转换 Pass，用于应用元调度数据库中的调优记录来优化计算图。
---

# MetaScheduleApplyDatabase

## 概述

`MetaScheduleApplyDatabase` 是 TVM Relax 框架中的一个转换 Pass，主要功能是从元调度（MetaSchedule）数据库中查询并应用预先调优的调度记录到计算图中的 PrimFunc 节点。该 Pass 能够自动利用历史调优结果，避免重复的调度优化过程，从而加速模型编译和优化。

## 函数签名

```cpp
Pass MetaScheduleApplyDatabase(ffi::Optional<ffi::String> work_dir, bool enable_warning = false)
```

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|---------|------|
| `work_dir` | `ffi::Optional<ffi::String>` | 无 | 工作目录路径，用于指定 JSON 数据库文件的存储位置。如果未提供，则使用当前已定义的数据库。 |
| `enable_warning` | `bool` | `false` | 是否启用警告信息。当设置为 `true` 时，会在创建 JSON 数据库时输出警告日志。 |

## 实现原理

该 Pass 的核心实现逻辑如下：

1. **数据库初始化**：
   - 如果当前已存在定义的数据库（通过 `Database::Current()`），则直接使用该数据库。
   - 否则，根据提供的 `work_dir` 参数创建 JSON 数据库，数据库文件包括工作负载文件（`database_workload.json`）和调优记录文件（`database_tuning_record.json`）。

2. **模块处理**：
   - 遍历输入 IRModule 中的所有函数，识别其中的 PrimFunc 节点。
   - 对每个 PrimFunc 进行规范化处理，转换为统一的 IRModule 格式。

3. **查询调优记录**：
   - 使用规范化后的模块、当前目标设备和函数名称作为键，在数据库中查询对应的调优记录。
   - 如果找到匹配的记录，则应用该记录中的调度方案到原始 PrimFunc。

4. **结构相等性检查**：
   - 使用忽略张量信息的模块相等性检查器（`ModuleEquality::Create("ignore-tensor")`）验证查询到的调优记录是否与当前模块结构匹配。
   - 当结构不匹配时，可能表明存在锚点块的变化，此时会输出相应的警告信息。

## 优化效果

- **编译加速**：通过复用历史调优结果，避免重复的自动调度过程，显著减少编译时间。
- **性能保持**：应用经过优化的调度方案，确保生成代码的性能与历史调优结果一致。
- **资源利用**：减少在相同或相似计算模式上的调度优化计算资源消耗。

## 使用场景

- **模型部署优化**：在部署已知模型时，利用预先调优的数据库快速生成高效代码。
- **批量编译**：当需要编译多个相似模型时，通过共享调优数据库提高整体编译效率。
- **持续集成**：在 CI/CD 流水线中，使用持久化的调优记录确保编译结果的一致性和性能。

## 示例代码

```python
import tvm
from tvm import meta_schedule as ms
from tvm.relax import transform

# 创建工作目录路径
work_dir = "./meta_schedule_db"

# 创建 MetaScheduleApplyDatabase Pass
apply_db_pass = transform.MetaScheduleApplyDatabase(work_dir, enable_warning=True)

# 应用 Pass 到 IRModule
mod_optimized = apply_db_pass(mod)
```

## 相关 Pass

- **MetaScheduleTuneIRMod**：用于对 IRModule 进行自动调优并生成调优记录的 Pass。
- **MetaScheduleTuneTIR**：专门针对 TIR 进行调优的 Pass。
- **MetaScheduleDatabase**：管理调优记录数据库的基础设施。

这些 Pass 共同构成了 TVM 元调度系统的重要组成部分，支持端到端的模型优化和部署流程。