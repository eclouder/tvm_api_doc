---
title: register_pipeline
description: TVM Relax Pipeline - register_pipeline 函数 API 文档
---

# register_pipeline

## 概述

`register_pipeline` 是一个装饰器工厂函数，用于在 TVM Relax 编译器中注册新的 pipeline。Pipeline 是 TVM 中用于定义和执行模型编译流程的重要组件，通过此函数可以扩展 TVM 的编译能力。

## 函数签名

```python
def register_pipeline(name: str)
```

## 参数

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| name | str | 无 | 要注册的 pipeline 名称，必须是唯一的标识符 |

## 返回值

**类型:** `Callable[[Callable], Callable]`

返回一个装饰器函数，该装饰器会将目标函数注册到 TVM 的全局 pipeline 映射表中。

## 使用示例

### 基本用法

```python
import tvm
from tvm.relax import register_pipeline

# 使用装饰器注册一个名为 "custom_pipeline" 的 pipeline
@register_pipeline("custom_pipeline")
def my_custom_pipeline(mod, target):
    """自定义 pipeline 实现"""
    # 在这里实现自定义的编译流程
    # mod: 输入的 IRModule
    # target: 目标硬件平台
    return mod

# 注册后，可以通过名称访问该 pipeline
from tvm.relax.pipeline import get_pipeline
pipeline_func = get_pipeline("custom_pipeline")
```

### 高级用法

```python
# 注册一个支持不同优化级别的 pipeline
@register_pipeline("advanced_opt_pipeline")
def advanced_optimization_pipeline(mod, target, opt_level=3):
    """支持优化级别配置的 pipeline"""
    if opt_level >= 1:
        mod = tvm.relax.transform.FoldConstant()(mod)
    if opt_level >= 2:
        mod = tvm.relax.transform.FuseOps()(mod)
    if opt_level >= 3:
        mod = tvm.relax.transform.LegalizeOps()(mod)
    return mod

# 使用不同优化级别
optimized_mod = advanced_optimization_pipeline(original_mod, target_cpu, opt_level=2)
```

## 实现细节

该函数通过维护一个全局的 `PIPELINE_MAP` 字典来管理所有注册的 pipeline。当调用 `register_pipeline(name)` 时：

1. 首先检查 `name` 是否已经在 `PIPELINE_MAP` 中存在，如果存在则抛出 `ValueError`
2. 返回一个内部装饰器函数 `_register`
3. `_register` 装饰器将目标函数注册到 `PIPELINE_MAP` 中，键为 `name`，值为被装饰的函数
4. 返回原始函数，保持其原有功能不变

## 相关函数

- [`get_pipeline`](./get_pipeline.md) - 根据名称获取已注册的 pipeline 函数
- [`list_pipelines`](./list_pipelines.md) - 列出所有已注册的 pipeline

## 注意事项

- Pipeline 名称必须是唯一的，重复注册相同名称的 pipeline 会导致 `ValueError`
- 注册的 pipeline 函数应该接受至少两个参数：`mod` (IRModule) 和 `target` (Target)
- 建议使用有意义的、描述性的名称来命名 pipeline，便于其他开发者理解其功能
- 注册的 pipeline 在 TVM 进程的生命周期内保持有效

## 错误处理

- **ValueError**: 当尝试注册一个已经存在的 pipeline 名称时抛出
  ```python
  # 这会抛出 ValueError
  @register_pipeline("existing_pipeline")
  def pipeline1(mod, target):
      pass
  
  @register_pipeline("existing_pipeline")  # ValueError!
  def pipeline2(mod, target):
      pass
  ```

- **TypeError**: 当传入的 `name` 参数不是字符串类型时抛出

建议在注册 pipeline 前检查名称是否已存在，或者使用 try-except 块来处理可能的异常：

```python
try:
    @register_pipeline("my_pipeline")
    def my_pipeline_func(mod, target):
        # pipeline 实现
        return mod
except ValueError as e:
    print(f"Pipeline registration failed: {e}")
```

---