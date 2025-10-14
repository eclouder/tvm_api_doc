---
title: mma_schedule
description: 为使用MMA（Matrix Multiply-Accumulate）内在函数的GEMM操作创建张量化调度
---

# mma_schedule

## 概述

`mma_schedule` 函数是TVM测试框架中的一个核心工具函数，专门用于为基于MMA（矩阵乘累加）内在函数的通用矩阵乘法（GEMM）操作生成高度优化的张量化调度。该函数主要应用于TVM的测试环境中，用于验证和评估不同硬件目标（特别是支持张量核心的GPU）上的GEMM性能。

在TVM测试流程中，该函数扮演着以下重要角色：
- 验证MMA内在函数在不同硬件平台上的正确性
- 测试TVM调度转换和张量化功能的完整性
- 为性能基准测试生成优化的计算内核
- 支持不同数据类型（int8, float16等）和矩阵布局的GEMM操作测试

## 函数签名

```python
def mma_schedule(workload, k_inner, in_dtype, b_transposed, i_factors, j_factors, k_factors, index_map_A, index_map_B, index_map_C, ldmatrix_a_intrin, ldmatrix_b_intrin, mma_intrin, mma_fill_intrin, mma_store_intrin, shared_scope='shared'):
```

## 参数

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| workload | TIR PrimFunc | 表示GEMM计算的工作负载 | 无 |
| k_inner | int | K维度的内层循环大小 | 无 |
| in_dtype | str | 输入数据类型（如"int8", "float16"） | 无 |
| b_transposed | bool | 矩阵B是否转置 | 无 |
| i_factors | List[int] | I维度的循环分割因子 | 无 |
| j_factors | List[int] | J维度的循环分割因子 | 无 |
| k_factors | List[int] | K维度的循环分割因子 | 无 |
| index_map_A | IndexMap | 矩阵A的布局变换映射 | 无 |
| index_map_B | IndexMap | 矩阵B的布局变换映射 | 无 |
| index_map_C | IndexMap | 矩阵C的布局变换映射 | 无 |
| ldmatrix_a_intrin | PrimExpr | 加载矩阵A的内在函数 | 无 |
| ldmatrix_b_intrin | PrimExpr | 加载矩阵B的内在函数 | 无 |
| mma_intrin | PrimExpr | MMA计算内在函数 | 无 |
| mma_fill_intrin | PrimExpr | 初始化累加器的内在函数 | 无 |
| mma_store_intrin | PrimExpr | 存储结果的内在函数 | 无 |
| shared_scope | str | 共享内存的作用域 | 'shared' |

## 返回值

**类型:** `tvm.tir.Schedule`

返回一个完整的TIR调度对象，该调度已经应用了针对MMA内在函数优化的各种变换，包括循环分割、重排序、绑定、缓存、存储对齐和张量化等。

## 使用场景

该函数主要应用于以下TVM测试场景：

### 单元测试
- 验证MMA调度转换的正确性
- 测试不同数据类型和矩阵布局的组合

### 性能测试
- 生成优化的GEMM内核进行性能基准测试
- 比较不同调度策略的性能差异

### 目标平台测试
- 针对NVIDIA GPU（支持Tensor Core）的测试
- 验证硬件特定内在函数的正确性

### 集成测试
- 测试端到端的GEMM工作流
- 验证调度与代码生成的集成

## 使用示例

```python
import tvm
from tvm.script import tir as T
from tvm.testing import mma_schedule

# 定义基础的GEMM工作负载
@T.prim_func
def gemm(
    A: T.Buffer((1024, 1024), "float16"),
    B: T.Buffer((1024, 1024), "float16"), 
    C: T.Buffer((1024, 1024), "float32"),
):
    for i, j, k in T.grid(1024, 1024, 1024):
        with T.block("C"):
            vi, vj, vk = T.axis.remap("SSR", [i, j, k])
            with T.init():
                C[vi, vj] = T.float32(0)
            C[vi, vj] += T.cast(A[vi, vk], "float32") * T.cast(B[vk, vj], "float32")

# 配置调度参数
k_inner = 16
in_dtype = "float16"
b_transposed = False
i_factors = [8, 4, 2, 16, 16]
j_factors = [8, 4, 2, 16, 16] 
k_factors = [64, 2, 8]

# 创建索引映射（简化示例）
def simple_index_map(i, j):
    return (i // 16, j // 16, i % 16, j % 16)

index_map_A = simple_index_map
index_map_B = simple_index_map  
index_map_C = simple_index_map

# 生成MMA调度
sch = mma_schedule(
    workload=gemm,
    k_inner=k_inner,
    in_dtype=in_dtype,
    b_transposed=b_transposed,
    i_factors=i_factors,
    j_factors=j_factors, 
    k_factors=k_factors,
    index_map_A=index_map_A,
    index_map_B=index_map_B,
    index_map_C=index_map_C,
    ldmatrix_a_intrin="wmma.load.a.sync",
    ldmatrix_b_intrin="wmma.load.b.sync", 
    mma_intrin="wmma.mma.sync",
    mma_fill_intrin="wmma.fill",
    mma_store_intrin="wmma.store.sync"
)

# 打印调度结果
print(sch.mod.script())
```

## 注意事项

- **硬件依赖**: 该函数生成的调度主要针对支持张量核心的NVIDIA GPU（Volta架构及以后）
- **数据类型限制**: 支持的数据类型包括int8、float16等，具体取决于目标硬件的能力
- **内存布局**: 矩阵B的转置状态会影响内存访问模式和张量化策略
- **循环因子**: 循环分割因子的选择会显著影响性能和资源利用率
- **TVM版本兼容**: 该函数依赖于TVM的TIR调度系统，需要TVM 0.8+版本

## 相关函数

- `tvm.tir.Schedule`: 基础的TIR调度类
- `tvm.tir.schedule.BlockRV`: 调度中的块表示
- `tvm.tir.schedule.LoopRV`: 调度中的循环表示
- 其他测试工具函数：如`verify_code`, `build_and_run`等用于验证生成的代码

---