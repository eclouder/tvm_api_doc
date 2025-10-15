---
title: LambdaLift
description: TVM Relax 模块级别的 Lambda 函数提升转换 Pass
---

# LambdaLift

## 概述

LambdaLift Pass 是一个 TVM Relax 的模块级别转换 Pass，主要功能是将模块中的 Lambda 表达式（匿名函数）提升为模块级别的命名函数。该 Pass 通过识别和提取 Lambda 表达式，将其转换为独立的全局函数定义，从而简化 IR 结构，为后续的优化和代码生成提供更好的基础。

在函数式编程风格的 Relax 代码中，Lambda 表达式经常被用作高阶函数的参数或局部函数定义。LambdaLift Pass 通过将这些匿名函数提升到模块级别，使得函数边界更加清晰，便于后续的优化 Pass 进行处理。

## 函数签名

```cpp
Pass LambdaLift()
```

**返回值：**
- `tvm.transform.Pass`：一个 TVM 模块级别的转换 Pass

**创建方式：**
```cpp
auto pass_func = [=](IRModule mod, PassContext pc) {
    return relax::LambdaLifter(mod).Lift();
};
return tvm::transform::CreateModulePass(pass_func, 1, "LambdaLift", {});
```

## 参数说明

该 Pass 是一个无参数的工厂函数，返回一个配置好的模块转换 Pass。在 Pass 执行时，会自动接收以下参数：

- `IRModule mod`：输入的 Relax IR 模块
- `PassContext pc`：Pass 执行的上下文信息

## 实现原理

LambdaLift Pass 的核心实现基于 `relax::LambdaLifter` 类，其主要工作原理如下：

### 1. Lambda 表达式识别
Pass 会遍历模块中的所有函数定义，识别其中的 Lambda 表达式节点。Lambda 表达式在 Relax IR 中通常表现为包含函数参数和函数体的匿名函数结构。

### 2. 函数提取与重命名
对于每个识别到的 Lambda 表达式：
- 生成一个唯一的全局函数名称
- 将 Lambda 表达式转换为独立的全局函数定义
- 在原始位置将 Lambda 表达式替换为对新生成函数的引用

### 3. 闭包处理
如果 Lambda 表达式捕获了外部变量（形成闭包），Pass 会：
- 分析捕获的变量集合
- 将这些变量作为显式参数添加到新生成的函数中
- 在调用站点传递相应的参数值

### 4. 递归处理
Pass 会递归地处理新生成的函数，确保其中可能包含的嵌套 Lambda 表达式也被正确提升。

## 优化效果

LambdaLift Pass 主要带来以下优化效果：

### 代码结构优化
- **函数边界清晰化**：将内联的 Lambda 表达式转换为模块级别的命名函数，使得函数边界更加明确
- **IR 简化**：减少嵌套的函数定义，简化 IR 结构

### 后续优化支持
- **函数级别优化**：提升后的函数可以独立参与函数级别的优化，如内联、常量传播等
- **代码生成改进**：命名函数更易于目标后端的代码生成和调试

### 调试和分析
- **更好的可读性**：命名函数比匿名 Lambda 表达式更易于理解和调试
- **性能分析**：独立的函数定义便于性能分析和优化

## 使用场景

LambdaLift Pass 在以下场景中特别有用：

### 1. 函数式编程模式
当 Relax 代码大量使用高阶函数和 Lambda 表达式时，如：
```python
# 使用 map、filter 等高阶函数
result = R.map(lambda x: x + 1, input_list)
```

### 2. 复杂的数据处理管道
在构建复杂的数据转换管道时，Lambda 表达式常用于定义转换逻辑。

### 3. 模型转换后期
在模型从其他框架转换到 Relax 后，通常包含大量的 Lambda 表达式，需要将其规范化。

### 4. 代码生成前准备
在代码生成阶段之前，将所有的 Lambda 表达式提升为命名函数，便于目标后端处理。

## 示例代码

### 转换前
```python
@R.function
def main(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 内联的 Lambda 表达式
    add_func = lambda y: R.add(y, R.const(1.0, "float32"))
    result = R.map(add_func, x)
    return result
```

### 转换后
```python
# 生成的 Lambda 提升函数
@R.function
def lifted_lambda_0(y: R.Tensor((64,), "float32")) -> R.Tensor((64,), "float32"):
    return R.add(y, R.const(1.0, "float32"))

@R.function  
def main(x: R.Tensor((32, 64), "float32")) -> R.Tensor((32, 64), "float32"):
    # 替换为对命名函数的引用
    result = R.map(lifted_lambda_0, x)
    return result
```

### 使用方式
```python
import tvm
from tvm import relax

# 创建 LambdaLift Pass
lambda_lift_pass = relax.transform.LambdaLift()

# 应用 Pass 到模块
mod_transformed = lambda_lift_pass(mod_original)
```

## 相关 Pass

### 协同工作的 Pass
- **`relax.transform.ToNonDataflow()`**：将数据流块转换为普通代码，可能包含需要提升的 Lambda 表达式
- **`relax.transform.CallTIRRewrite()`**：TIR 调用重写，可能处理包含 Lambda 的函数调用
- **`relax.transform.StaticPlanBlockMemory()`**：静态内存规划，在函数边界清晰化后更有效

### 后续优化 Pass
- **`relax.transform.FunctionInline()`**：函数内联，可以处理提升后的命名函数
- **`relax.transform.DeadCodeElimination()`**：死代码消除，可能移除未使用的提升函数
- **`relax.transform.FoldConstant()`**：常量折叠，在函数边界清晰后更有效

### 替代或补充 Pass
- **`relax.transform.LambdaLift`** 是处理 Lambda 表达式的主要 Pass，在 TVM Relax 优化流程中通常位于中间转换阶段。