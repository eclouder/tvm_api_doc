# TVM Testing API 文档

TVM Testing 模块提供了一套完整的测试工具和实用函数，用于 TVM 深度学习编译器的测试开发。

## 模块概述

TVM Testing 模块包含以下主要组件：

- **测试断言和验证**: 用于验证计算结果和表达式的正确性
- **目标和设备管理**: 管理不同的编译目标和计算设备
- **测试参数化**: 支持参数化测试和测试固件
- **pytest 集成**: 与 pytest 框架的深度集成
- **运行器**: 本地和远程执行测试的工具
- **并发测试**: 多进程和并发测试支持

## 函数分类


### 测试断言和验证

- [assert_allclose](assert_allclose.md) - TVM 测试工具函数
- [check_numerical_grads](check_numerical_grads.md) - TVM 测试工具函数
- [assert_prim_expr_equal](assert_prim_expr_equal.md) - TVM 测试工具函数
- [check_bool_expr_is_true](check_bool_expr_is_true.md) - TVM 测试工具函数

### 目标和设备管理

- [device_enabled](device_enabled.md) - TVM 测试工具函数
- [enabled_targets](enabled_targets.md) - TVM 测试工具函数
- [parametrize_targets](parametrize_targets.md) - TVM 测试工具函数
- [exclude_targets](exclude_targets.md) - TVM 测试工具函数

### 测试要求和跳过

- [requires_llvm_minimum_version](requires_llvm_minimum_version.md) - TVM 测试工具函数
- [requires_nvcc_version](requires_nvcc_version.md) - TVM 测试工具函数
- [requires_cuda_compute_version](requires_cuda_compute_version.md) - TVM 测试工具函数
- [skip_if_32bit](skip_if_32bit.md) - TVM 测试工具函数
- [requires_package](requires_package.md) - TVM 测试工具函数

### 参数化和固件

- [parameter](parameter.md) - TVM 测试工具函数
- [parameters](parameters.md) - TVM 测试工具函数
- [fixture](fixture.md) - TVM 测试工具函数
- [parametrize_targets](parametrize_targets.md) - TVM 测试工具函数

### 运行器和执行

- [local_run](local_run.md) - TVM 测试工具函数
- [rpc_run](rpc_run.md) - TVM 测试工具函数

### pytest集成

- [pytest_configure](pytest_configure.md) - TVM 测试工具函数
- [pytest_addoption](pytest_addoption.md) - TVM 测试工具函数
- [pytest_generate_tests](pytest_generate_tests.md) - TVM 测试工具函数
- [dev](dev.md) - TVM 测试工具函数

### 进程池和并发

- [initializer](initializer.md) - TVM 测试工具函数
- [fast_summation](fast_summation.md) - TVM 测试工具函数
- [slow_summation](slow_summation.md) - TVM 测试工具函数
- [timeout_job](timeout_job.md) - TVM 测试工具函数

### TIR调度

- [mma_schedule](mma_schedule.md) - TVM 测试工具函数
- [mfma_schedule](mfma_schedule.md) - TVM 测试工具函数

### FFI和C++接口


### 其他工具函数

- [after_initializer](after_initializer.md) - TVM 测试工具函数
- [call_cpp_ffi](call_cpp_ffi.md) - TVM 测试工具函数
- [call_cpp_py_ffi](call_cpp_py_ffi.md) - TVM 测试工具函数
- [call_py_ffi](call_py_ffi.md) - TVM 测试工具函数
- [check_int_constraints_trans_consistency](check_int_constraints_trans_consistency.md) - TVM 测试工具函数
- [get_dtype_range](get_dtype_range.md) - TVM 测试工具函数
- [identity_after](identity_after.md) - TVM 测试工具函数
- [identity_py](identity_py.md) - TVM 测试工具函数
- [install_request_hook](install_request_hook.md) - TVM 测试工具函数
- [is_ampere_or_newer](is_ampere_or_newer.md) - TVM 测试工具函数
- [known_failing_targets](known_failing_targets.md) - TVM 测试工具函数
- [pytest_collection_modifyitems](pytest_collection_modifyitems.md) - TVM 测试工具函数
- [pytest_sessionfinish](pytest_sessionfinish.md) - TVM 测试工具函数
- [register_ffi](register_ffi.md) - TVM 测试工具函数
- [skip_if_no_reference_system](skip_if_no_reference_system.md) - TVM 测试工具函数
- [skip_parameterizations](skip_parameterizations.md) - TVM 测试工具函数
- [strtobool](strtobool.md) - TVM 测试工具函数
- [terminate_self](terminate_self.md) - TVM 测试工具函数
- [xfail_parameterizations](xfail_parameterizations.md) - TVM 测试工具函数
- [_args_to_device](_args_to_device.md) - TVM 测试工具函数
- [_args_to_numpy](_args_to_numpy.md) - TVM 测试工具函数
- [_normalize_export_func](_normalize_export_func.md) - TVM 测试工具函数


## 使用指南

### 基本测试编写

```python
import tvm.testing

# 使用参数化测试
@tvm.testing.parametrize_targets("llvm", "cuda")
def test_my_function(target, dev):
    # 测试代码
    pass

# 使用断言验证结果
def test_computation():
    result = compute_something()
    expected = get_expected_result()
    tvm.testing.assert_allclose(result, expected)
```

### 目标和设备管理

```python
# 检查设备是否可用
if tvm.testing.device_enabled("cuda"):
    # CUDA 相关测试
    pass

# 获取所有启用的目标
for target, dev in tvm.testing.enabled_targets():
    # 在每个目标上运行测试
    pass
```

### 测试要求和跳过

```python
# 要求特定版本
@tvm.testing.requires_cuda_compute_version(7, 0)
def test_cuda_feature():
    pass

# 跳过特定条件
@tvm.testing.skip_if_32bit("不支持32位系统")
def test_64bit_only():
    pass
```

## 总计

本文档包含 50 个 TVM Testing API 函数的详细说明。

---

*此文档由 TVM Testing API 文档生成器自动生成*
