---
title: zero_pipeline
description: TVM Relax Pipeline - zero_pipeline 函数 API 文档
---

# zero_pipeline

## 概述

`zero_pipeline` 是一个包装函数，用于创建和返回 TVM Relax 的零级优化流水线。该流水线包含一系列针对 Relax 模型的优化和转换过程，特别适用于应用预调优日志的场景。

## 函数签名

```python
def zero_pipeline(*, enable_warning: bool = False) -> tvm.transform.ModulePass
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| enable_warning | bool | False | 控制是否在特定情况下打印警告信息：<br>- 在 LegalizeOps pass 中，对于操作符（CallNode）的合法化函数未注册的情况<br>- 在 MetaScheduleApplyDatabase pass 中，对于数据库中不存在的 TIR 函数 |

## 返回值

**类型:** `tvm.transform.ModulePass`

返回一个 TVM 模块级别的 pass，该 pass 实现了完整的零级优化流水线，可以对输入的 IRModule 进行一系列优化转换。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 创建零级优化流水线
pipeline = relax.pipeline.zero_pipeline(enable_warning=True)

# 应用流水线到 IRModule
optimized_mod = pipeline(input_mod)
```

### 在完整编译流程中使用

```python
import tvm
from tvm import relax
from tvm.relax.testing import nn

# 构建示例模型
class SimpleModel(nn.Module):
    def __init__(self):
        self.linear = nn.Linear(10, 20)
    
    def forward(self, x):
        return self.linear(x)

model = SimpleModel()
input_mod = model.export_tvm(spec={"forward": {"x": (1, 10)}})

# 应用零级优化流水线
pipeline = relax.pipeline.zero_pipeline(enable_warning=False)
optimized_mod = pipeline(input_mod)

print("优化后的模块:")
print(optimized_mod)
```

## 实现细节

`zero_pipeline` 函数内部创建了一个包含以下优化步骤的序列：

1. **LegalizeOps** - 操作符合法化，将高级操作符转换为后端支持的低级操作符
2. **AnnotateTIROpPattern** - 为 TIR 操作符标注计算模式
3. **FoldConstant** - 常量折叠优化
4. **FuseOps** - 操作符融合，将多个操作符合并为一个更大的内核
5. **FuseTIR** - TIR 级别的融合优化

如果当前存在激活的 MetaSchedule 数据库，流水线还会应用：
- **MetaScheduleApplyDatabase** - 应用预调优的调度规则

## 相关函数

- [`LegalizeOps`](./legalize_ops.md) - 操作符合法化转换
- [`MetaScheduleApplyDatabase`](./meta_schedule_apply_database.md) - 应用 MetaSchedule 数据库中的预调优结果
- [`FuseOps`](./fuse_ops.md) - 操作符融合优化

## 注意事项

- 默认情况下，警告功能是关闭的（`enable_warning=False`），在生产环境中建议保持此设置以避免过多的警告输出
- 该流水线主要针对已经通过 MetaSchedule 进行过调优的模型，能够充分利用预调优的调度规则
- 流水线的优化级别为 0（`opt_level=0`），表示这是基础优化流水线

## 错误处理

- 如果输入不是有效的 `tvm.ir.IRModule`，TVM 会抛出类型错误异常
- 当 `enable_warning=True` 时，会在控制台输出相关的警告信息，但不会中断程序执行
- 如果 MetaSchedule 数据库不存在或为空，`MetaScheduleApplyDatabase` pass 会静默跳过，不会影响其他优化步骤的执行

---