---
title: CallTIRRewrite
description: TVM Relax 模块级变换 Pass，用于重写和优化 CallTIR 操作符调用。
---

# CallTIRRewrite

## 概述

`CallTIRRewrite` 是 TVM Relax 中的一个模块级变换 Pass，主要功能是对 Relax 模块中的 `CallTIR` 操作符调用进行重写和优化。该 Pass 通过遍历和修改 Relax IR 模块中的函数定义，将特定的 `CallTIR` 调用模式转换为更高效或更规范的表示形式，从而提高后续编译和优化的效果。

## 函数签名

```cpp
Pass CallTIRRewrite()
```

**返回值：**
- `Pass`：返回一个 TVM 模块级 Pass 对象，可在 Pass 流水线中执行。

## 参数说明

该 Pass 不接受任何显式参数，所有必要的上下文信息通过 `PassContext` 在内部管理。

## 实现原理

`CallTIRRewrite` Pass 的核心实现基于 `CallTIRMutator` 类，采用访问者模式遍历和修改 IR 模块：

1. **模块遍历**：Pass 接收一个 `IRModule` 作为输入，对模块中的所有函数进行遍历。

2. **函数重写**：对于每个函数，`CallTIRMutator` 会重写其中的 `CallTIR` 操作符调用：
   - 识别特定的 `CallTIR` 调用模式
   - 根据预定义的规则进行模式匹配和转换
   - 生成优化后的新表达式

3. **不变性保证**：Pass 确保在变换过程中保持 IR 的语义不变性，只改变表达式的表示形式而不影响计算语义。

4. **模块更新**：重写完成后，返回更新后的 IR 模块。

## 优化效果

执行 `CallTIRRewrite` Pass 可以带来以下优化效果：

- **表达式规范化**：将复杂的 `CallTIR` 调用转换为更简洁、规范的表示形式
- **编译优化**：为后续的优化 Pass 提供更好的 IR 基础，便于进行进一步的优化
- **性能提升**：通过消除冗余和简化表达式，可能带来运行时性能的提升
- **代码可读性**：生成更清晰、易于理解的 IR 表示

## 使用场景

`CallTIRRewrite` Pass 适用于以下场景：

1. **TVM 编译流水线**：作为 Relax 优化流水线的一部分，在前期进行表达式规范化
2. **模型导入后处理**：在从其他框架导入模型后，用于标准化 `CallTIR` 调用
3. **手动 IR 构建优化**：当手动构建 Relax IR 时，用于优化和规范化 `CallTIR` 操作
4. **调试和分析**：在调试 IR 变换时，用于观察 `CallTIR` 调用的规范化过程

## 示例代码

以下是在 TVM 中使用 `CallTIRRewrite` Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 构建一个包含 CallTIR 调用的 Relax 模块
mod = tvm.IRModule({
    "main": relax.Function(
        params=[x],
        body=relax.CallTIR("my_tir_func", [x], relax.TensorStructInfo(x.shape, x.dtype)),
        ret_struct_info=relax.TensorStructInfo(x.shape, x.dtype)
    )
})

# 创建并应用 CallTIRRewrite Pass
pass_obj = transform.CallTIRRewrite()
optimized_mod = pass_obj(mod)

# 查看优化后的模块
print(optimized_mod.script())
```

## 相关 Pass

- **LegalizeOps**：将高级操作符合法化为底层 TIR 实现
- **FuseOps**：操作符融合优化 Pass
- **FoldConstant**：常量折叠优化
- **CanonicalizeBindings**：规范化绑定表达式
- **EliminateCommonSubexpr**：消除公共子表达式

这些 Pass 通常与 `CallTIRRewrite` 结合使用，构成完整的 Relax 优化流水线。