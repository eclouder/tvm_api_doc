---
title: pytest_addoption
description: 用于向TVM测试框架添加自定义pytest命令行选项的工具函数
---

# pytest_addoption

## 概述

`pytest_addoption` 是TVM测试框架中用于扩展pytest命令行接口的关键函数。该函数的主要作用是在TVM的测试环境中注册自定义的命令行参数，特别是用于集成Google Test框架的参数传递。

在TVM测试流程中，该函数位于测试插件的初始化阶段，当pytest启动时会自动调用此函数来注册所有可用的命令行选项。通过这个函数，TVM测试框架能够将Google Test的特定参数传递给底层的C++测试代码，实现了Python测试框架与C++测试代码的无缝集成。

## 函数签名

```python
def pytest_addoption(parser):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| parser | `pytest.Parser` | pytest的参数解析器对象，用于添加自定义命令行选项 | 无 |

## 返回值

**类型:** `None`

该函数不返回任何值，其主要作用是通过修改传入的parser对象来注册命令行选项。

## 使用场景

- **C++后端测试**: 当需要运行TVM的C++后端单元测试时，通过此函数传递Google Test参数
- **集成测试**: 在混合Python和C++的集成测试场景中传递测试配置
- **目标平台测试**: 为不同的硬件目标平台（如CPU、GPU）传递特定的测试参数
- **测试过滤**: 使用Google Test的过滤功能来选择性运行特定的测试用例

## 使用示例

```python
# 在命令行中使用--gtest_args参数
# 运行特定的Google Test测试用例
pytest tvm/tests/python/unittest/test_target.py --gtest_args="--gtest_filter=TestTarget*"

# 运行所有测试并显示详细输出
pytest tvm/tests/python/ -v --gtest_args="--gtest_also_run_disabled_tests"

# 在CI环境中使用，设置测试超时和输出格式
pytest tvm/tests/python/ --gtest_args="--gtest_output=xml:report.xml --gtest_timeout=30"
```

## 注意事项

- 该函数是pytest的钩子函数，不应被直接调用，而是由pytest框架在初始化时自动调用
- `--gtest_args` 参数的值会直接传递给底层的Google Test框架，需要符合Google Test的参数格式
- 在使用该功能前，需要确保TVM编译时包含了Google Test支持
- 该函数主要服务于TVM内部的C++测试基础设施，普通用户测试通常不需要直接使用

## 相关函数

- `pytest_configure`: 配置pytest测试环境的配套函数
- `tvm.testing.run_google_test`: 实际执行Google测试的辅助函数
- `tvm.testing.enabled_targets`: 与目标平台测试相关的工具函数

---