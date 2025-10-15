---
title: UpdateParamStructInfo
description: TVM Relax 模块级变换 Pass，用于更新函数参数的 StructInfo 信息。
---

# UpdateParamStructInfo

## 概述

`UpdateParamStructInfo` 是一个 TVM Relax 模块级变换 Pass，其主要功能是根据用户提供的回调函数，更新模块中所有函数的参数结构信息（StructInfo）。该 Pass 允许动态地修改函数参数的 StructInfo，从而支持在编译过程中对参数类型信息进行细粒度的调整和优化。

## 函数签名

```cpp
Pass UpdateParamStructInfo(ffi::TypedFunction<ffi::Optional<StructInfo>(Var)> sinfo_func)
```

## 参数说明

| 参数 | 类型 | 描述 |
|------|------|------|
| `sinfo_func` | `ffi::TypedFunction<ffi::Optional<StructInfo>(Var)>` | 用户提供的回调函数，接受一个 `Var`（变量）作为输入，返回一个可选的 `StructInfo`。如果返回非空值，则使用该值更新对应参数的 StructInfo；如果返回空值，则保持原 StructInfo 不变。 |

## 实现原理

该 Pass 的核心实现逻辑如下：

1. **参数结构信息变异器**：创建 `ParamStructInfoMutator` 对象，使用用户提供的 `sinfo_func` 回调函数来处理函数参数。

2. **模块遍历**：遍历 IRModule 中的所有函数：
   - 对每个函数应用变异器，更新其参数的 StructInfo
   - 如果函数发生了改变（即更新后的函数与原始函数不同），则记录需要替换的函数

3. **模块更新**：
   - 移除需要被替换的原始函数 GlobalVar
   - 添加更新后的函数及其对应的新 GlobalVar
   - 更新新 GlobalVar 的 StructInfo 信息

4. **变更应用**：只有当确实有函数需要更新时，才执行实际的模块修改操作，避免不必要的拷贝。

## 优化效果

- **类型信息精确化**：通过更新参数的 StructInfo，可以提供更准确的类型信息，有助于后续的优化 Pass 做出更好的决策
- **内存布局优化**：更精确的 StructInfo 可以帮助优化内存分配和访问模式
- **编译时验证**：增强的类型信息可以在编译时捕获更多错误，提高代码的可靠性

## 使用场景

该 Pass 在以下场景中特别有用：

1. **参数类型推断**：当需要根据上下文信息推断或修正函数参数的类型时
2. **动态形状处理**：在处理动态形状的模型中，需要根据运行时信息调整参数形状时
3. **类型特化**：在特定硬件后端上，需要对参数类型进行特化优化时
4. **跨模块类型协调**：在多个模块间协调参数类型信息时

## 示例代码

```python
import tvm
from tvm import relax
from tvm.script import relax as R

# 定义回调函数，更新参数的 StructInfo
def update_param_sinfo(var):
    # 根据变量名或其他特征决定如何更新 StructInfo
    if var.name_hint == "input_tensor":
        # 将参数更新为特定的 TensorStructInfo
        return relax.TensorStructInfo(
            shape=[1, 3, 224, 224], 
            dtype="float32"
        )
    return None  # 返回 None 表示不更新该参数

# 创建 Pass
pass_obj = relax.transform.UpdateParamStructInfo(update_param_sinfo)

# 应用 Pass 到模块
updated_mod = pass_obj(original_mod)
```

## 相关 Pass

- **`Normalize`**：规范化 Relax 函数，包括类型推断和规范化
- **`FoldConstant`**：常量折叠优化
- **`DeadCodeElimination`**：死代码消除
- **`CanonicalizeBindings`**：规范化绑定表达式

这些 Pass 通常与 `UpdateParamStructInfo` 结合使用，构成完整的 Relax 优化流水线。