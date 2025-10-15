---
title: default_build_pipeline
description: TVM Relax Pipeline - default_build_pipeline 函数 API 文档
---

# default_build_pipeline

## 概述

`default_build_pipeline` 是 TVM Relax 编译器中默认的编译流水线函数，用于定义和执行从 Relax IR 模块到可执行代码的标准编译过程。该函数返回一个包含一系列优化和转换 pass 的模块级 pass，是 `tvm.compile` 中使用的标准编译流程。

## 函数签名

```python
def default_build_pipeline()
```

## 参数

此函数不接受任何参数。

## 返回值

**类型:** `tvm.transform.ModulePass`

返回一个模块级别的 pass，该 pass 封装了完整的默认编译流水线。当应用于 TVM IR 模块时，会按顺序执行一系列优化和转换步骤。

## 使用示例

### 基本用法

```python
import tvm
from tvm import relax
from tvm.relax import transform

# 获取默认编译流水线
pipeline = relax.pipeline.default_build_pipeline()

# 应用流水线到 Relax IR 模块
mod_transformed = pipeline(mod)

# 或者直接在编译时使用
with tvm.transform.PassContext(opt_level=3):
    ex = relax.vm.build(mod, target="llvm", pipeline=relax.pipeline.default_build_pipeline())
```

### 自定义流水线

```python
# 基于默认流水线创建自定义流水线
def custom_build_pipeline():
    default_pipeline = relax.pipeline.default_build_pipeline()
    
    # 在默认流水线前后添加自定义 pass
    @tvm.transform.module_pass(opt_level=0)
    def _custom_pipeline(mod, ctx):
        # 前置自定义处理
        mod = transform.MyCustomPass()(mod)
        
        # 应用默认流水线
        mod = default_pipeline(mod)
        
        # 后置自定义处理
        mod = transform.AnotherCustomPass()(mod)
        return mod
    
    return _custom_pipeline
```

## 实现细节

`default_build_pipeline` 函数内部定义了一个模块级别的 pass，该 pass 按顺序执行以下关键转换步骤：

1. **调度采样** (`backend.DispatchSampling`) - 处理随机采样操作
2. **排序扫描调度** (`backend.DispatchSortScan`) - 优化排序和扫描操作
3. **操作合法化** (`transform.LegalizeOps`) - 将高级操作转换为目标后端支持的操作
4. **数据流重塑重写** (`transform.RewriteDataflowReshape`) - 优化数据流图中的 reshape 操作
5. **转换为非数据流** (`transform.ToNonDataflow`) - 将数据流图转换为传统计算图
6. **移除纯度检查** (`transform.RemovePurityChecking`) - 移除函数纯度检查相关代码
7. **CallTIR 重写** (`transform.CallTIRRewrite`) - 重写 TIR 调用
8. **静态规划块内存** (`transform.StaticPlanBlockMemory`) - 静态内存分配规划
9. **CUDA 图重写** (`transform.RewriteCUDAGraph`) - 针对 CUDA 后端优化计算图
10. **降低 AllocTensor** (`transform.LowerAllocTensor`) - 将张量分配操作降低到运行时
11. **最后使用后清理** (`transform.KillAfterLastUse`) - 清理不再使用的变量
12. **降低运行时内置函数** (`transform.LowerRuntimeBuiltin`) - 处理运行时内置函数
13. **计算原始值** (`transform.ComputePrimValue`) - 计算编译时常量
14. **VM 形状降低** (`transform.VMShapeLower`) - 处理虚拟机中的形状计算
15. **附加全局符号** (`transform.AttachGlobalSymbol`) - 为函数附加全局符号

这些 pass 按顺序执行，每个 pass 都对 IR 模块进行特定的转换和优化，最终生成适合目标后端执行的优化代码。

## 相关函数

- [`tvm.relax.transform.Sequential`](./sequential.md) - 顺序执行多个 pass 的容器
- [`tvm.relax.vm.build`](./vm_build.md) - 使用指定流水线构建虚拟机可执行文件
- [`tvm.transform.PassContext`](./pass_context.md) - 编译 pass 的上下文管理器

## 注意事项

- 该流水线是 TVM Relax 的默认编译流程，适用于大多数使用场景
- 流水线中的 pass 顺序经过精心设计，改变顺序可能导致编译错误或性能下降
- 对于特定的硬件目标或特殊需求，建议基于此流水线进行自定义扩展
- 流水线中的某些 pass（如 CUDA 图重写）主要针对特定后端优化

## 错误处理

- 如果输入模块不符合 Relax IR 规范，可能在执行早期 pass 时抛出验证错误
- 当目标后端不支持某些操作时，`LegalizeOps` pass 可能失败
- 内存规划相关的 pass 可能在内存不足的情况下失败
- 建议在应用流水线前确保输入模块已通过 `relax.analysis.well_formed` 检查