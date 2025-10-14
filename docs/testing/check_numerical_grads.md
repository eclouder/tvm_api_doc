---
title: check_numerical_grads
description: 用于验证数值梯度与解析梯度一致性的测试工具函数
---

# check_numerical_grads

## 概述

`check_numerical_grads` 是 TVM 测试框架中的一个核心梯度验证工具，主要用于验证深度学习算子或模型的数值梯度与解析梯度是否一致。该函数通过有限差分法计算数值梯度，并与通过自动微分或其他方法计算的解析梯度进行比较，确保梯度计算的正确性。

在 TVM 测试流程中，该函数通常用于：
- 验证新开发的算子梯度实现是否正确
- 确保优化后的计算图梯度计算保持正确
- 在不同目标设备上验证梯度计算的一致性

该函数支持逐步增加采样点数的策略，在梯度误差较大时使用更精确但计算代价更高的五点差分法，在保证准确性的同时平衡计算效率。

## 函数签名

```python
def check_numerical_grads(function, input_values, grad_values, function_value=None, delta=0.001, atol=0.01, rtol=0.1):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| function | Callable | 需要验证梯度的函数，接受位置参数或关键字参数，返回标量结果。必须能够处理 numpy ndarray 输入 | 无 |
| input_values | Dict[str, ndarray] 或 List[ndarray] | 梯度计算点的输入值，可以是字典（变量名到值的映射）或列表（位置参数） | 无 |
| grad_values | Dict[str, ndarray] 或 List[ndarray] | 通过其他方法（如自动微分）计算的解析梯度值，格式需与 input_values 一致 | 无 |
| function_value | float, 可选 | 函数在 input_values 处的计算结果，如果为 None 则自动计算 | None |
| delta | float, 可选 | 有限差分计算中使用的小数值，用于计算偏导数。对于 float32 类型，默认值 1e-3 是合适的选择 | 0.001 |
| atol | float, 可选 | 绝对容差，会乘以梯度大小的平方根 `sqrt(n)` | 0.01 |
| rtol | float, 可选 | 相对容差 | 0.1 |

## 返回值

**类型:** `None`

该函数不返回任何值，如果数值梯度与解析梯度在指定容差范围内一致，则正常执行；否则会抛出 `AssertionError` 异常，包含详细的梯度差异信息。

## 使用场景

### 算子梯度验证
在开发新的 TVM 算子时，使用该函数验证算子的梯度实现是否正确。

### 优化验证
在对计算图进行优化后，验证优化前后的梯度计算是否一致。

### 跨平台测试
在不同目标设备（CPU、GPU、加速器）上验证梯度计算的正确性。

### 单元测试集成
作为 pytest 测试用例的一部分，自动化验证梯度计算。

## 使用示例

```python
import tvm.testing
import numpy as np

# 定义一个简单的函数：f(x, y) = x^2 + y^2
def test_function(x, y):
    return np.sum(x**2 + y**2)

# 输入值
x_val = np.array([1.0, 2.0], dtype=np.float32)
y_val = np.array([3.0, 4.0], dtype=np.float32)

# 解析梯度（手动计算）
# df/dx = 2x, df/dy = 2y
grad_x = 2 * x_val
grad_y = 2 * y_val

# 使用列表格式输入
input_values = [x_val, y_val]
grad_values = [grad_x, grad_y]

# 验证梯度
tvm.testing.check_numerical_grads(test_function, input_values, grad_values)

# 使用字典格式输入
input_dict = {"x": x_val, "y": y_val}
grad_dict = {"x": grad_x, "y": grad_y}

# 验证梯度（字典格式）
tvm.testing.check_numerical_grads(test_function, input_dict, grad_dict)

# 在 TVM 算子测试中的典型用法
def test_softmax_gradient():
    import tvm
    from tvm import te
    
    # 构建 softmax 计算
    n = 10
    A = te.placeholder((n,), name='A')
    B = te.compute((n,), lambda i: tvm.tir.exp(A[i]) / te.sum(tvm.tir.exp(A)))
    
    # 使用 TVM 的梯度计算功能获取解析梯度
    # [实际的梯度计算代码...]
    
    # 验证数值梯度
    # tvm.testing.check_numerical_grads(...)
```

## 注意事项

- **数据类型敏感性**：对于 float32 数据类型，默认的 `delta=1e-3` 通常工作良好，但对于更高精度的数据类型可能需要调整
- **计算代价**：数值梯度计算需要多次函数评估，对于复杂函数可能计算代价较高
- **梯度形状匹配**：输入的梯度值必须与对应的输入变量形状完全一致
- **容差设置**：`atol` 和 `rtol` 参数需要根据具体问题的精度要求进行调整
- **异常处理**：函数会检测 NaN 或无穷大值，并在发现时抛出 ValueError

## 相关函数

- `tvm.testing.assert_allclose`：用于数组近似相等的断言函数
- `tvm.testing.check_mod`：验证 TVM 模块正确性的工具
- `tvm.differentiate`：TVM 的自动微分功能，常与该函数配合使用

该函数是 TVM 测试框架中梯度验证的核心工具，广泛应用于算子开发、优化验证和跨平台测试场景中。