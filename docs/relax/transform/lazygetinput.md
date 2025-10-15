---
title: LazyGetInput
description: TVM Relax 的 LazyGetInput Pass 用于延迟获取函数输入参数，优化内存使用和计算效率。
---

# LazyGetInput

## 概述

LazyGetInput Pass 是 TVM Relax 中的一个函数级变换 Pass，主要用于实现**延迟获取输入参数**的优化。该 Pass 通过将函数的输入参数获取操作从编译时延迟到运行时，减少不必要的内存分配和数据拷贝，特别适用于处理大型模型参数时的性能优化场景。

## 函数签名

```cpp
Pass LazyGetInput()
```

**返回值：**
- `Pass`：返回一个 TVM Pass 对象，可在 Pass 流水线中执行。

## 参数说明

该 Pass 为无参工厂函数，返回的 Pass 对象在执行时会自动处理以下参数：

- `func` (`Function`)：需要变换的 Relax 函数
- `IRModule`：包含函数的 IR 模块
- `PassContext`：Pass 执行上下文

## 实现原理

LazyGetInput Pass 的核心实现逻辑如下：

1. **符号检查**：首先检查函数是否具有 `kGlobalSymbol` 属性，只有具有全局符号的函数才会被处理，确保只对入口函数进行变换。

2. **延迟输入变换**：对于符合条件的函数，调用 `WithLazyInputs` 函数进行实际变换：
   - 将输入参数的获取操作从编译时绑定延迟到运行时
   - 生成相应的延迟加载代码结构
   - 保持函数接口不变，但内部实现使用惰性求值

3. **Pass 配置**：使用 `CreateFunctionPass` 创建函数级 Pass，设置：
   - 优化级别为 0（基础优化）
   - Pass 名称为 "LazyGetInput"
   - 无前置依赖 Pass

## 优化效果

使用 LazyGetInput Pass 可带来以下优化效果：

- **内存优化**：避免在编译时预先分配大量参数内存，减少峰值内存使用
- **启动加速**：加快模型加载和初始化速度，特别适合大型模型
- **资源效率**：按需加载参数，避免不必要的资源占用
- **流水线优化**：与后续的优化 Pass 协同工作，提升整体编译效率

## 使用场景

该 Pass 主要适用于以下场景：

1. **大型模型部署**：当模型参数较大时，延迟加载可显著改善内存使用
2. **动态参数场景**：参数在运行时可能变化或需要动态加载的情况
3. **多设备部署**：在不同设备间共享参数时，延迟加载提供更好的灵活性
4. **内存受限环境**：在嵌入式设备或内存受限环境中优化资源使用

## 示例代码

```python
import tvm
from tvm import relax

# 创建 IRModule
mod = tvm.IRModule()

# 构建包含需要优化的函数的模块
# ... 模块构建代码 ...

# 应用 LazyGetInput Pass
seq = tvm.transform.Sequential([
    relax.transform.LazyGetInput(),
    # 其他优化 Pass...
])
optimized_mod = seq(mod)

# 或者单独使用
lazy_pass = relax.transform.LazyGetInput()
result_mod = lazy_pass(mod)
```

## 相关 Pass

- **`FoldConstant`**：常量折叠 Pass，可与 LazyGetInput 协同优化
- **`DeadCodeElimination`**：死代码消除，清理延迟加载后产生的冗余代码
- **`FuseOps`**：算子融合 Pass，在延迟加载基础上进行进一步的计算图优化
- **`ToMixedPrecision`**：混合精度变换，与延迟加载结合进行内存和精度优化

## 注意事项

- 该 Pass 主要针对具有全局符号的入口函数，内部函数通常不会被处理
- 延迟加载可能引入轻微的运行时代价，但在大多数场景下收益大于成本
- 建议在 Pass 流水线的早期阶段应用此 Pass，以便后续优化能够充分利用延迟加载的优势