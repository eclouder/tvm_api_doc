---
title: NormalizeGlobalVar
description: TVM Relax 模块级别的 Pass，用于规范化全局变量定义。
---

# NormalizeGlobalVar

## 概述

`NormalizeGlobalVar` 是一个 TVM Relax 模块级别的变换 Pass，主要功能是规范化 IRModule 中的全局变量定义。该 Pass 通过重命名和重新组织全局变量，确保模块中的符号定义符合 TVM 的内部规范要求，为后续的优化和代码生成阶段提供标准化的输入。

## 函数签名

```cpp
Pass NormalizeGlobalVar()
```

**返回值**: `Pass` - 返回一个模块级别的 Pass 对象

## 参数说明

该 Pass 不接受任何显式参数，它通过 TVM 的 Pass 机制自动处理 IRModule。

## 实现原理

`NormalizeGlobalVar` Pass 的核心实现逻辑如下：

1. **Pass 创建**: 使用 `CreateModulePass` 创建一个模块级别的 Pass
2. **Lambda 函数**: 定义一个 lambda 函数作为 Pass 的主要执行逻辑
3. **全局变量规范化**: 调用 `GlobalVarNormalizer::Normalize(mod)` 方法对模块中的所有全局变量进行规范化处理
4. **零优化级别**: 设置优化级别为 0，表示这是一个基础规范化 Pass
5. **无前置依赖**: 该 Pass 不依赖于其他前置 Pass

```cpp
Pass NormalizeGlobalVar() {
  auto pass_func = [=](IRModule mod, PassContext pc) {
    return GlobalVarNormalizer::Normalize(mod);
  };
  return CreateModulePass(/*pass_function=*/pass_func,
                          /*opt_level=*/0,
                          /*pass_name=*/"NormalizeGlobalVar",
                          /*required=*/{});
}
```

## 优化效果

该 Pass 主要带来以下优化效果：

- **标准化符号表**: 确保全局变量名称符合 TVM 的内部命名规范
- **消除命名冲突**: 解决潜在的全局变量命名冲突问题
- **提高可读性**: 使生成的 IR 更加规范和易于理解
- **为后续优化铺路**: 为依赖规范符号表的后续优化 Pass 提供基础

## 使用场景

`NormalizeGlobalVar` Pass 适用于以下场景：

1. **模块导入后**: 在从外部格式（如 ONNX、TorchScript）导入模型后立即应用
2. **Pass 流水线早期**: 作为优化流水线的早期阶段，确保后续 Pass 能够正确处理全局变量
3. **符号表重构**: 当需要重新组织模块的符号表结构时
4. **调试和分析**: 在调试 IR 时，规范化后的变量名更易于跟踪和分析

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建一个包含全局变量的 IRModule
mod = tvm.IRModule({
    "main": relax.Function([], relax.Call(relax.ExternFunc("external_func"), [])),
    "func1": relax.Function([], relax.const(1, "int32"))
})

# 应用 NormalizeGlobalVar Pass
seq = transform.Sequential([
    transform.NormalizeGlobalVar()
])
mod_normalized = seq(mod)

# 规范化后的模块将具有标准化的全局变量定义
print(mod_normalized)
```

## 相关 Pass

- **`LegalizeOps`**: 合法化操作符，依赖规范的全局变量
- **`FuseOps`**: 操作符融合，需要清晰的符号表结构
- **`ToNonDataflow`**: 转换到非数据流形式，受益于规范的变量命名
- **`CanonicalizeBindings`**: 规范化绑定，与全局变量规范化协同工作

该 Pass 通常作为 TVM Relax 优化流水线的基础组成部分，确保整个优化过程中符号表的一致性和规范性。