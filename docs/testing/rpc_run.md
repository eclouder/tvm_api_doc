---
title: rpc_run
description: 在远程设备上运行TVM模块并获取执行结果和性能分析数据的测试工具函数
---

# rpc_run

## 概述

`rpc_run` 是 TVM 测试框架中的一个核心工具函数，主要用于在远程设备上执行 TVM 编译后的模块并收集运行结果。该函数在 TVM 的跨平台测试、性能基准测试和设备兼容性验证中扮演着重要角色。

主要功能包括：
- 将 TVM 模块导出为指定格式的部署包
- 通过 RPC 协议连接到远程目标设备
- 在远程设备上加载和执行模块
- 收集模块的执行结果和性能分析数据
- 自动管理临时文件和远程资源清理

该函数通常用于 TVM 的集成测试和端到端测试流程中，特别是在需要验证模型在不同硬件平台（如 ARM CPU、GPU、DSP 等）上正确性和性能的场景。

## 函数签名

```python
def rpc_run(
    mod: 'Module',
    device_type: str,
    args: List[Union['np.ndarray', 'Tensor', int, float]], 
    evaluator_config: Optional['EvaluatorConfig'] = None,
    rpc_config: Optional['RPCConfig'] = None,
    export_func: Union[Callable[['Module', str], None], Literal['tar', 'ndk']] = 'tar',
    output_format: Optional[str] = None
):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| mod | Module | 要执行的 TVM 模块，通常是经过编译的模型 | 无默认值（必需） |
| device_type | str | 目标设备类型，如 "cpu", "cuda", "opencl" 等 | 无默认值（必需） |
| args | List[Union[np.ndarray, Tensor, int, float]] | 输入参数列表，支持多种数据类型 | 无默认值（必需） |
| evaluator_config | Optional[EvaluatorConfig] | 评估器配置，控制性能测量的参数 | None |
| rpc_config | Optional[RPCConfig] | RPC 连接配置，指定远程设备信息 | None |
| export_func | Union[Callable[[Module, str], None], Literal['tar', 'ndk']] | 模块导出函数或导出方式 | 'tar' |
| output_format | Optional[str] | 导出模块的格式 | None |

## 返回值

**类型:** `Tuple[List[Union[np.ndarray, Tensor, int, float]], tvm.runtime.BenchmarkResult]`

返回一个包含两个元素的元组：
- **args**: 模块执行后的输出结果，数据类型与输入参数保持一致
- **profile_result**: 性能分析结果，包含执行时间、重复次数等基准测试数据

## 使用场景

### 单元测试
验证 TVM 模块在特定设备上的功能正确性

### 集成测试
测试整个模型在远程目标设备上的端到端执行流程

### 性能测试
收集模型在不同硬件平台上的性能基准数据

### 目标平台测试
验证 TVM 编译后的模块在嵌入式设备、移动设备等特定平台的兼容性

## 使用示例

```python
import tvm
from tvm import relay
from tvm.contrib import utils
from tvm.testing import rpc_run
import numpy as np

# 创建一个简单的 Relay 计算图
x = relay.var("x", relay.TensorType((1, 3, 224, 224), "float32"))
y = relay.nn.relu(x)
func = relay.Function([x], y)

# 编译模块
target = "llvm"
with tvm.transform.PassContext(opt_level=3):
    mod = relay.build(func, target=target)

# 准备输入数据
input_data = np.random.uniform(-1, 1, size=(1, 3, 224, 224)).astype("float32")

# 配置 RPC 连接（假设已设置环境变量）
# TVM_TRACKER_HOST=your_tracker_host
# TVM_TRACKER_PORT=your_tracker_port

# 在远程设备上运行模块
results, profile_result = rpc_run(
    mod=mod,
    device_type="cpu", 
    args=[input_data],
    export_func="tar"
)

print(f"执行结果形状: {results[0].shape}")
print(f"性能数据: {profile_result}")
```

## 注意事项

- **环境变量配置**: 当 `rpc_config` 为 None 时，函数会读取以下环境变量：
  - `TVM_TRACKER_HOST`: RPC 跟踪器主机地址
  - `TVM_TRACKER_PORT`: RPC 跟踪器端口
  - `TVM_TRACKER_KEY`: RPC 认证密钥

- **临时文件管理**: 函数会自动创建临时目录用于存储导出的模块，并在执行完成后清理所有临时文件

- **设备兼容性**: 确保目标设备支持指定的 `device_type`，并且已正确配置 TVM RPC 运行时

- **性能测量**: `evaluator_config` 可以控制性能测量的精度和重复次数，对于稳定的性能测试建议设置适当的 `number` 和 `repeat` 参数

## 相关函数

- `tvm.meta_schedule.runner.RPCConfig`: RPC 连接配置类
- `tvm.meta_schedule.runner.EvaluatorConfig`: 性能评估配置类
- `tvm.rpc.connect`: 建立 RPC 连接的底层函数
- `tvm.testing.local_run`: 在本地设备上运行模块的类似函数