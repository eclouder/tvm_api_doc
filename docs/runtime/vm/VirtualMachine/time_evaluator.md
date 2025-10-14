---
title: time_evaluator
description: TVM Relax 虚拟机的性能测试方法，用于测量模块中函数的执行时间
---

# time_evaluator

## 概述

`time_evaluator` 是 TVM Relax 虚拟机 (VirtualMachine) 的核心性能测试方法，专门用于精确测量模块中函数的执行时间。该方法返回一个高度可配置的评估器函数，能够进行多次运行并收集详细的性能统计信息。

在 TVM 性能优化工作流中，`time_evaluator` 发挥着关键作用：
- 为模型推理性能提供精确的基准测试
- 支持多种设备类型的性能评估（CPU、GPU、专用加速器）
- 提供统计学上可靠的性能数据，包括平均值、标准差等
- 与 TVM 的编译和优化流程无缝集成
- 支持预热机制，确保测量结果的准确性

## 方法签名

```python
def time_evaluator(
    self,
    func_name: str,
    dev: Device,
    number: int = 10,
    repeat: int = 1,
    min_repeat_ms: int = 0,
    cooldown_interval_ms: int = 0,
    repeats_to_cooldown: int = 1,
    f_preproc: str = "",
) -> Callable[..., tvm.runtime.module.BenchmarkResult]:
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| func_name | str | 要测试的函数名称，通常是模块中的主函数名（如 "main"） | 无 |
| dev | Device | 运行函数的设备，可以是 `tvm.cpu()`, `tvm.cuda(0)` 等 | 无 |
| number | int | 每次重复测量中运行函数的次数，这些运行的平均时间构成一次测量结果 | 10 |
| repeat | int | 重复测量的次数，最终结果包含 `repeat` 个测量值 | 1 |
| min_repeat_ms | int | 每次重复测量的最小持续时间（毫秒），如果设置此参数，`number` 会动态调整 | 0 |
| cooldown_interval_ms | int | 冷却间隔时间（毫秒），在指定次数的重复测量之间插入冷却时间 | 0 |
| repeats_to_cooldown | int | 激活冷却机制前的重复次数 | 1 |
| f_preproc | str | 在执行时间评估器之前要执行的预处理函数名称 | "" |

## 返回值

**类型:** `Callable[..., tvm.runtime.module.BenchmarkResult]`

返回一个评估器函数，该函数：
- 接受与原函数相同的参数
- 返回 `BenchmarkResult` 对象，包含详细的性能测试结果

## 执行机制

函数总共会被调用 `(1 + number × repeat)` 次：
- **预热阶段**: 第一次调用用于预热，结果会被丢弃（处理延迟初始化）
- **测量阶段**: 后续的 `number × repeat` 次调用用于实际测量

## 使用示例

### 基本性能测试

```python
import tvm
from tvm import relax
import numpy as np
import tvm.runtime

# 假设已有编译好的模块
vm = relax.VirtualMachine(executable, tvm.cpu())

# 创建时间评估器
timer = vm.time_evaluator("main", tvm.cpu(), number=10, repeat=3)

# 准备输入数据
input_data = tvm.runtime.ndarray.array(np.random.randn(1, 784).astype("float32"))
param_values = [tvm.runtime.ndarray.array(param.numpy()) for param in model_params]

# 执行性能测试
benchmark_result = timer(input_data, *param_values)

# 查看结果
print(f"平均执行时间: {benchmark_result.mean * 1000:.3f} ms")
print(f"标准差: {benchmark_result.std * 1000:.3f} ms")
print(f"最小时间: {benchmark_result.min * 1000:.3f} ms")
print(f"最大时间: {benchmark_result.max * 1000:.3f} ms")
```

### 与状态API结合使用

```python
# 使用状态API进行性能测试
vm.set_input("main", input_data, *param_values)
timer = vm.time_evaluator("invoke_stateful", tvm.cpu(), number=10, repeat=3)
benchmark_result = timer("main")

