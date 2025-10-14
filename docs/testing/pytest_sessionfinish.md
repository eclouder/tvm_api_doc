---
title: pytest_sessionfinish
description: 用于处理TVM测试会话结束时的退出状态，特别优化了标记表达式测试选择场景
---

# pytest_sessionfinish

## 概述

`pytest_sessionfinish` 是 TVM 测试框架中的一个 pytest 钩子函数，专门用于在测试会话结束时处理退出状态。该函数的主要作用是优化测试选择场景下的退出行为，当使用标记表达式选择测试用例时，如果未收集到任何匹配的测试，函数会将退出状态从"无测试收集"调整为"正常退出"，避免因测试选择范围限制而导致的错误退出。

在 TVM 测试流程中，该函数位于测试执行的最后阶段，与 pytest 的会话生命周期管理紧密集成。它确保了 TVM 的测试选择功能在各种测试场景下都能提供合理的退出行为，特别是在使用 `-m` 标记表达式筛选测试时。

## 函数签名

```python
def pytest_sessionfinish(session, exitstatus):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| session | `pytest.Session` | pytest 测试会话对象，包含测试配置和状态信息 | 无默认值 |
| exitstatus | `pytest.ExitCode` | pytest 的原始退出状态代码 | 无默认值 |

## 返回值

**类型:** `None`

该函数不直接返回值，但会修改会话的退出状态 (`session.exitstatus`)。

## 使用场景

### 单元测试
在 TVM 单元测试中，当使用标记表达式选择特定类型的测试时（如 `pytest -m "cuda"`），如果当前环境中没有匹配的 CUDA 设备，该函数确保测试正常退出而非报错。

### 集成测试
在跨平台集成测试中，针对不同目标平台（如 x86、ARM、CUDA、OpenCL）的测试选择，该函数提供了更友好的退出体验。

### 目标平台测试
当测试特定硬件目标时，如果目标设备不可用，该函数避免了不必要的错误退出，使得测试流水线能够继续执行其他测试。

## 使用示例

```python
# 在实际的 TVM 测试中，该函数由 pytest 自动调用
# 但可以通过以下方式验证其行为：

import pytest
import tvm.testing

# 使用标记表达式选择不存在的测试标记
# 正常情况下会返回 NO_TESTS_COLLECTED 退出码
# 但经过 pytest_sessionfinish 处理后，会变为 OK 退出码

# 在命令行中测试：
# pytest -m "nonexistent_marker" tests/python/relay/test_op_level2.py

# 或者在 Python 代码中模拟：
def test_exit_status_handling():
    """验证退出状态处理机制"""
    # 模拟使用标记表达式但无测试匹配的场景
    # 在实际测试中，pytest_sessionfinish 会自动处理这种情况
    pass
```

## 注意事项

- 该函数仅在使用了标记表达式 (`-m` 参数) 且未收集到任何测试时才会修改退出状态
- 对于其他原因导致的"无测试收集"情况（如测试路径错误），退出状态不会被修改
- 该函数是 pytest 的钩子函数，通常不需要直接调用
- 与 TVM 0.8+ 版本兼容，依赖于 pytest 的会话管理机制

## 相关函数

- `pytest_configure` - pytest 配置阶段的钩子函数
- `pytest_collection_modifyitems` - 测试项收集后的修改钩子
- `tvm.testing.main` - TVM 测试的主入口函数
- `tvm.testing.plugin` - TVM pytest 插件的其他组件

该函数是 TVM 测试框架用户体验优化的重要组成部分，特别在使用复杂标记表达式进行测试筛选时提供了更好的开发体验。