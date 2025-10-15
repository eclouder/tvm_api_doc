---
title: RemovePurityChecking
description: TVM Relax 中用于移除纯度检查的函数级转换 Pass
---

# RemovePurityChecking

## 概述

`RemovePurityChecking` 是一个函数级别的转换 Pass，主要功能是移除 Relax 函数中的纯度检查逻辑。纯度检查是函数式编程中的一个重要概念，用于确保函数没有副作用。在 TVM Relax 的编译过程中，某些阶段可能需要移除这些检查来优化性能或简化后续处理。

该 Pass 通过调用底层的 `relax::RemovePurityChecking` 函数来实现，专门处理 Relax 函数的纯度相关注解和检查代码。

## 函数签名

```cpp
Pass RemovePurityChecking()
```

**返回值：**
- `Pass`：返回一个 TVM 转换 Pass 对象，可以在 Pass 流水线中使用

## 参数说明

该 Pass 构造函数不接受任何显式参数。在 Pass 执行时，内部会接收以下参数：

- `const Function& f`：要处理的 Relax 函数
- `IRModule mod`：包含该函数的 IR 模块
- `PassContext pc`：Pass 执行上下文，包含配置选项等信息

## 实现原理

`RemovePurityChecking` Pass 的核心实现基于以下逻辑：

1. **Pass 创建**：使用 `CreateFunctionPass` 创建一个函数级别的 Pass
2. **遍历处理**：对 IR 模块中的每个函数应用转换逻辑
3. **纯度检查移除**：调用 `relax::RemovePurityChecking(f)` 函数来处理具体的纯度检查移除工作
4. **零开销**：Pass 的优化级别设置为 0，表示这是一个基础转换 Pass

```cpp
auto pass_func = [=](const Function& f, IRModule mod, PassContext pc) {
  return relax::RemovePurityChecking(f);
};
return CreateFunctionPass(pass_func, 0, "RemovePurityChecking", {});
```

## 优化效果

该 Pass 主要带来以下优化效果：

1. **代码简化**：移除纯度检查相关的代码，减少 IR 的复杂度
2. **性能提升**：消除运行时纯度检查的开销
3. **内存优化**：减少生成的代码体积
4. **编译加速**：简化后续 Pass 的处理逻辑

## 使用场景

`RemovePurityChecking` Pass 适用于以下场景：

1. **性能优化阶段**：在需要最大化运行时性能时使用
2. **部署准备**：在生成最终部署代码前移除调试和检查代码
3. **后端代码生成**：在针对特定硬件后端生成代码时简化 IR
4. **测试和调试**：在需要分析不含纯度检查的代码行为时使用

## 示例代码

以下是在 TVM Pass 流水线中使用 `RemovePurityChecking` 的示例：

```python
import tvm
from tvm import relax

# 创建 IR 模块
mod = tvm.IRModule()

# 构建 Pass 流水线
seq = relax.transform.Sequential([
    # ... 其他 Pass
    relax.transform.RemovePurityChecking(),
    # ... 其他 Pass
])

# 应用转换
mod_optimized = seq(mod)
```

## 相关 Pass

- **`CanonicalizeBindings`**：规范化绑定，常与纯度检查移除配合使用
- **`EliminateCommonSubexpr`**：消除公共子表达式，在简化代码后效果更佳
- **`FuseOps`**：算子融合，纯度检查移除后可以更安全地进行融合优化
- **`DeadCodeElimination`**：死代码消除，可以清理被移除纯度检查后的无用代码

这些 Pass 通常在优化流水线中按特定顺序组合使用，以达到最佳的优化效果。