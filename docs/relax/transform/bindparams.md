---
title: BindParams Pass
description: TVM Relax 模块级别的参数绑定 Pass，用于将常量参数绑定到指定函数的参数上。
---

# BindParams Pass

## 概述

`BindParams` Pass 是 TVM Relax 中的一个模块级别（ModulePass）变换，主要功能是将预定义的常量参数绑定到指定函数的参数上。通过将函数参数替换为具体的常量值，该 Pass 可以消除函数调用时的参数传递开销，并为后续的常量折叠和优化创造机会。

## 函数签名

```cpp
Pass BindParams(ffi::String func_name, ffi::Map<Any, ObjectRef> params)
```

## 参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `func_name` | `ffi::String` | 目标函数的名称，需要绑定参数的函数 |
| `params` | `ffi::Map<Any, ObjectRef>` | 参数映射表，键为参数名（Any 类型），值为对应的常量值（ObjectRef 类型） |

## 实现原理

`BindParams` Pass 的核心实现逻辑如下：

1. **Pass 创建**：使用 `CreateModulePass` 创建一个模块级别的 Pass
2. **Lambda 函数**：定义一个 lambda 函数作为 Pass 的主要执行逻辑
3. **参数绑定**：在 lambda 函数中调用 `BindParam` 函数，执行实际的参数绑定操作
4. **参数替换**：将目标函数中指定的参数替换为对应的常量值
5. **模块更新**：返回更新后的 IRModule，其中目标函数的参数已被常量替换

实现代码：
```cpp
Pass BindParams(ffi::String func_name, ffi::Map<Any, ObjectRef> params) {
  auto pass_func = [=](IRModule mod, PassContext pc) {
    return BindParam(std::move(mod), func_name, params);
  };
  return CreateModulePass(pass_func, 0, "BindParams", {});
}
```

## 优化效果

使用 `BindParams` Pass 可以带来以下优化效果：

- **减少运行时开销**：消除函数调用时的参数传递和解析开销
- **启用常量折叠**：为后续的常量折叠优化提供基础，编译器可以在编译时计算常量表达式
- **简化计算图**：减少计算图中的节点数量，提高执行效率
- **内存优化**：在某些情况下可以减少内存分配和拷贝操作

## 使用场景

`BindParams` Pass 适用于以下场景：

1. **模型部署**：在部署预训练模型时，将模型的权重参数绑定到计算图中
2. **常量传播**：当某些函数参数在编译时已知且为常量时
3. **图优化前置步骤**：作为其他优化 Pass（如常量折叠、死代码消除）的前置步骤
4. **专用硬件优化**：在针对特定硬件优化时，固定某些配置参数

## 示例代码

以下是一个使用 `BindParams` Pass 的示例：

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建一个简单的计算图
@relax.function
def main(x: relax.Tensor, weight: relax.Tensor, bias: relax.Tensor):
    return relax.op.add(relax.op.matmul(x, weight), bias)

# 创建预定义的权重和偏置参数
weight_np = np.random.rand(128, 64).astype(np.float32)
bias_np = np.random.rand(64).astype(np.float32)

weight = relax.const(weight_np)
bias = relax.const(bias_np)

# 创建参数映射
params = {
    "weight": weight,
    "bias": bias
}

# 应用 BindParams Pass
mod = tvm.IRModule({"main": main})
mod = transform.BindParams("main", params)(mod)

# 此时 main 函数只需要输入 x 参数，weight 和 bias 已被绑定为常量
```

## 相关 Pass

- **ConstantFolding**：常量折叠 Pass，利用 `BindParams` 绑定的常量进行表达式简化
- **DeadCodeElimination**：死代码消除 Pass，可以移除因参数绑定而不再使用的代码
- **FuseOps**：算子融合 Pass，可能在参数绑定后进行更有效的融合
- **LegalizeOps**：算子合法化 Pass，在参数绑定后可能产生新的优化机会

该 Pass 通常在优化流水线的早期阶段使用，为后续的优化 Pass 创造条件。