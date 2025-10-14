---
title: enabled_targets
description: 获取所有已启用的目标平台及其关联设备，主要用于TVM测试框架中的多目标参数化测试
---

# enabled_targets

## 概述

`enabled_targets` 函数是 TVM 测试框架中的核心工具函数，用于动态获取当前环境中所有可用的目标平台和对应的设备上下文。该函数的主要作用是在测试执行时自动识别和筛选出可运行的硬件目标，为参数化测试提供设备配置。

在 TVM 测试流程中，该函数通常与 `parametrize_targets` 装饰器配合使用，实现跨多个硬件平台的自动化测试。它通过检查 TVM 编译配置、环境变量设置和设备可用性三个维度来确定哪些目标平台在当前环境中真正可用。

## 函数签名

```python
def enabled_targets():
```

## 参数

此函数不接受任何参数。

## 返回值

**类型:** `List[Tuple[str, tvm.runtime.Device]]`

返回一个列表，其中每个元素都是一个元组，包含：
- 目标平台名称（字符串）
- 对应的 TVM 设备上下文对象

## 使用场景

### 单元测试
在多目标硬件平台上运行相同的测试用例，验证 TVM 算子在不同后端的一致性。

### 集成测试
测试 TVM 模型在不同硬件设备上的端到端推理流程。

### 目标平台验证
验证特定硬件目标在测试环境中的可用性和配置正确性。

### 性能基准测试
在不同设备上收集性能数据，进行跨平台性能比较。

## 使用示例

```python
import tvm.testing
import tvm
from tvm import relay

# 基本用法：获取所有可用目标
targets = tvm.testing.enabled_targets()
print(f"找到 {len(targets)} 个可用目标:")
for target_name, device in targets:
    print(f"  - {target_name}: {device}")

# 在测试函数中使用
def test_simple_addition():
    """在不同目标平台上测试简单的加法运算"""
    targets = tvm.testing.enabled_targets()
    
    for target_name, dev in targets:
        with tvm.target.Target(target_name):
            # 构建简单的计算图
            x = tvm.te.placeholder((10,), name="x")
            y = tvm.te.placeholder((10,), name="y")
            z = tvm.te.compute((10,), lambda i: x[i] + y[i])
            
            # 调度和构建
            s = tvm.te.create_schedule(z.op)
            f = tvm.build(s, [x, y, z], target=target_name)
            
            # 在对应设备上执行
            x_np = np.random.uniform(size=10).astype(np.float32)
            y_np = np.random.uniform(size=10).astype(np.float32)
            z_np = np.zeros(10, dtype=np.float32)
            
            x_tvm = tvm.nd.array(x_np, device=dev)
            y_tvm = tvm.nd.array(y_np, device=dev)
            z_tvm = tvm.nd.array(z_np, device=dev)
            
            f(x_tvm, y_tvm, z_tvm)
            
            # 验证结果
            tvm.testing.assert_allclose(z_tvm.numpy(), x_np + y_np, rtol=1e-5)
            print(f"目标 {target_name} 测试通过")

# 使用 pytest 参数化（推荐方式）
@pytest.mark.parametrize("target,dev", tvm.testing.enabled_targets())
def test_with_parametrize(target, dev):
    """使用参数化装饰器的测试示例"""
    # 测试逻辑...
    pass
```

## 注意事项

### 重要警告
- **必须使用装饰器**: 如果测试函数直接使用 `enabled_targets()` 的结果，必须使用 `@tvm.testing.uses_gpu` 装饰测试函数，否则 GPU 目标将不会被执行
- **环境变量控制**: 目标可用性受 `TVM_TEST_TARGETS` 环境变量控制，如果未设置则使用默认目标列表
- **运行时检查**: 函数会在运行时检查设备实际可用性，即使编译时支持的目标也可能因设备不存在而被过滤

### 目标启用条件
目标平台被标记为 "可运行" 必须满足以下所有条件：
1. TVM 编译时启用了对该目标的支持
2. 目标名称出现在 `TVM_TEST_TARGETS` 环境变量中（或使用默认目标）
3. 系统中存在适合运行该目标的物理设备

### 性能考虑
- 函数调用涉及设备检测，在测试初始化阶段调用为宜
- 避免在紧密循环中重复调用此函数

## 相关函数

### 主要配套函数
- **`tvm.testing.parametrize_targets`**: 推荐的替代方案，自动处理目标参数化和设备管理
- **`tvm.testing.uses_gpu`**: 必需的装饰器，确保 GPU 测试正确执行

### 底层支持函数
- **`_get_targets()`**: 内部函数，获取目标配置信息
- **`tvm.device()`**: 创建设备上下文的 TVM 核心函数

### 测试验证函数
- **`tvm.testing.assert_allclose`**: 数值结果验证
- **`tvm.testing.main()`**: 测试入口点

---

**版本兼容性**: 此函数在 TVM 0.8 及以上版本中保持稳定，接口向后兼容。