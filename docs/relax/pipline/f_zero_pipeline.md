---
title: f_zero_pipeline
description: TVM Relax Pipeline - f_zero_pipeline 函数 API 文档
---

# f_zero_pipeline

## 概述

`f_zero_pipeline` 是 TVM Relax 编译流水线中的一个重要函数，专门用于应用预调优的日志（pre-tuned logs）来优化深度学习模型。该函数通过一系列预定义的转换过程，对输入的 IRModule 进行优化，并利用 MetaSchedule 数据库中的调优记录来进一步提升性能。

## 函数签名

```python
def f_zero_pipeline(mod: tvm.ir.IRModule, ctx: tvm.transform.PassContext) -> tvm.ir.IRModule
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| mod | tvm.ir.IRModule | 无 | 输入的中间表示模块，包含需要优化的计算图 |
| ctx | tvm.transform.PassContext | 无 | 转换过程的上下文，用于控制转换行为的配置 |

## 返回值

**类型:** `tvm.ir.IRModule`

返回经过优化转换后的 IRModule。该模块已经过算子合法化、常量折叠、算子融合等一系列优化步骤，如果 MetaSchedule 数据库可用，还会应用预调优的算子实现。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax import transform
import tvm.transform as transform

# 创建一个简单的 IRModule
@tvm.script.ir_module
class SimpleModule:
    @R.function
    def main(x: R.Tensor((32, 64), "float32"), y: R.Tensor((64, 128), "float32")) -> R.Tensor:
        with R.dataflow():
            z = R.matmul(x, y)
            R.output(z)
        return z

mod = SimpleModule

# 创建 PassContext
with transform.PassContext(opt_level=3):
    # 应用 f_zero_pipeline 优化
    optimized_mod = f_zero_pipeline(mod, transform.PassContext.current())
    
    # 检查优化结果
    print(optimized_mod)
```

### 启用 MetaSchedule 数据库

```python
import tvm
from tvm import meta_schedule as ms
from tvm.relax.pipeline import f_zero_pipeline

# 创建或加载 MetaSchedule 数据库
database = ms.database.MemoryDatabase()

# 设置当前数据库
with ms.Database.current(database):
    # 应用包含数据库优化的流水线
    optimized_mod = f_zero_pipeline(input_mod, pass_ctx)
```

## 实现细节

`f_zero_pipeline` 函数的实现包含以下关键步骤：

1. **转换序列构建**：创建一个顺序执行的转换序列，包含：
   - `LegalizeOps`：算子合法化，确保所有算子都能在目标后端执行
   - `AnnotateTIROpPattern`：为 TIR 算子标注计算模式
   - `FoldConstant`：常量折叠优化
   - `FuseOps`：算子融合，将多个小算子合并为更大的计算单元
   - `FuseTIR`：TIR 级别的算子融合

2. **转换执行**：将输入的 IRModule 通过转换序列进行处理

3. **数据库应用**：如果当前存在激活的 MetaSchedule 数据库，应用预调优的算子实现

## 相关函数

- [`LegalizeOps`](./legalize_ops.md) - 算子合法化转换
- [`FuseOps`](./fuse_ops.md) - 算子融合转换  
- [`MetaScheduleApplyDatabase`](./meta_schedule_apply_database.md) - 应用 MetaSchedule 数据库中的调优记录

## 注意事项

- 在使用此函数前，建议确保输入 IRModule 已经过基本的图级别优化
- `enable_warning` 参数在函数内部使用，控制是否显示警告信息
- MetaSchedule 数据库的应用是可选的，取决于当前是否有激活的数据库
- 该函数主要面向有预调优记录的模型优化场景

## 错误处理

- 如果输入的 IRModule 格式不正确，可能会在转换过程中抛出 `TVMError`
- 当应用数据库中的调优记录时，如果记录与当前算子不匹配，可能会产生警告或错误
- 建议在使用时通过 try-except 块捕获可能的异常：

```python
try:
    optimized_mod = f_zero_pipeline(mod, ctx)
except tvm.TVMError as e:
    print(f"优化过程中发生错误: {e}")
    # 处理错误情况
```