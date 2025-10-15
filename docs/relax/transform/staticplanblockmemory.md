---
title: StaticPlanBlockMemory
description: TVM Relax 的静态内存规划 Pass，用于优化计算图的内存分配
---

# StaticPlanBlockMemory

## 概述

`StaticPlanBlockMemory` 是 TVM Relax 中的一个模块级变换 Pass，主要用于对计算图进行静态内存规划。该 Pass 通过分析计算图中的数据依赖关系，为每个计算块（Block）预先分配和复用内存空间，从而减少动态内存分配的开销，提升模型推理性能。

该 Pass 特别适用于需要高效内存管理的场景，如移动端部署、嵌入式设备等资源受限环境。

## 函数签名

```cpp
Pass StaticPlanBlockMemory() {
  auto pass_func = [=](IRModule m, PassContext pc) {
    return relax::StaticPlanBlockMemory(std::move(m));
  };
  return CreateModulePass(pass_func, /*opt_level=*/0, "StaticPlanBlockMemory", {});
}
```

## 参数说明

| 参数 | 类型 | 描述 |
|------|------|------|
| m | IRModule | 输入的 Relax IR 模块，包含需要优化的计算图 |
| pc | PassContext | Pass 执行上下文，包含优化配置和选项 |

**返回值：**
- 返回一个 `Pass` 对象，该 Pass 会对输入的 IRModule 进行静态内存规划优化

## 实现原理

`StaticPlanBlockMemory` Pass 的核心实现逻辑包括以下几个步骤：

1. **计算图分析**：遍历 IRModule 中的所有函数，分析计算块之间的数据依赖关系
2. **生命周期分析**：确定每个张量（Tensor）的生命周期，识别可以共享内存的张量
3. **内存分配规划**：基于生命周期分析结果，为计算块预先分配内存空间
4. **内存复用优化**：在不同计算块之间复用内存空间，减少总体内存占用
5. **IR 重写**：根据内存规划结果，重写原始 IR，插入相应的内存分配和释放操作

该 Pass 采用静态分析的方法，在编译时完成内存规划，避免了运行时的动态内存分配开销。

## 优化效果

使用 `StaticPlanBlockMemory` Pass 可以带来以下优化效果：

- **减少内存分配开销**：通过预分配和复用内存，减少运行时的内存分配/释放操作
- **降低内存峰值**：优化内存使用模式，降低模型运行时的峰值内存占用
- **提升执行效率**：减少内存管理开销，提升模型推理速度
- **改善缓存局部性**：通过合理的内存布局规划，改善数据访问的缓存局部性

## 使用场景

`StaticPlanBlockMemory` Pass 适用于以下场景：

1. **资源受限环境**：在内存有限的移动设备、嵌入式系统上部署模型
2. **性能关键应用**：对推理延迟有严格要求的实时应用
3. **批量推理**：需要同时处理多个输入的场景，需要高效的内存管理
4. **长期运行服务**：模型推理服务需要长时间稳定运行，避免内存碎片

**使用时机：**
- 通常在计算图优化阶段的中后期应用该 Pass
- 在算子融合、常量折叠等优化之后应用，以获得更准确的内存使用分析

## 示例代码

```python
import tvm
from tvm import relax

# 构建原始的 Relax IRModule
@relax.function
def main(x: relax.Tensor((1, 64, 56, 56), "float32")):
    # 一些计算操作
    weight = relax.const(..., "float32")
    conv1 = relax.op.nn.conv2d(x, weight)
    relu1 = relax.op.nn.relu(conv1)
    return relu1

mod = tvm.IRModule({"main": main})

# 应用 StaticPlanBlockMemory Pass
mod_optimized = relax.transform.StaticPlanBlockMemory()(mod)

# 查看优化后的 IR
print(mod_optimized)
```

## 相关 Pass

- **`FuseOps`**：算子融合 Pass，将多个小算子融合为更大的计算块，为内存规划提供更好的基础
- **`FoldConstant`**：常量折叠 Pass，减少不必要的内存分配
- **`DeadCodeElimination`**：死代码消除 Pass，移除无用的计算和内存分配
- **`MemoryPlanning`**：通用的内存规划 Pass，提供更基础的内存优化功能
- **`ToNonDataflow`**：将数据流图转换为非数据流格式，便于内存规划分析

这些 Pass 通常与 `StaticPlanBlockMemory` 配合使用，形成完整的内存优化流水线。