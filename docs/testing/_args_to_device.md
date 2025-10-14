---
title: _args_to_device
description: 将输入参数上传到指定设备的内部工具函数，主要用于TVM测试框架中的设备数据准备
---

# _args_to_device

## 概述

`_args_to_device` 是 TVM 测试框架中的一个内部工具函数，主要负责将输入参数（如 numpy 数组或 TVM Tensor）上传到指定的计算设备上。该函数在 TVM 的测试流程中扮演着关键的数据准备角色，特别是在需要跨不同硬件设备（如 CPU、GPU、FPGA 等）执行测试时。

在 TVM 测试框架中，当需要验证算子在不同目标设备上的正确性或性能时，必须确保输入数据位于正确的设备内存中。`_args_to_device` 函数正是为此目的而设计，它能够：
- 自动检测输入参数的数据类型
- 将 numpy 数组和 TVM Tensor 复制到目标设备
- 保持标量参数不变
- 为后续的 kernel 执行准备正确的设备数据

该函数通常被其他测试工具函数（如 `run_and_check`）内部调用，是 TVM 测试基础设施的重要组成部分。

## 函数签名

```python
def _args_to_device(args, device):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| args | List[Any] | 需要上传到设备的参数列表，支持 numpy.ndarray、tvm.runtime.Tensor、int、float 类型 | 无默认值，必须提供 |
| device | Device | TVM 目标设备对象，指定数据要上传到的目标设备 | 无默认值，必须提供 |

## 返回值

**类型:** `List[Union[Tensor, int, float]]`

返回一个新的参数列表，其中所有的数组类型数据（numpy.ndarray 和 TVM Tensor）都已被复制到指定的设备上，而标量类型数据（int、float）保持不变。返回的 TVM Tensor 对象都位于目标设备的存储空间中。

## 使用场景

### 单元测试
在算子单元测试中，当需要验证同一个算子在多种设备上的行为一致性时，使用该函数准备设备数据。

### 集成测试
在端到端的模型测试中，确保中间结果能够在不同设备间正确传递。

### 性能测试
在基准测试中，将输入数据上传到目标设备（如 GPU），以测量设备上的实际执行性能。

### 目标平台测试
验证 TVM 编译的代码在不同硬件平台（如 ARM CPU、NVIDIA GPU、Intel FPGA）上的正确性。

## 使用示例

```python
import tvm
import tvm.testing
import numpy as np
from tvm.runtime import Device

# 准备测试数据
np_input1 = np.random.rand(10, 10).astype(np.float32)
np_input2 = np.random.rand(10, 10).astype(np.float32)
scalar_param = 3.14

# 获取目标设备（例如 CUDA GPU）
device = tvm.cuda(0)

# 使用 _args_to_device 上传数据到设备
device_args = _args_to_device([np_input1, np_input2, scalar_param], device)

# 现在 device_args[0] 和 device_args[1] 是位于 GPU 上的 Tensor
# device_args[2] 保持为原始标量值 3.14

# 这些设备数据可以直接用于 kernel 执行
print(f"第一个参数设备: {device_args[0].device}")
print(f"第二个参数设备: {device_args[1].device}") 
print(f"标量参数类型: {type(device_args[2])}")
```

## 注意事项

- **内部函数警告**: 该函数是 TVM 测试框架的内部工具函数，普通用户通常不需要直接调用，而应该使用更高级的测试接口。
- **数据类型限制**: 仅支持 numpy.ndarray、tvm.runtime.Tensor、int 和 float 类型，其他类型会抛出 ValueError。
- **内存管理**: 函数会创建新的设备内存，调用者需要负责适当的内存管理。
- **设备兼容性**: 确保提供的设备参数与实际的硬件设备匹配，否则可能导致运行时错误。
- **性能考虑**: 对于大型数组，数据上传可能比较耗时，在性能测试中应考虑这部分开销。

## 相关函数

- `tvm.testing.run_and_check`: 执行并验证测试结果的高级接口，内部使用 `_args_to_device`
- `tvm.runtime.Tensor`: TVM 运行时张量类
- `tvm.runtime.empty`: 在指定设备上创建未初始化的张量
- `tvm.testing.assert_allclose`: 验证设备上计算结果正确性的断言函数

---