print(f"状态API执行时间: {benchmark_result.mean * 1000:.3f} ms")
```

### 使用保存的闭包（推荐）

```python
# 保存函数闭包以减少字典查找开销
vm.save_function("main", "main_saved", input_data, *param_values)

# 对保存的闭包进行性能测试
timer = vm.time_evaluator("main_saved", tvm.cpu(), number=10, repeat=3)
benchmark_result = timer()  # 无需传递参数，因为已保存在闭包中

print(f"闭包执行时间: {benchmark_result.mean * 1000:.3f} ms")
```

### GPU 性能测试

```python
# GPU 设备性能测试
if tvm.cuda().exist:
    # 将数据移动到GPU
    gpu_input = input_data.copyto(tvm.cuda(0))
    gpu_params = [param.copyto(tvm.cuda(0)) for param in param_values]
    
    # 创建GPU时间评估器
    gpu_timer = vm.time_evaluator("main", tvm.cuda(0), number=100, repeat=5)
    gpu_result = gpu_timer(gpu_input, *gpu_params)
    
    print(f"GPU 平均执行时间: {gpu_result.mean * 1000:.3f} ms")
    print(f"GPU vs CPU 加速比: {cpu_result.mean / gpu_result.mean:.2f}x")
```

### 高级配置示例

```python
# 使用最小重复时间和冷却间隔
timer = vm.time_evaluator(
    func_name="main",
    dev=tvm.cpu(),
    number=1,  # 初始运行次数
    repeat=10,
    min_repeat_ms=100,  # 每次重复至少100ms
    cooldown_interval_ms=50,  # 50ms冷却间隔
    repeats_to_cooldown=3,  # 每3次重复后冷却
)

result = timer(input_data, *param_values)
print(f"高级配置测试结果: {result.mean * 1000:.3f} ± {result.std * 1000:.3f} ms")
```

### 实际项目中的使用模式

```python
def benchmark_ir_module(ir_module, device, func_name="main", repeat=3):
    """对 IR 模块进行性能基准测试"""
    import tvm.runtime
    
    try:
        # 编译模块
        with device:
            vm_exec = relax.build(ir_module, target=device)
        vm = relax.VirtualMachine(vm_exec, device)
        
        # 准备测试数据
        dummy_input = tvm.runtime.ndarray.array(
            np.random.randn(1, 784).astype("float32"), device
        )
        
        # 获取模型参数
        params = ir_module["main"].params[1:]  # 跳过输入参数
        param_values = [
            tvm.runtime.ndarray.array(np.random.randn(*param.struct_info.shape).astype("float32"), device)
            for param in params
        ]
        
        # 预热运行
        vm[func_name](dummy_input, *param_values)
        
        # 正式性能测试
        timer = vm.time_evaluator(func_name, device, number=10, repeat=repeat)
        benchmark_result = timer(dummy_input, *param_values)
        
        return {
            "mean_ms": benchmark_result.mean * 1000,
            "std_ms": benchmark_result.std * 1000,
            "min_ms": benchmark_result.min * 1000,
            "max_ms": benchmark_result.max * 1000,
            "device": str(device)
        }
        
    except Exception as e:
        print(f"基准测试失败: {e}")
        return None
```

## BenchmarkResult 对象

返回的 `BenchmarkResult` 对象包含以下重要属性：

| 属性名 | 类型 | 描述 |
|--------|------|------|
| mean | float | 平均执行时间（秒） |
| std | float | 标准差（秒） |
| results | List[float] | 所有重复测量的结果列表 |
| min | float | 最小执行时间（秒） |
| max | float | 最大执行时间（秒） |

### 结果分析示例

```python
result = timer(input_data, *param_values)

# 基本统计信息
print(f"执行时间统计:")
print(f"  平均值: {result.mean * 1000:.3f} ms")
print(f"  标准差: {result.std * 1000:.3f} ms")
print(f"  变异系数: {(result.std / result.mean) * 100:.2f}%")
print(f"  最小值: {result.min * 1000:.3f} ms")
print(f"  最大值: {result.max * 1000:.3f} ms")

