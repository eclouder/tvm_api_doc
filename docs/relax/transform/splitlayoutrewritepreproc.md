---
title: SplitLayoutRewritePreproc
description: TVM Relax 的布局重写预处理 Pass，用于优化计算图布局转换。
---

# SplitLayoutRewritePreproc

## 概述

`SplitLayoutRewritePreproc` 是一个 TVM Relax 模块级别的转换 Pass，主要用于在布局重写优化之前对计算图进行预处理。该 Pass 通过识别和拆分特定的布局转换模式，为后续的布局优化 Pass 创造更好的优化条件，从而提高模型在目标硬件上的执行效率。

该 Pass 通常作为布局优化流水线的前置处理步骤，与后续的布局重写 Pass 配合使用，共同实现计算图布局的优化。

## 函数签名

```cpp
Pass SplitLayoutRewritePreproc()
```

**返回值：**
- `Pass`：返回一个 TVM 转换 Pass 对象，该 Pass 会对输入的 IRModule 进行布局重写预处理。

## 参数说明

该 Pass 函数不接受任何显式参数，它通过 TVM 的 Pass 机制自动接收和处理 IRModule。

在内部实现中，Pass 会接收以下隐式参数：
- `IRModule mod`：需要优化的 Relax IR 模块
- `PassContext pc`：Pass 执行的上下文信息，包含各种配置选项

## 实现原理

`SplitLayoutRewritePreproc` 的实现基于以下核心逻辑：

1. **模块转换**：通过 `relax::SplitLayoutRewritePreproc::Transform(mod)` 对输入模块进行转换处理
2. **模式识别**：识别计算图中适合进行布局拆分的操作模式，特别是涉及张量布局转换的操作
3. **操作拆分**：将复杂的布局转换操作拆分为多个简单的、可优化的子操作
4. **死代码消除**：在转换完成后自动执行 DeadCodeElimination Pass，清理转换过程中产生的不再使用的中间结果

该 Pass 的实现采用了 TVM 的标准模块 Pass 架构：
```cpp
auto pass_func = [](IRModule mod, PassContext pc) {
  return relax::SplitLayoutRewritePreproc::Transform(mod);
};
auto pass = CreateModulePass(pass_func, 0, "SplitLayoutRewritePreproc", {});
return tvm::transform::Sequential({pass, relax::transform::DeadCodeElimination()},
                                  "SplitLayoutRewritePreproc");
```

## 优化效果

使用 `SplitLayoutRewritePreproc` Pass 可以带来以下优化效果：

1. **布局转换优化**：通过预处理为后续的布局重写 Pass 提供更好的优化基础
2. **计算图简化**：将复杂的布局操作拆分为更简单的操作，便于后续优化
3. **内存访问优化**：改善张量在内存中的布局，提高缓存利用率和内存访问效率
4. **性能提升**：通过优化的布局转换，减少运行时开销，提升模型执行速度

## 使用场景

该 Pass 适用于以下场景：

1. **布局敏感模型**：对于卷积神经网络等对内存布局敏感的计算密集型模型
2. **硬件特定优化**：在针对特定硬件（如 GPU、NPU）进行优化时，需要调整张量布局
3. **优化流水线**：作为布局优化流水线的前置步骤，与其他布局相关的 Pass 配合使用
4. **性能调优**：当模型在目标硬件上出现内存访问瓶颈时，使用此 Pass 进行优化

## 示例代码

以下是在 TVM 编译流程中使用 `SplitLayoutRewritePreproc` Pass 的示例：

```python
import tvm
from tvm import relax

# 构建原始的 Relax IRModule
mod = build_original_module()

# 创建优化流水线
seq = tvm.transform.Sequential([
    # 其他预处理 Pass...
    relax.transform.SplitLayoutRewritePreproc(),
    # 其他布局优化 Pass...
    relax.transform.RewriteLayout(),
    # 后续优化 Pass...
])

# 应用优化
optimized_mod = seq(mod)
```

## 相关 Pass

- **RewriteLayout**：主要的布局重写 Pass，负责实际的布局转换优化
- **DeadCodeElimination**：死代码消除 Pass，用于清理优化过程中产生的无用代码
- **FuseOps**：操作融合 Pass，可能与布局优化协同工作
- **LegalizeOps**：操作合法化 Pass，确保操作在目标硬件上可执行

这些 Pass 通常组合使用，形成一个完整的优化流水线，共同提升模型性能。