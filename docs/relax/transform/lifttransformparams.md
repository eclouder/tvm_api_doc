---
title: LiftTransformParams
description: TVM Relax 模块级 Pass，用于将模型参数转换逻辑从端到端函数中分离并提升为独立函数。
---

# LiftTransformParams

## 概述

`LiftTransformParams` 是一个 TVM Relax 模块级 Pass，主要功能是将模型参数转换逻辑从端到端函数中分离出来。该 Pass 通过三个步骤实现参数转换逻辑的提取和优化：

1. **参数分区**：将每个函数划分为编译时和运行时两部分
2. **函数提升**：将编译时和运行时的 lambda 函数从端到端函数中提取出来
3. **后处理**：暴露编译时和运行时函数供外部使用，替换原有的端到端函数

该 Pass 特别适用于需要将参数预处理、量化、剪枝等转换操作与模型推理分离的场景。

## 函数签名

```cpp
Pass LiftTransformParams(ffi::Variant<Bool, ffi::Array<ffi::String>> shared_transform)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `shared_transform` | `ffi::Variant<Bool, ffi::Array<ffi::String>>` | 控制参数转换共享行为的配置：<br>- 如果为 `Bool` 类型：表示是否对所有函数启用共享转换<br>- 如果为 `ffi::Array<ffi::String>` 类型：指定需要共享转换的函数名称列表 |

## 实现原理

### 三阶段处理流程

#### 1. PartitionTransformParams 阶段
- 分析每个函数中的参数使用模式
- 将函数逻辑划分为编译时部分和运行时部分
- 编译时部分负责参数转换和预处理
- 运行时部分负责模型推理

#### 2. LambdaLift 阶段
- 将编译时和运行时的 lambda 函数从原函数中提取出来
- 创建独立的全局函数
- 保持函数间的调用关系

#### 3. 后处理阶段
```cpp
auto post_proc_func = [=](IRModule mod, PassContext pc) {
    std::unordered_map<GlobalVar, Function> to_add;
    for (const auto& [gvar, base_func] : mod->functions) {
        if (auto opt = base_func.as<Function>()) {
            auto func = opt.value();
            std::string func_name = gvar->name_hint;
            if (ends_with(func_name, "transform_params")) {
                // 设置全局符号属性
                func = WithAttr(func, tvm::attr::kGlobalSymbol, gvar->name_hint);
                // 可选：消费捆绑参数
                if (pc->GetConfig<Bool>(kLiftTransformConsumeParams).value_or(Bool(false))) {
                    func = Downcast<Function>(ConsumeBundledParams()(func));
                }
                to_add[gvar] = func;
            }
        }
    }
    // 将处理后的函数添加回模块
    if (to_add.size()) {
        auto write_ptr = mod.CopyOnWrite();
        for (const auto& [gvar, func] : to_add) {
            write_ptr->Add(gvar, func);
        }
    }
    return mod;
};
```

## 优化效果

### 主要优势

1. **编译时优化**：将参数转换逻辑提前到编译时执行，减少运行时开销
2. **内存优化**：分离的参数转换函数可以独立优化内存使用
3. **代码清晰**：分离关注点，使端到端函数专注于推理逻辑
4. **可重用性**：提取的参数转换函数可以在多个模型间共享

### 性能提升

- 减少运行时参数处理时间
- 降低内存峰值使用量
- 提高缓存局部性

## 使用场景

### 适用场景

1. **模型量化**：将量化参数转换从推理流程中分离
2. **参数预处理**：如权重归一化、格式转换等操作
3. **动态剪枝**：运行时参数剪枝逻辑的提取
4. **多设备部署**：不同设备需要不同参数格式的场景

### 使用时机

建议在以下阶段使用该 Pass：

- 模型优化流水线的中后期
- 在算子融合和内存优化之后
- 在代码生成之前

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import LiftTransformParams

# 创建 IRModule
mod = tvm.IRModule.from_expr(...)

# 使用 LiftTransformParams Pass
# 方式1：对所有函数启用共享转换
pass_with_shared = LiftTransformParams(True)

# 方式2：对特定函数启用共享转换
pass_with_specific = LiftTransformParams(["model_main", "model_inference"])

# 应用 Pass
mod_optimized = pass_with_shared(mod)
```

## 相关 Pass

### 协同工作的 Pass

1. **PartitionTransformParams**
   - 功能：划分编译时和运行时函数逻辑
   - 关系：LiftTransformParams 的第一阶段

2. **LambdaLift**
   - 功能：提升 lambda 函数为全局函数
   - 关系：LiftTransformParams 的第二阶段

3. **ConsumeBundledParams**
   - 功能：处理捆绑参数消费
   - 关系：在后处理阶段可选使用

### 配套优化 Pass

- `FuseOps`：算子融合，建议在 LiftTransformParams 之前使用
- `DeadCodeElimination`：死代码消除，可在之后使用以清理无用代码
- `MemoryPlan`：内存规划，优化提取函数的内存使用

## 注意事项

1. **函数命名约定**：该 Pass 会识别以 "transform_params" 结尾的函数名
2. **配置选项**：可通过 `kLiftTransformConsumeParams` 配置启用参数消费优化
3. **模块完整性**：应用 Pass 后需要确保所有提取的函数都能正确链接
4. **调试支持**：建议在开发阶段保留原始函数以便调试