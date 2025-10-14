---
title: mfma_schedule
description: 为使用MFMA指令的GEMM运算创建张量化调度方案，主要用于TVM测试框架中的GPU目标平台测试。
---

# mfma_schedule

## 概述

`mfma_schedule` 是一个专门为TVM测试框架设计的张量化调度生成函数，主要用于为使用矩阵融合乘加（MFMA）指令的通用矩阵乘法（GEMM）运算创建优化的TIR调度。该函数在TVM的GPU目标平台测试中扮演重要角色，特别是针对AMD GPU的MFMA指令集优化。

该函数通过将GEMM计算分解为多级层次结构，并应用张量化内在函数，生成高效的GPU内核代码。它主要用于：
- 验证TVM对MFMA指令的支持
- 测试不同数据类型的GEMM性能
- 验证张量化调度的正确性
- 性能基准测试和回归测试

## 函数签名

```python
def mfma_schedule(
    workload,
    k_inner,
    in_dtype,
    b_transposed,
    i_factors,
    j_factors,
    k_factors,
    index_map_A,
    index_map_B,
    index_map_C,
    ldmatrix_a_intrin,
    ldmatrix_b_intrin,
    mfma_intrin,
    mfma_fill_intrin,
    mfma_store_intrin,
    shared_scope="shared"
):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| workload | tvm.IRModule | 包含GEMM计算的TIR模块 | 无 |
| k_inner | int | MFMA内部累加维度大小 | 无 |
| in_dtype | str | 输入数据类型（如"int8", "float16"） | 无 |
| b_transposed | bool | 矩阵B是否转置 | 无 |
| i_factors | List[int] | M维度的循环分割因子 | 无 |
| j_factors | List[int] | N维度的循环分割因子 | 无 |
| k_factors | List[int] | K维度的循环分割因子 | 无 |
| index_map_A | Callable | 矩阵A的布局变换映射 | 无 |
| index_map_B | Callable | 矩阵B的布局变换映射 | 无 |
| index_map_C | Callable | 矩阵C的布局变换映射 | 无 |
| ldmatrix_a_intrin | tvm.tir.PrimFunc | 加载矩阵A的张量化内在函数 | 无 |
| ldmatrix_b_intrin | tvm.tir.PrimFunc | 加载矩阵B的张量化内在函数 | 无 |
| mfma_intrin | tvm.tir.PrimFunc | MFMA计算张量化内在函数 | 无 |
| mfma_fill_intrin | tvm.tir.PrimFunc | MFMA初始化张量化内在函数 | 无 |
| mfma_store_intrin | tvm.tir.PrimFunc | MFMA存储张量化内在函数 | 无 |
| shared_scope | str | 共享内存作用域 | "shared" |

## 返回值

**类型:** `tvm.tir.Schedule`

返回一个优化后的TIR调度对象，该调度应用了MFMA张量化并包含了多级内存层次优化（共享内存、warp级别缓存等）。

## 使用场景

该函数主要应用于以下TVM测试场景：

- **单元测试**：验证MFMA调度生成器的正确性
- **集成测试**：测试张量化调度与TVM代码生成的集成
- **性能测试**：比较不同配置下MFMA调度的性能
- **目标平台测试**：针对AMD GPU平台的MFMA指令支持测试
- **回归测试**：确保调度优化不会引入性能回归

## 使用示例

```python
import tvm
import tvm.testing
from tvm.script import tir as T

# 定义基础的GEMM计算
@T.prim_func
def gemm(
    A: T.Buffer((1024, 1024), "float16"),
    B: T.Buffer((1024, 1024), "float16"), 
    C: T.Buffer((1024, 1024), "float16")
):
    for i, j, k in T.grid(1024, 1024, 1024):
        with T.block("C"):
            vi, vj, vk = T.axis.remap("SSR", [i, j, k])
            with T.init():
                C[vi, vj] = T.float16(0)
            C[vi, vj] += A[vi, vk] * B[vk, vj]

# 创建调度
sch = tvm.testing.mfma_schedule(
    workload=gemm,
    k_inner=16,
    in_dtype="float16", 
    b_transposed=False,
    i_factors=[4, 2, 16, 4, 4],
    j_factors=[4, 2, 16, 4, 4],
    k_factors=[64, 2, 8],
    index_map_A=lambda i, j: (i, j),
    index_map_B=lambda i, j: (i, j),
    index_map_C=lambda i, j: (i, j),
    ldmatrix_a_intrin=ldmatrix_a_intrin,
    ldmatrix_b_intrin=ldmatrix_b_intrin,
    mfma_intrin=mfma_intrin,
    mfma_fill_intrin=mfma_fill_intrin,
    mfma_store_intrin=mfma_store_intrin
)

# 构建和运行测试
mod = tvm.build(sch.mod, target="rocm")
```

## 注意事项

- 该函数主要针对AMD GPU的MFMA指令集优化，在其他平台可能无法正常工作
- 需要正确配置循环分割因子以确保线程块和warp的合理分配
- 输入数据类型必须与MFMA指令支持的数据类型匹配
- 张量化内在函数需要与目标硬件架构兼容
- 在使用前需要确保TVM编译时启用了ROCM后端支持

## 相关函数

- `tvm.tir.Schedule`：TVM的调度基础类
- `tvm.tir.schedule.BlockRV`：调度中的块引用
- `tvm.testing.gpu_verify`：GPU内核验证函数
- `tvm.testing.rocm`：ROCM平台特定的测试工具

---