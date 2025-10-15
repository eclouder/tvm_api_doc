---
title: ExpandTupleArguments
description: TVM Relax 中用于展开元组参数的模块级转换 Pass。
---

# ExpandTupleArguments

## 概述

`ExpandTupleArguments` 是一个 TVM Relax 模块级转换 Pass，主要功能是将函数参数中的元组（Tuple）展开为多个独立的参数。该 Pass 通过消除函数签名中的元组结构，使得后续的优化和代码生成能够更直接地处理各个参数，从而提高编译效率和运行时性能。

## 函数签名

```cpp
Pass ExpandTupleArguments()
```

**返回值**：
- `Pass`：一个 TVM 模块级 Pass 对象，可在 Pass 流水线中执行。

## 参数说明

该 Pass 没有显式参数，它作为一个无状态的转换 Pass 运行，通过 TVM 的 PassContext 来管理执行上下文。

## 实现原理

`ExpandTupleArguments` Pass 的实现分为两个主要阶段：

### 1. 参数展开阶段

```cpp
for (const auto& [gvar, base_func] : mod->functions) {
    if (auto func = base_func.as<Function>()) {
        if (auto opt = ExpandParams(func.value())) {
            // 创建新的函数和全局变量
            auto new_func = opt.value();
            GlobalVar new_gvar(gvar->name_hint);
            new_gvar->struct_info_ = new_func->struct_info_;
            gvar_replacements[gvar] = new_gvar;
            new_callees[new_gvar] = new_func;
        }
    }
}
```

- 遍历模块中的所有函数
- 对每个函数调用 `ExpandParams` 来展开参数中的元组
- 如果展开成功，创建新的函数和对应的全局变量
- 记录全局变量的替换映射关系

### 2. 调用站点更新阶段

```cpp
TupleExpander mutator(std::move(gvar_replacements));

for (const auto& [gvar, base_func] : mod->functions) {
    if (auto func = base_func.as<Function>()) {
        auto mutated = Downcast<Function>(mutator.VisitExpr(func.value()));
        if (!mutated.same_as(base_func)) {
            caller_updates->Add(gvar, mutated);
        }
    }
}
```

- 使用 `TupleExpander` 访问器遍历所有函数调用站点
- 根据第一阶段建立的替换映射，更新所有对已修改函数的调用
- 确保调用站点的参数与新的函数签名匹配

## 优化效果

该 Pass 带来的主要优化效果包括：

1. **简化函数签名**：消除元组包装，使函数接口更加直接
2. **提升优化效果**：后续的优化 Pass 可以更精确地分析单个参数
3. **改善代码生成**：目标后端代码生成器可以更高效地处理展开后的参数
4. **减少运行时开销**：避免元组的构造和解构操作

## 使用场景

`ExpandTupleArguments` Pass 适用于以下场景：

- **模型导入后处理**：从其他框架导入的模型可能包含元组参数
- **算子融合优化**：融合后的算子可能需要调整参数结构
- **后端代码生成前**：为目标后端准备更友好的函数签名
- **性能调优**：当发现元组参数成为性能瓶颈时

## 示例代码

以下是在 TVM 中使用该 Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax.transform import ExpandTupleArguments

# 创建包含元组参数的 Relax 模块
@tvm.script.ir_module
class MyModule:
    @relax.function
    def main(x: relax.Tuple((relax.Tensor((32, 64), "float32"), 
                           relax.Tensor((32, 64), "float32")))) -> relax.Tensor((32, 64), "float32"):
        # 函数实现
        return x[0]

# 应用 ExpandTupleArguments Pass
mod = MyModule
mod_optimized = ExpandTupleArguments()(mod)

# 查看优化后的模块
print(mod_optimized.script())
```

优化后的函数签名将变为：
```python
@relax.function
def main(x_0: relax.Tensor((32, 64), "float32"), 
         x_1: relax.Tensor((32, 64), "float32")) -> relax.Tensor((32, 64), "float32"):
    return x_0
```

## 相关 Pass

- **`FoldConstant`**：常量折叠 Pass，可在参数展开后进行常量传播
- **`DeadCodeElimination`**：死代码消除，清理展开后可能产生的无用代码
- **`FuseOps`**：算子融合 Pass，可能受益于简化的参数结构
- **`LegalizeOps`**：算子合法化，处理展开后的参数类型
- **`ToNonDataflow`**：将数据流图转换为非数据流形式，可与参数展开协同工作

该 Pass 通常在优化流水线的早期阶段执行，为后续的优化 Pass 准备更清晰的中间表示。