---
title: BundleModelParams
description: TVM Relax 中用于将模型参数打包成元组的变换 Pass。
---

# BundleModelParams

## 概述

`BundleModelParams` 是一个 TVM Relax 模块级别的变换 Pass，主要功能是将模型参数（权重和偏置等）从函数的参数列表中提取出来，并打包成一个单独的元组参数。这种参数打包机制能够简化模型部署时的参数管理，特别是在需要将模型和参数序列化到磁盘或在不同运行时环境间传输时。

该 Pass 通过重构函数签名，将分散的多个参数合并为一个结构化的元组，从而提升模型的可移植性和部署效率。

## 函数签名

```cpp
Pass BundleModelParams(ffi::Optional<ffi::String> param_tuple_name)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `param_tuple_name` | `ffi::Optional<ffi::String>` | 可选参数，指定生成的参数元组的名称。如果未提供，将使用默认名称。 |

## 实现原理

`BundleModelParams` Pass 的核心实现基于一个 IRModule 级别的变换：

1. **遍历模块中的函数**：Pass 会遍历输入 IRModule 中的所有函数，识别出 Relax 函数（`relax::Function` 类型）。

2. **参数打包处理**：对于每个 Relax 函数，使用 `ModelParamBundler` 变换器进行处理。该变换器会：
   - 识别函数中的所有模型参数（通常是通过特定属性标记的参数）
   - 将这些参数从原始参数列表中移除
   - 创建一个包含所有模型参数的元组
   - 将元组作为新的单一参数添加到函数参数列表中

3. **增量更新**：只有当函数确实被修改时，才会将新函数添加到更新集合中，避免不必要的 IR 修改。

4. **模块更新**：如果存在函数更新，通过 `CopyOnWrite` 机制安全地更新原始模块。

## 优化效果

使用 `BundleModelParams` Pass 可以带来以下优化效果：

- **简化接口**：将多个参数合并为单一元组，简化了函数的调用接口
- **提升序列化效率**：模型参数被打包后，序列化和反序列化操作更加高效
- **减少内存碎片**：参数在内存中连续存储，有助于提升缓存局部性
- **便于参数管理**：在模型部署和传输过程中，参数可以作为单一实体进行管理

## 使用场景

`BundleModelParams` Pass 在以下场景中特别有用：

- **模型导出**：当需要将模型导出到磁盘或传输到其他系统时
- **边缘部署**：在资源受限的边缘设备上部署模型时
- **参数加密**：需要对模型参数进行整体加密或压缩时
- **AOT编译**：在 Ahead-of-Time 编译场景下，需要固定模型参数时

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 构建一个包含模型参数的 Relax 函数
@relax.function
def model_func(input_data, weight1, bias1, weight2, bias2):
    # 模型计算逻辑
    return output

# 创建 IRModule
mod = tvm.IRModule({"main": model_func})

# 应用 BundleModelParams Pass
pass_obj = transform.BundleModelParams("model_params")
mod_optimized = pass_obj(mod)

# 优化后的函数将只有一个输入数据参数和一个参数元组
# 函数签名变为：func(%input_data, %model_params)
```

## 相关 Pass

- **`ToNonDataflow`**：将数据流图转换为非数据流形式，常与参数打包配合使用
- **`StaticPlanBlockMemory`**：静态内存规划 Pass，在参数打包后可以更有效地进行内存分配
- **`FuseOps`**：算子融合 Pass，可以在参数打包优化后进行进一步的图优化