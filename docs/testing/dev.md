---
title: dev
description: 获取TVM设备句柄，为需要设备访问的测试用例提供设备支持
---

# dev

## 概述

`dev` 函数是 TVM 测试框架中的一个核心工具函数，主要用于在测试环境中获取指定目标平台的设备句柄。该函数封装了 `tvm.device()` 调用，为测试用例提供标准化的设备访问接口。

在 TVM 测试流程中，`dev` 函数扮演着关键角色：
- 为单元测试、集成测试和性能测试提供设备初始化支持
- 确保测试用例能够在正确的目标设备上执行计算
- 简化测试代码中对设备管理的复杂性
- 与 TVM 的运行时系统紧密集成，保证设备分配的正确性

## 函数签名

```python
def dev(target):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| target | str | 目标设备描述符，指定要使用的计算设备（如 "llvm"、"cuda"、"opencl" 等） | 无 |

## 返回值

**类型:** `tvm.runtime.Device`

返回一个 TVM 运行时设备对象，该对象封装了目标硬件设备的上下文信息，可用于后续的张量分配和内核执行。

## 使用场景

### 单元测试
在测试单个算子或函数时，需要确保在正确的设备上创建输入张量和执行计算。

### 集成测试
验证多个 TVM 组件在特定设备上的协同工作能力。

### 性能测试
在不同目标设备上评估算子的执行性能。

### 目标平台测试
测试 TVM 对各种硬件后端的支持情况，包括 CPU、GPU 和专用加速器。

## 使用示例

```python
import tvm
import tvm.testing
from tvm import te

# 基本用法：获取CPU设备
def test_cpu_operation():
    target = "llvm"
    device = tvm.testing.dev(target)
    
    # 在获取的设备上创建张量
    A = te.placeholder((1024,), name="A", dtype="float32")
    B = te.compute(A.shape, lambda i: A[i] + 1, name="B")
    
    s = te.create_schedule(B.op)
    func = tvm.build(s, [A, B], target=target)
    
    # 在设备上执行计算
    a_np = np.random.uniform(size=1024).astype("float32")
    a = tvm.nd.array(a_np, device=device)
    b = tvm.nd.array(np.zeros(1024, dtype="float32"), device=device)
    func(a, b)
    
    # 验证结果
    tvm.testing.assert_allclose(b.numpy(), a_np + 1, rtol=1e-5)

# 测试GPU设备
def test_gpu_operation():
    if tvm.testing.uses_gpu():
        target = "cuda"
        device = tvm.testing.dev(target)
        
        # GPU特定的测试逻辑
        # ...
```

## 注意事项

- 在使用 GPU 或其他加速器设备前，请确保 TVM 已正确编译并支持该目标平台
- 对于需要特定硬件支持的测试，建议使用 `tvm.testing.requires_*` 装饰器来标记测试条件
- 在多设备测试环境中，注意设备内存的管理和释放
- 该函数返回的设备对象应在同一测试会话中重复使用以提高性能

## 相关函数

- `tvm.testing.enabled_targets()` - 获取当前环境中可用的目标平台列表
- `tvm.testing.requires_gpu()` - 标记需要GPU支持的测试用例
- `tvm.device()` - 底层的设备获取函数
- `tvm.runtime.Device` - 设备对象的类定义