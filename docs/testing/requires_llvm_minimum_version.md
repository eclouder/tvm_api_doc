---
title: requires_llvm_minimum_version
description: 用于标记需要特定最低版本LLVM的测试用例的装饰器函数
---

# requires_llvm_minimum_version

## 概述

`requires_llvm_minimum_version` 是 TVM 测试框架中的一个装饰器函数，主要用于在单元测试中标记对 LLVM 版本有特定要求的测试用例。该函数确保只有当系统中安装的 LLVM 版本达到或超过指定的大版本号时，相关的测试才会被执行。

在 TVM 测试流程中，该函数位于测试装饰器层，与 pytest 框架深度集成。它通过检查当前环境的 LLVM 版本，自动跳过不满足版本要求的测试，同时确保测试需要 LLVM 后端支持。这有助于维护跨不同 LLVM 版本的测试兼容性。

## 函数签名

```python
def requires_llvm_minimum_version(major_version):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| major_version | int | 要求的最低 LLVM 主版本号 | 无默认值，必须指定 |

## 返回值

**类型:** `function`

返回一个装饰器函数，该装饰器会为被装饰的测试函数添加版本检查逻辑和 LLVM 后端要求。

## 使用场景

- **单元测试**: 标记依赖于特定 LLVM 版本特性的测试用例
- **目标平台测试**: 确保 LLVM 后端测试在兼容的版本环境中运行
- **跨版本兼容性测试**: 验证 TVM 在不同 LLVM 版本下的行为一致性
- **功能特性测试**: 测试需要特定 LLVM 版本支持的新功能或优化

## 使用示例

```python
import tvm.testing
import pytest

# 标记需要 LLVM 12 或更高版本的测试
@tvm.testing.requires_llvm_minimum_version(12)
def test_llvm12_specific_feature():
    """测试 LLVM 12 引入的特定功能"""
    import tvm
    from tvm import relay
    
    # 构建计算图
    x = relay.var("x", shape=(1, 3, 224, 224), dtype="float32")
    weight = relay.var("weight", shape=(64, 3, 7, 7), dtype="float32")
    y = relay.nn.conv2d(x, weight, channels=64, kernel_size=(7, 7))
    func = relay.Function([x, weight], y)
    
    # 使用 LLVM 后端编译
    with tvm.target.Target("llvm"):
        mod = tvm.IRModule.from_expr(func)
        # 此测试仅在 LLVM >= 12 时运行

# 标记需要 LLVM 15 或更高版本的测试
@tvm.testing.requires_llvm_minimum_version(15)
def test_llvm15_advanced_optimizations():
    """测试 LLVM 15 引入的高级优化特性"""
    # 测试代码...
```

## 注意事项

- **版本检查**: 如果无法检测到 LLVM 版本（如 LLVM 未安装），函数会将版本视为 0，导致测试被跳过
- **pytest 集成**: 该装饰器会生成 pytest 的 `skipif` 标记，与 pytest 测试运行器完全兼容
- **LLVM 后端依赖**: 自动包含 `requires_llvm` 的所有标记，确保测试需要 LLVM 后端支持
- **版本格式**: 只检查主版本号（major version），不考虑次版本号和修订号
- **错误处理**: 在 LLVM 版本检测失败时会优雅降级，不会导致测试框架崩溃

## 相关函数

- [`requires_llvm`](requires_llvm.md): 标记需要 LLVM 后端支持的测试
- [`skip_if`](skip_if.md): 通用的测试跳过装饰器
- [`pytest.mark.skipif`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-skipif): pytest 原生的条件跳过装饰器
- [`llvm_version_major`](llvm_version_major.md): 获取 LLVM 主版本号的工具函数

---