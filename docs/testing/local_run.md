---
title: local_run
description: 在本地设备上运行TVM模块并获取执行结果和性能分析数据
---

# local_run

## 概述

`local_run` 是 TVM 测试框架中的一个核心工具函数，主要用于在本地设备上执行编译后的 TVM 模块并收集运行结果。该函数通过临时目录管理模块导出、设备配置、参数传输和性能分析，为 TVM 的单元测试、集成测试和性能基准测试提供标准化的执行环境。

在 TVM 测试流程中，`local_run` 位于模型编译和实际部署之间，负责：
- 将编译后的模块导出为指定格式
- 在目标设备上加载和执行模块
- 自动处理参数在主机和设备间的传输
- 收集详细的性能分析数据

## 函数签名

```python
def local_run(
    mod: 'Module',
    device_type: str,
    args: List[Union['np.ndarray', 'Tensor', int, float]], 
    evaluator_config: Optional['EvaluatorConfig'] = None,
    export_func: Union[Callable[['Module', str], None], Literal['tar', 'ndk']] = 'tar',
    output_format: Optional[str] = None
):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| mod | Module | 要执行的TVM模块，通常是经过编译的模型 | 无 |
| device_type | str | 目标设备类型，如"cuda"、"cpu"、"opencl"等 | 无 |
| args | List[Union[np.ndarray, Tensor, int, float]] | 输入参数列表，支持numpy数组、TVM张量、标量值 | 无 |
| evaluator_config | Optional[EvaluatorConfig] | 性能评估器配置，控制测量次数、重复次数等 | None |
| export_func | Union[Callable[[Module, str], None], Literal["tar", "ndk"]] | 模块导出函数或预定义导出方式 | "tar" |
| output_format | Optional[str] | 导出模块的格式，如"so"、"tar"等 | None |

## 返回值

**类型:** `Tuple[List[Union[np.ndarray, Tensor, int, float]], tvm.runtime.BenchmarkResult]`

返回一个包含两个元素的元组：
- **第一个元素**: 模块执行结果的列表，所有设备上的张量数据都已转换为numpy数组格式
- **第二个元素**: 性能分析结果，包含详细的计时信息和统计指标

## 使用场景

### 单元测试
验证单个算子或子图在不同设备上的正确性

### 集成测试
测试完整模型从编译到执行的端到端流程

### 性能测试
收集模型在不同硬件平台上的性能基准数据

### 跨平台测试
验证模型在多种目标设备（CPU、GPU、加速器等）上的兼容性

## 使用示例

```python
import tvm
import tvm.testing
import numpy as np
from tvm.meta_schedule.runner import EvaluatorConfig

# 编译一个简单的TVM模块
A = tvm.te.placeholder((1024,), name="A")
B = tvm.te.compute((1024,), lambda i: A[i] + 1, name="B")
s = tvm.te.create_schedule(B.op)
target = "llvm"
mod = tvm.build(s, [A, B], target)

# 准备输入数据
input_data = np.random.uniform(size=1024).astype(np.float32)

# 配置评估参数
config = EvaluatorConfig(number=10, repeat=3)

# 在CPU上运行模块
results, profile = tvm.testing.local_run(
    mod=mod,
    device_type="cpu",
    args=[input_data],
    evaluator_config=config,
    export_func="tar"
)

print(f"执行结果: {results[0]}")
print(f"性能分析: {profile}")
print(f"平均执行时间: {profile.mean * 1000:.2f} ms")
```

## 注意事项

- **设备兼容性**: 确保目标设备类型与编译时指定的target匹配
- **内存管理**: 函数会自动处理设备内存的分配和释放，但大模型可能仍需注意内存限制
- **导出格式**: 默认使用tar格式导出，对于Android设备建议使用"ndk"格式
- **性能测量**: 通过EvaluatorConfig可精确控制性能测量的参数，避免测量误差
- **临时文件**: 所有导出文件都在临时目录中创建，函数执行完毕后自动清理

## 相关函数

- `tvm.testing.run_on_rpc`: 在远程设备上运行TVM模块
- `tvm.meta_schedule.runner.local_runner`: Meta Schedule框架中的本地运行器
- `tvm.runtime.load_module`: 加载已导出的TVM模块
- `tvm.runtime.Device`: TVM设备管理接口