---
title: AttachGlobalSymbol
description: TVM Relax 模块级 Pass，用于为模块中的函数附加全局符号属性。
---

# AttachGlobalSymbol

## 概述

`AttachGlobalSymbol` 是一个 TVM Relax 的模块级转换 Pass，主要功能是为 IRModule 中的函数附加全局符号（Global Symbol）属性。该 Pass 确保模块中的每个函数都有一个合适的全局符号名称，这对于后续的代码生成和链接过程至关重要。

## 函数签名

```cpp
Pass AttachGlobalSymbol()
```

**返回值：**
- `Pass`：一个 TVM 模块级 Pass 对象

## 参数说明

该 Pass 不接受任何参数，是一个无参的工厂函数。

## 实现原理

`AttachGlobalSymbol` Pass 的核心实现逻辑如下：

1. **获取系统库前缀**：从模块属性中获取系统库前缀（如果存在），用于 TIR PrimFunc 的命名。

2. **遍历模块函数**：遍历 IRModule 中的所有全局函数（GlobalVar 到 BaseFunc 的映射）。

3. **函数类型判断与处理**：
   - **TIR PrimFunc**：为 PrimFunc 附加全局符号属性，名称为 `系统库前缀 + 全局变量名`
   - **Relax Function**：为 Relax 函数附加全局符号属性，名称为 `全局变量名`

4. **属性更新条件**：
   - 当函数原本没有全局符号属性时
   - 或者原有的全局符号属性与新的名称不同时

5. **全局变量重命名**：如果新的全局符号名称与原来的全局变量名不同，会创建新的 GlobalVar 并更新引用。

6. **模块更新**：使用批量更新机制来应用所有的函数属性修改和全局变量替换。

## 优化效果

该 Pass 的主要优化效果包括：

- **符号一致性**：确保所有函数都有正确的全局符号名称，避免链接时的符号冲突
- **代码生成准备**：为后续的代码生成阶段提供必要的符号信息
- **系统库集成**：通过系统库前缀支持，便于将生成的代码集成到系统库中

## 使用场景

`AttachGlobalSymbol` Pass 在以下场景中特别有用：

1. **编译流程早期**：在 Relax 模块的编译流程早期阶段使用，为后续的优化和代码生成做准备

2. **混合函数类型**：当模块中同时包含 Relax 函数和 TIR PrimFunc 时

3. **系统库构建**：当需要将生成的代码构建为系统库时，确保符号命名的正确性

4. **跨模块链接**：在多个模块需要链接在一起时，确保符号的唯一性和正确性

## 示例代码

```python
import tvm
from tvm import relax
from tvm.relax.transform import AttachGlobalSymbol

# 创建示例 Relax 模块
@tvm.script.ir_module
class MyModule:
    @relax.function
    def main(x: relax.Tensor((32, 32), "float32")) -> relax.Tensor((32, 32), "float32"):
        return x

    @T.prim_func
    def tir_func(A: T.Buffer((32, 32), "float32"), B: T.Buffer((32, 32), "float32")):
        T.func_attr({"global_symbol": "old_name"})
        for i, j in T.grid(32, 32):
            with T.block("compute"):
                vi, vj = T.axis.remap("SS", [i, j])
                B[vi, vj] = A[vi, vj] + 1.0

# 应用 AttachGlobalSymbol Pass
mod = MyModule
mod_with_symbols = AttachGlobalSymbol()(mod)

# 检查结果
print(mod_with_symbols)
```

应用 Pass 后，模块中的函数将具有正确的全局符号属性：
- `main` 函数：全局符号为 "main"
- `tir_func` 函数：全局符号为系统库前缀 + "tir_func"

## 相关 Pass

- **`LambdaLift`**：将局部函数提升为全局函数，通常在此 Pass 之前运行
- **`ToNonDF`**：将数据流图转换为非数据流形式，可能影响函数的结构
- **`LegalizeOps`**：操作符合法化，可能改变函数的实现
- **`FuseOps`**：操作符融合，可能影响函数的边界和符号需求

这些 Pass 通常在编译流程中按特定顺序执行，`AttachGlobalSymbol` 通常在符号确定后的阶段执行。