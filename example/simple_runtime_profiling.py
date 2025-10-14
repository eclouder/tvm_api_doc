#!/usr/bin/env python3
"""
TVM Runtime Profiling 简单使用例子
展示 tvm.runtime.profiling 模块的基本用法
"""

import numpy as np
import tvm
from tvm import te
from tvm.runtime import profiling
import time


class SimpleRuntimeProfilingDemo:
    """简单的 TVM Runtime Profiling 演示"""
    
    def __init__(self):
        """初始化"""
        self.target = tvm.target.Target("llvm")
        self.device = tvm.cpu(0)
        print(f"目标平台: {self.target}")
        print(f"执行设备: {self.device}")
        print("-" * 50)
    
    def example_1_basic_profiling(self):
        """例子1: 基本的性能分析"""
        print("例子1: 基本的性能分析")
        
        # 创建简单的向量加法
        n = 10000
        A = te.placeholder((n,), name="A", dtype="float32")
        B = te.placeholder((n,), name="B", dtype="float32")
        C = te.compute(A.shape, lambda i: A[i] + B[i], name="C")
        
        # 编译函数
        func = tvm.build(te.create_prim_func([A, B, C]), target=self.target)
        
        # 准备数据
        a_np = np.random.randn(n).astype("float32")
        b_np = np.random.randn(n).astype("float32")
        c_np = np.zeros(n, dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 方法1: 使用 profile_function (需要 collectors 参数)
        print("  方法1: 使用 profile_function")
        try:
            # 创建一个空的 collectors 列表，因为我们只是想要基本的性能分析
            collectors = []
            prof_func = profiling.profile_function(func, self.device, collectors)
            result = prof_func(a_tvm, b_tvm, c_tvm)
            print(f"    profile_function 执行完成")
            if result:
                print(f"    收集到的指标: {result}")
        except Exception as e:
            print(f"    profile_function 跳过 (需要特定的 collectors): {e}")
        
        # 方法2: 使用 time_evaluator (更常用和简单)
        print("  方法2: 使用 time_evaluator")
        evaluator = func.time_evaluator(func.entry_name, self.device, number=100)
        time_cost = evaluator(a_tvm, b_tvm, c_tvm)
        print(f"    平均执行时间: {time_cost.mean * 1000:.4f} ms")
        print(f"    最小执行时间: {time_cost.min * 1000:.4f} ms")
        print(f"    最大执行时间: {time_cost.max * 1000:.4f} ms")
        print()
    
    def example_2_detailed_profiling(self):
        """例子2: 详细的性能分析报告"""
        print("例子2: 详细的性能分析报告")
        
        # 创建矩阵乘法
        M, N, K = 512, 512, 512
        A = te.placeholder((M, K), name="A", dtype="float32")
        B = te.placeholder((K, N), name="B", dtype="float32")
        
        k = te.reduce_axis((0, K), name="k")
        C = te.compute((M, N), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k), name="C")
        
        func = tvm.build(te.create_prim_func([A, B, C]), target=self.target)
        
        # 准备数据
        a_np = np.random.randn(M, K).astype("float32")
        b_np = np.random.randn(K, N).astype("float32")
        c_np = np.zeros((M, N), dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 使用 profiling 获取详细报告
        print("  执行矩阵乘法性能分析...")
        evaluator = func.time_evaluator(func.entry_name, self.device, number=10, repeat=3)
        results = evaluator(a_tvm, b_tvm, c_tvm)
        
        print(f"    矩阵大小: {M}x{K} × {K}x{N} = {M}x{N}")
        print(f"    平均执行时间: {results.mean * 1000:.4f} ms")
        print(f"    标准差: {results.std * 1000:.4f} ms")
        
        # 计算 GFLOPS
        flops = 2 * M * N * K  # 矩阵乘法的浮点运算次数
        gflops = flops / (results.mean * 1e9)
        print(f"    计算性能: {gflops:.2f} GFLOPS")
        print()
    
    def example_3_profiling_with_warmup(self):
        """例子3: 带预热的性能分析"""
        print("例子3: 带预热的性能分析")
        
        # 创建复杂一点的计算
        n = 50000
        A = te.placeholder((n,), name="A", dtype="float32")
        B = te.compute(A.shape, lambda i: A[i] * A[i] + tvm.tir.sqrt(A[i]) + 1.0, name="B")
        
        func = tvm.build(te.create_prim_func([A, B]), target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(1.0, 10.0, size=(n,)).astype("float32")
        b_np = np.zeros(n, dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        
        # 预热运行
        print("  预热运行...")
        for _ in range(5):
            func(a_tvm, b_tvm)
        
        # 正式性能测试
        print("  正式性能测试...")
        evaluator = func.time_evaluator(func.entry_name, self.device, 
                                      number=50, repeat=5, min_repeat_ms=100)
        results = evaluator(a_tvm, b_tvm)
        
        print(f"    数据大小: {n} 个元素")
        print(f"    平均执行时间: {results.mean * 1000:.4f} ms")
        print(f"    最佳执行时间: {results.min * 1000:.4f} ms")
        print(f"    最差执行时间: {results.max * 1000:.4f} ms")
        print(f"    标准差: {results.std * 1000:.4f} ms")
        print()
    
    def example_4_compare_implementations(self):
        """例子4: 比较不同实现的性能"""
        print("例子4: 比较不同实现的性能")
        
        n = 100000
        
        # 实现1: 简单的逐元素操作
        A1 = te.placeholder((n,), name="A1", dtype="float32")
        B1 = te.placeholder((n,), name="B1", dtype="float32")
        C1 = te.compute(A1.shape, lambda i: A1[i] + B1[i], name="C1")
        func1 = tvm.build(te.create_prim_func([A1, B1, C1]), target=self.target)
        
        # 实现2: 带调度优化的版本
        A2 = te.placeholder((n,), name="A2", dtype="float32")
        B2 = te.placeholder((n,), name="B2", dtype="float32")
        C2 = te.compute(A2.shape, lambda i: A2[i] + B2[i], name="C2")
        
        # 创建调度并尝试向量化
        s = te.create_schedule(C2.op)
        try:
            # 尝试向量化（如果支持的话）
            s[C2].vectorize(C2.op.axis[0])
            func2 = tvm.build(s, [A2, B2, C2], target=self.target)
            vectorized = True
        except:
            # 如果向量化失败，使用原始版本
            func2 = tvm.build(te.create_prim_func([A2, B2, C2]), target=self.target)
            vectorized = False
        
        # 准备数据
        a_np = np.random.randn(n).astype("float32")
        b_np = np.random.randn(n).astype("float32")
        c_np = np.zeros(n, dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 测试实现1
        evaluator1 = func1.time_evaluator(func1.entry_name, self.device, number=100)
        time1 = evaluator1(a_tvm, b_tvm, c_tvm)
        
        # 测试实现2
        evaluator2 = func2.time_evaluator(func2.entry_name, self.device, number=100)
        time2 = evaluator2(a_tvm, b_tvm, c_tvm)
        
        print(f"  数据大小: {n} 个元素")
        print(f"  实现1 (基础版本): {time1.mean * 1000:.4f} ms")
        print(f"  实现2 ({'向量化' if vectorized else '基础'}版本): {time2.mean * 1000:.4f} ms")
        
        if time1.mean > time2.mean:
            speedup = time1.mean / time2.mean
            print(f"  实现2 比实现1 快 {speedup:.2f}x")
        else:
            slowdown = time2.mean / time1.mean
            print(f"  实现1 比实现2 快 {slowdown:.2f}x")
        print()
    
    def example_5_profiling_report(self):
        """例子5: 生成性能分析报告"""
        print("例子5: 生成性能分析报告")
        
        # 创建多个不同的操作
        operations = []
        
        # 操作1: 向量加法
        n = 10000
        A = te.placeholder((n,), name="A", dtype="float32")
        B = te.placeholder((n,), name="B", dtype="float32")
        C = te.compute(A.shape, lambda i: A[i] + B[i], name="VecAdd")
        operations.append(("向量加法", tvm.build(te.create_prim_func([A, B, C]), target=self.target)))
        
        # 操作2: 向量乘法
        D = te.compute(A.shape, lambda i: A[i] * B[i], name="VecMul")
        operations.append(("向量乘法", tvm.build(te.create_prim_func([A, B, D]), target=self.target)))
        
        # 操作3: 向量平方根
        E = te.compute(A.shape, lambda i: tvm.tir.sqrt(A[i]), name="VecSqrt")
        operations.append(("向量平方根", tvm.build(te.create_prim_func([A, E]), target=self.target)))
        
        # 准备数据
        a_np = np.random.uniform(1.0, 10.0, size=(n,)).astype("float32")
        b_np = np.random.uniform(1.0, 10.0, size=(n,)).astype("float32")
        out_np = np.zeros(n, dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        out_tvm = tvm.nd.array(out_np, self.device)
        
        print("  性能分析报告:")
        print("  " + "="*60)
        print(f"  {'操作名称':<15} {'平均时间(ms)':<15} {'吞吐量(GB/s)':<15}")
        print("  " + "-"*60)
        
        for name, func in operations:
            if name == "向量平方根":
                # 只需要一个输入
                evaluator = func.time_evaluator(func.entry_name, self.device, number=100)
                time_cost = evaluator(a_tvm, out_tvm)
                data_size = n * 4 * 2  # 输入和输出，每个float32是4字节
            else:
                # 需要两个输入
                evaluator = func.time_evaluator(func.entry_name, self.device, number=100)
                time_cost = evaluator(a_tvm, b_tvm, out_tvm)
                data_size = n * 4 * 3  # 两个输入一个输出
            
            throughput = (data_size / (time_cost.mean * 1e9))  # GB/s
            print(f"  {name:<15} {time_cost.mean * 1000:<15.4f} {throughput:<15.2f}")
        
        print("  " + "="*60)
        print()
    
    def run_all_examples(self):
        """运行所有例子"""
        print("TVM Runtime Profiling 使用例子")
        print("="*50)
        
        self.example_1_basic_profiling()
        self.example_2_detailed_profiling()
        self.example_3_profiling_with_warmup()
        self.example_4_compare_implementations()
        self.example_5_profiling_report()
        
        print("所有例子运行完成！")


def main():
    """主函数"""
    demo = SimpleRuntimeProfilingDemo()
    demo.run_all_examples()


if __name__ == "__main__":
    main()