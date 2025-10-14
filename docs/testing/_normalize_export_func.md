---
title: _normalize_export_func
description: 标准化TVM测试中的模型导出函数和输出格式
---

# _normalize_export_func

## 概述

`_normalize_export_func` 是TVM测试框架中的一个内部辅助函数，主要用于标准化和规范化模型导出函数及其对应的输出格式。在TVM的测试流程中，该函数负责处理不同的模型库导出方式，确保测试过程中生成的模型库文件格式与目标平台和设备兼容。

该函数在TVM测试框架中扮演着重要的桥梁角色，它将用户指定的导出方式（如tar打包、NDK编译等）转换为统一的函数接口，同时确定正确的文件扩展名。这使得TVM的测试用例能够以一致的方式处理不同目标平台的模型部署需求。

## 函数签名

```python
def _normalize_export_func(export_func, output_format) -> Tuple[Callable, str]:
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| export_func | str 或 Callable | 指定模型库的导出方式。支持预定义字符串"tar"、"ndk"或自定义可调用函数 | 无默认值，必须提供 |
| output_format | str | 输出文件的格式扩展名。当export_func为自定义函数时必须指定 | None |

## 返回值

**类型:** `Tuple[Callable, str]`

返回一个包含两个元素的元组：
- 第一个元素是标准化后的导出函数，该函数接受模块和路径参数
- 第二个元素是确定的输出格式字符串（如"tar"、"so"等）

## 使用场景

### 单元测试
在模型编译和导出的单元测试中，确保不同导出方式的一致性

### 集成测试
在端到端的模型部署测试中，处理不同目标平台的库文件生成

### 目标平台测试
针对Android（使用NDK）、Linux等不同平台生成相应的动态库文件

### 打包测试
测试模型库的打包和分发功能，特别是tar格式的归档处理

## 使用示例

```python
import tvm
from tvm import relay
from tvm.testing.runner import _normalize_export_func

# 示例1：使用tar格式导出
def test_tar_export():
    # 创建简单的计算图
    x = relay.var("x", shape=(1, 3, 224, 224), dtype="float32")
    y = relay.nn.softmax(x)
    mod = tvm.IRModule.from_expr(y)
    
    # 编译模块
    with tvm.transform.PassContext(opt_level=3):
        lib = relay.build(mod, target="llvm")
    
    # 标准化导出函数
    export_func, output_format = _normalize_export_func("tar", None)
    print(f"输出格式: {output_format}")  # 输出: tar
    
    # 导出模型库
    # export_func(lib, "model_library.tar")

# 示例2：使用NDK导出（Android目标）
def test_ndk_export():
    export_func, output_format = _normalize_export_func("ndk", None)
    print(f"输出格式: {output_format}")  # 输出: so
    
    # 适用于Android平台的模型库生成
    # export_func(compiled_lib, "model_library.so")

# 示例3：使用自定义导出函数
def custom_compiler(mod, path):
    # 自定义编译逻辑
    return mod.export_library(path)

def test_custom_export():
    # 必须指定output_format
    export_func, output_format = _normalize_export_func(custom_compiler, "dll")
    print(f"输出格式: {output_format}")  # 输出: dll
```

## 注意事项

- 该函数是TVM测试框架的内部函数，不建议在用户代码中直接使用
- 当使用自定义的`export_func`时，必须明确指定`output_format`参数，否则会抛出`ValueError`
- 支持的预定义导出方式包括："tar"（生成tar包）、"ndk"（生成Android动态库）
- 函数返回的导出函数遵循`Callable[[tvm.runtime.Module, str], None]`签名
- 在TVM版本更新时，支持的预定义导出方式可能会发生变化

## 相关函数

- `tvm.runtime.Module.export_library` - 实际的模型库导出函数
- `tvm.contrib.ndk.create_shared` - NDK动态库创建函数
- `tvm.contrib.tar.tar` - tar打包工具函数
- `tvm.testing.runner` - 测试运行器相关函数

该函数与TVM的目标平台和设备管理紧密相关，特别是在处理交叉编译和不同操作系统的库文件格式时起到关键作用。