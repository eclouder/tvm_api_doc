---
title: AnnotateTIROpPattern
description: TVM Relax 转换 Pass，用于为 TIR PrimFunc 中的操作添加模式注解。
---

# AnnotateTIROpPattern

## 概述

`AnnotateTIROpPattern` 是一个 TVM Relax 转换 Pass，主要功能是为 TIR (TensorIR) PrimFunc 中的操作添加模式注解。这些模式注解用于标识计算操作的类型和特性，为后续的图优化、算子融合和代码生成提供必要的元信息。

该 Pass 通常在 TIR 级别优化流程的早期阶段使用，为后续的优化 Pass 提供操作模式的分类信息。

## 函数签名

```cpp
Pass AnnotateTIROpPattern()
```

**返回值：**
- `Pass`：一个 TVM Pass 对象，可以应用于 IRModule 或 PrimFunc

## 参数说明

该 Pass 本身不接受参数，但在内部实现中会处理以下参数：

- `f` (`tir::PrimFunc`)：需要被注解的 TIR 原函数
- `m` (`IRModule`)：包含该函数的 IR 模块
- `ctx` (`PassContext`)：Pass 执行的上下文信息

## 实现原理

`AnnotateTIROpPattern` 的核心实现基于以下逻辑：

1. **Pass 创建**：使用 `tir::transform::CreatePrimFuncPass` 创建一个 PrimFunc 级别的 Pass
2. **函数转换**：对每个 TIR PrimFunc 应用 `AnnotateOpPattern` 函数
3. **模式识别**：在 `AnnotateOpPattern` 内部，Pass 会：
   - 遍历 TIR 函数中的计算操作
   - 根据操作的特征识别其模式类型
   - 为操作添加相应的模式注解属性

常见的模式注解包括：
- `kElemwise`：逐元素操作
- `kBroadcast`：广播操作  
- `kInjective`：单射操作
- `kCommReduce`：通信归约操作
- `kOutEWiseFusable`：可外部融合的逐元素操作

## 优化效果

应用此 Pass 后带来的主要优化效果：

1. **模式识别**：为后续优化 Pass 提供操作模式的标准化分类
2. **融合优化**：帮助算子融合 Pass 识别可融合的操作模式
3. **代码生成**：为代码生成器提供操作特性信息，优化内核生成
4. **调度优化**：基于模式信息选择更合适的调度策略

## 使用场景

`AnnotateTIROpPattern` 适用于以下场景：

- **TIR 优化流水线**：在 TIR 级别优化流程的早期阶段使用
- **算子融合准备**：在应用融合优化 Pass 之前
- **自定义算子**：为自定义 TIR 算子添加标准化的模式注解
- **性能调优**：需要基于操作模式进行针对性优化的场景

## 示例代码

```python
import tvm
from tvm import tir
from tvm.ir.transform import PassContext

# 创建一个简单的 TIR 函数
def create_primfunc():
    n = tir.Var("n", "int32")
    A = tir.decl_buffer((n,), "float32", name="A")
    B = tir.decl_buffer((n,), "float32", name="B")
    
    def prim_func(A: T.Buffer[(n,), "float32"], B: T.Buffer[(n,), "float32"]):
        for i in range(n):
            B[i] = A[i] * 2.0
    
    return prim_func

# 应用 AnnotateTIROpPattern Pass
with PassContext(opt_level=3):
    # 获取 Pass
    annotate_pass = tvm.get_global_func("relax.transform.AnnotateTIROpPattern")()
    
    # 创建 IRModule 并应用 Pass
    mod = tvm.IRModule.from_expr(create_primfunc())
    optimized_mod = annotate_pass(mod)
```

## 相关 Pass

- **FuseOps**：基于模式注解进行算子融合
- **AnnotateTIROpPattern**：类似的注解 Pass，可能用于不同级别的 IR
- **CanonicalizeBindings**：规范化绑定，为模式注解准备
- **FuseTIR**：TIR 级别的融合优化，依赖模式注解
- **LegalizeOps**：算子合法化，可能使用模式信息

该 Pass 通常与其他 TIR 优化 Pass 组合使用，形成完整的优化流水线。