# 详细结果分析
print(f"\n所有测量结果 (ms):")
for i, time_ms in enumerate([t * 1000 for t in result.results]):
    print(f"  第{i+1}次: {time_ms:.3f} ms")
```

## 注意事项

### 设备兼容性
- 确保输入数据和模型参数都在正确的设备上
- 使用 `.copyto(device)` 方法进行设备间数据传输

### 内存管理
- 对于大型模型，注意GPU内存使用情况
- 及时释放不需要的张量以避免内存溢出

### 预热重要性
- 第一次调用用于预热，对于准确的性能测量很重要
- GPU 设备特别需要预热以达到稳定的性能状态

### RPC 限制
- 通过RPC使用时，如果函数返回元组可能不工作
- 建议使用状态API或保存的闭包来避免此问题

### 参数匹配
- 确保传递给评估器的参数数量与函数期望的参数数量匹配
- 检查参数的数据类型和形状是否正确

## 错误处理

### 常见错误及解决方案

```python
def safe_benchmark(vm, func_name, device, input_data, param_values, **kwargs):
    """安全的性能基准测试函数"""
    try:
        timer = vm.time_evaluator(func_name, device, **kwargs)
        result = timer(input_data, *param_values)
        return result
    except Exception as e:
        error_msg = str(e).lower()
        
        if "arguments" in error_msg:
            print(f"❌ 参数数量不匹配: {e}")
            print("💡 检查函数签名和传递的参数数量")
        elif "device" in error_msg:
            print(f"❌ 设备不匹配: {e}")
            print("💡 确保数据在正确的设备上")
        elif "memory" in error_msg:
            print(f"❌ 内存错误: {e}")
            print("💡 检查GPU内存使用情况或减少批次大小")
        else:
            print(f"❌ 其他错误: {e}")
        
        return None
```

### 调试技巧

```python
# 调试参数匹配问题
def debug_function_signature(vm, func_name):
    """调试函数签名信息"""
    try:
        arity = vm._get_function_arity(func_name)
        print(f"函数 '{func_name}' 期望 {arity} 个参数")
        
        for i in range(arity):
            param_name = vm._get_function_param_name(func_name, i)
            print(f"  参数 {i}: {param_name}")
    except Exception as e:
        print(f"无法获取函数签名信息: {e}")
```

## 性能优化建议

### 最佳实践

1. **使用保存的闭包**: 减少运行时的字典查找开销
2. **合理设置重复次数**: 平衡测量精度和测试时间
3. **预热充分**: 特别是GPU设备，确保达到稳定性能状态
4. **设备数据对齐**: 避免不必要的设备间数据传输

### 性能对比示例

```python
def compare_optimization_performance(original_mod, optimized_mod, device):
    """比较优化前后的性能"""
    
    def benchmark_module(mod, name):
        vm_exec = relax.build(mod, target=device)
        vm = relax.VirtualMachine(vm_exec, device)
        
        # 准备测试数据
        input_data = tvm.runtime.ndarray.array(
            np.random.randn(1, 784).astype("float32"), device
        )
        
        timer = vm.time_evaluator("main", device, number=50, repeat=5)
        result = timer(input_data)
        
        return {
            "name": name,
            "mean_ms": result.mean * 1000,
            "std_ms": result.std * 1000
        }
    
    original_result = benchmark_module(original_mod, "原始模型")
    optimized_result = benchmark_module(optimized_mod, "优化模型")
    
    speedup = original_result["mean_ms"] / optimized_result["mean_ms"]
    
    print(f"性能对比结果:")
    print(f"  {original_result['name']}: {original_result['mean_ms']:.3f} ± {original_result['std_ms']:.3f} ms")
    print(f"  {optimized_result['name']}: {optimized_result['mean_ms']:.3f} ± {optimized_result['std_ms']:.3f} ms")
    print(f"  加速比: {speedup:.2f}x")
    
    return speedup
```
