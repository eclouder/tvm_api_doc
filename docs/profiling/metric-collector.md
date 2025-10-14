---
title: MetricCollector
description: TVM Runtime Profiling MetricCollector API 文档
---

# MetricCollector

`MetricCollector` 是 TVM 运行时性能分析模块中的核心接口，用于收集自定义的性能指标。

## 概述

`MetricCollector` 提供了一个抽象接口，允许用户定义自己的性能指标收集器。它可以与 `profile_function` 一起使用，收集函数执行过程中的各种性能数据，如缓存命中率、浮点运算次数等。

## 类定义

```python
@_ffi.register_object("runtime.profiling.MetricCollector")
class MetricCollector(Object):
    """Interface for user defined profiling metric collection."""
```

## 核心方法

### Init

初始化调用，在性能分析开始前调用。任何昂贵的预计算都应该在这里进行。

```python
def Init(self, devs: List[DeviceWrapper]) -> None:
    """
    参数:
        devs: 此收集器将运行的设备列表
    """
```

### Start

开始为函数调用收集指标。

```python
def Start(self, dev: Device) -> ObjectRef:
    """
    参数:
        dev: 调用将运行的设备
    
    返回:
        用于维护指标收集状态的对象。此对象将传递给相应的 Stop 调用。
        如果设备不受支持，此函数将返回 nullptr ObjectRef。
    """
```

### Stop

停止收集指标。

```python
def Stop(self, obj: ObjectRef) -> Dict[str, Any]:
    """
    参数:
        obj: 由相应 Start 调用创建的对象
    
    返回:
        一组指标名称和关联值的字典。值必须是 DurationNode、PercentNode、
        CountNode 或 String 之一。
    """
```

## 使用示例

### 基本用法

```python
import tvm
from tvm.runtime import profiling

# 编译函数
f = tvm.compile(my_func, target="llvm", name="my_func")

# 使用 PAPI 指标收集器进行性能分析
prof = profiling.profile_function(
    f,
    tvm.cpu(),
    [profiling.PAPIMetricCollector({tvm.cpu(): ["PAPI_FP_OPS"]})]
)

# 执行并收集性能数据
counters = prof(*args)
print(counters)
```

### 自定义 MetricCollector

```python
class CustomMetricCollector(profiling.MetricCollector):
    def __init__(self):
        # 初始化自定义收集器
        pass
    
    def Init(self, devs):
        # 执行初始化逻辑
        pass
    
    def Start(self, dev):
        # 开始收集指标
        return start_time
    
    def Stop(self, obj):
        # 停止收集并返回指标
        return {"custom_metric": value}
```

## 内置实现

### PAPIMetricCollector

TVM 提供了基于 PAPI (Performance Application Programming Interface) 的内置实现：

```python
class PAPIMetricCollector(MetricCollector):
    """使用 PAPI 收集性能计数器信息的收集器"""
    
    def __init__(self, metric_names: Optional[Dict[Device, Sequence[str]]] = None):
        """
        参数:
            metric_names: 每个设备要收集的指标列表字典。
                         可以通过命令行运行 `papi_native_avail` 查看有效指标列表。
        """
```

#### 使用示例

```python
# 创建 PAPI 指标收集器
papi_collector = profiling.PAPIMetricCollector({
    tvm.cpu(): ["PAPI_FP_OPS", "PAPI_L1_DCM"]
})

# 在 profile_function 中使用
prof = profiling.profile_function(
    module,
    device,
    [papi_collector]
)
```

## 注意事项

1. **设备支持**: 并非所有设备都支持所有类型的指标收集
2. **性能开销**: 指标收集会带来一定的性能开销
3. **PAPI 依赖**: `PAPIMetricCollector` 需要 TVM 在编译时启用 PAPI 支持
4. **线程安全**: 自定义实现需要考虑线程安全性

## 相关 API

- [`profile_function`](./profile-function): 使用 MetricCollector 进行函数性能分析
- [`Report`](./report): 性能分析报告类
- [`DeviceWrapper`](./device-wrapper): 设备包装器类

## 参考资料

- [TVM 性能分析文档](https://tvm.apache.org/docs/how_to/profile_and_tune/index.html)
- [PAPI 官方文档](http://icl.utk.edu/papi/)