---
title: InlinePrivateFunctions
description: TVM Relax 的内联私有函数优化 Pass，用于内联没有全局符号的私有函数以减少函数调用开销。
---

# InlinePrivateFunctions

## 概述

`InlinePrivateFunctions` 是一个 TVM Relax 的模块级变换 Pass，其主要功能是内联模块中的私有函数。私有函数指的是那些没有 `kGlobalSymbol` 属性的函数，即没有全局符号名称的函数。通过内联这些私有函数，可以减少函数调用的开销，提高程序运行效率。

该 Pass 会自动检测并排除递归函数，确保不会对递归函数进行内联，从而避免无限循环和代码膨胀问题。

## 函数签名

```cpp
Pass InlinePrivateFunctions()
```

**返回值：**
- `Pass`：一个 TVM 模块级 Pass 对象，可以应用于 IRModule。

## 参数说明

该 Pass 没有显式参数，它通过 TVM 的 Pass 上下文（PassContext）来获取执行配置信息。

## 实现原理

`InlinePrivateFunctions` Pass 的实现逻辑如下：

1. **识别私有函数**：遍历 IRModule 中的所有函数，检查哪些函数没有 `kGlobalSymbol` 属性，将这些函数标记为私有函数。

2. **检测递归函数**：使用 `DetectRecursion` 函数检测模块中的递归函数集合，并从待内联的私有函数列表中排除所有递归函数。

3. **函数内联**：对于非私有函数（即保留在模块中的函数），使用 `FunctionInlineFunctions` 函数将其中的私有函数调用进行内联替换。

4. **模块更新**：从模块中移除所有已被内联的私有函数定义，并更新那些被修改过的函数。

关键实现细节：
- 使用 `ffi::Map` 来存储需要被内联替换的私有函数
- 通过 `DetectRecursion` 确保递归函数不被内联
- 使用 `CopyOnWrite` 机制安全地更新模块

## 优化效果

应用此 Pass 后，可以带来以下优化效果：

- **减少函数调用开销**：消除私有函数的调用开销，包括参数传递、栈帧设置等
- **增加优化机会**：内联后的代码可以参与后续的优化 Pass，如常量折叠、死代码消除等
- **降低运行时开销**：减少函数调用次数，提高缓存局部性

## 使用场景

`InlinePrivateFunctions` Pass 适用于以下场景：

1. **优化私有辅助函数**：当模块中包含多个小的私有辅助函数时，内联可以显著提升性能

2. **预处理阶段**：通常在函数特化、常量传播等优化之前应用，为后续优化创造更多机会

3. **代码生成前**：在生成目标代码之前应用，减少最终代码中的函数调用

**使用时机建议：**
```python
# 在优化序列中的典型位置
seq = tvm.transform.Sequential([
    # ... 其他优化 Pass
    relax.transform.InlinePrivateFunctions(),
    relax.transform.FoldConstant(),
    relax.transform.DeadCodeElimination(),
    # ... 更多优化 Pass
])
```

## 示例代码

以下是一个使用 `InlinePrivateFunctions` Pass 的示例：

```python
import tvm
from tvm import relax
import tvm.script

# 定义一个包含私有函数的 Relax 模块
@tvm.script.ir_module
class MyModule:
    @relax.function
    def main(x: relax.Tensor((32, 32), "float32")) -> relax.Tensor((32, 32), "float32"):
        # 调用私有函数
        return MyModule.private_helper(x)
    
    @relax.function
    def private_helper(y: relax.Tensor((32, 32), "float32")) -> relax.Tensor((32, 32), "float32"):
        # 私有函数实现（没有 kGlobalSymbol 属性）
        return relax.op.add(y, y)

# 应用 InlinePrivateFunctions Pass
mod = MyModule
print("应用 Pass 前的模块：")
print(mod)

pass_obj = relax.transform.InlinePrivateFunctions()
mod_optimized = pass_obj(mod)

print("\n应用 Pass 后的模块：")
print(mod_optimized)
```

在这个示例中，`private_helper` 函数是一个私有函数，应用 Pass 后会被内联到 `main` 函数中，从而消除函数调用。

## 相关 Pass

- **`InlineFunctions`**：更通用的函数内联 Pass，可以内联指定的函数
- **`FoldConstant`**：常量折叠 Pass，在内联后可以进一步优化常量表达式
- **`DeadCodeElimination`**：死代码消除 Pass，可以移除内联后不再使用的函数定义
- **`FuseOps`**：算子融合 Pass，在内联后可能有更多的融合机会

这些 Pass 通常组合使用，形成一个完整的优化流水线。