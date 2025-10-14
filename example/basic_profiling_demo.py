#!/usr/bin/env python3
"""
TVM Profiling 基础演示
展示如何使用 TVM 的性能分析功能来测量模型和算子的执行时间
"""

import numpy as np
np.float_ = np.float64
import tvm
from tvm import te, tir, relax
from tvm.relax.testing import nn
from tvm.runtime import profiling
import time
import os


class TVMProfilingDemo:
    """TVM 性能分析演示类"""
    
    def __init__(self):
        """初始化演示环境"""
        self.target = tvm.target.Target("llvm")
        self.device = tvm.cpu(0)
        print(f"使用目标: {self.target}")
        print(f"使用设备: {self.device}")
    
    def demo_basic_tensor_operation(self):
        """演示基本张量操作的性能分析"""
        print("1. 基本张量操作性能分析")
        
        # 定义张量操作
        n = 1024
        A = te.placeholder((n,), name="A", dtype="float32")
        B = te.placeholder((n,), name="B", dtype="float32")
        C = te.compute(A.shape, lambda i: A[i] + B[i], name="C")
        
        # 构建函数
        func = tvm.build(te.create_prim_func([A, B, C]), target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(size=(n,)).astype("float32")
        b_np = np.random.uniform(size=(n,)).astype("float32")
        c_np = np.zeros((n,), dtype="float32")
        
        # 转换为 TVM 数组
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 性能测试
        evaluator = func.time_evaluator(func.entry_name, self.device, number=100)
        mean_time = evaluator(a_tvm, b_tvm, c_tvm).mean
        
        print(f"  向量加法 (大小: {n})")
        print(f"  平均执行时间: {mean_time * 1000:.4f} ms")
        print(f"  吞吐量: {n / mean_time / 1e6:.2f} M elements/s")
        print()
    
    def demo_matrix_multiplication(self):
        """演示矩阵乘法的性能分析"""
        print("2. 矩阵乘法性能分析")
        
        # 矩阵乘法参数
        M, K, N = 512, 512, 512
        
        # 定义矩阵乘法
        A = te.placeholder((M, K), name="A", dtype="float32")
        B = te.placeholder((K, N), name="B", dtype="float32")
        k = te.reduce_axis((0, K), name="k")
        C = te.compute((M, N), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k), name="C")
        
        # 构建函数
        func = tvm.build(te.create_prim_func([A, B, C]), target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(size=(M, K)).astype("float32")
        b_np = np.random.uniform(size=(K, N)).astype("float32")
        c_np = np.zeros((M, N), dtype="float32")
        
        # 转换为 TVM 数组
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 性能测试
        evaluator = func.time_evaluator(func.entry_name, self.device, number=10)
        mean_time = evaluator(a_tvm, b_tvm, c_tvm).mean
        
        # 计算 GFLOPS
        flops = 2 * M * K * N  # 矩阵乘法的浮点运算数
        gflops = flops / mean_time / 1e9
        
        print(f"  矩阵乘法 ({M}x{K} @ {K}x{N})")
        print(f"  平均执行时间: {mean_time * 1000:.4f} ms")
        print(f"  性能: {gflops:.2f} GFLOPS")
        print()
    
    def demo_neural_network_profiling(self):
        """演示神经网络层的性能分析"""
        print("\n3. 神经网络层性能分析")
        
        try:
            # 简化的神经网络演示，使用 TE 而不是 Relax
            batch_size = 32
            input_size = 784
            hidden_size = 256
            output_size = 10
            
            # 使用 TE 构建简单的线性层
            def linear_layer(input_data, weight, bias):
                k = te.reduce_axis((0, input_size), name="k")
                output = te.compute(
                    (batch_size, hidden_size),
                    lambda i, j: te.sum(input_data[i, k] * weight[k, j], axis=k) + bias[j],
                    name="linear"
                )
                return output
            
            # 创建输入张量
            input_data = te.placeholder((batch_size, input_size), name="input", dtype="float32")
            weight = te.placeholder((input_size, hidden_size), name="weight", dtype="float32")
            bias = te.placeholder((hidden_size,), name="bias", dtype="float32")
            
            # 构建计算图
            output = linear_layer(input_data, weight, bias)
            
            # 编译函数
            func = tvm.build(te.create_prim_func([input_data, weight, bias, output]), target=self.target)
            
            # 创建测试数据
            input_np = np.random.randn(batch_size, input_size).astype(np.float32)
            weight_np = np.random.randn(input_size, hidden_size).astype(np.float32)
            bias_np = np.random.randn(hidden_size).astype(np.float32)
            output_np = np.zeros((batch_size, hidden_size), dtype=np.float32)
            
            # 转换为 TVM 张量
            input_tvm = tvm.nd.array(input_np, device=self.device)
            weight_tvm = tvm.nd.array(weight_np, device=self.device)
            bias_tvm = tvm.nd.array(bias_np, device=self.device)
            output_tvm = tvm.nd.array(output_np, device=self.device)
            
            # 性能测试
            evaluator = func.time_evaluator(func.entry_name, self.device, number=100)
            time_cost = evaluator(input_tvm, weight_tvm, bias_tvm, output_tvm).mean
            
            print(f"  线性层执行时间: {time_cost * 1000:.4f} ms")
            print(f"  输入形状: {input_np.shape}")
            print(f"  权重形状: {weight_np.shape}")
            print(f"  输出形状: {output_np.shape}")
            
            # 计算 FLOPS
            flops = batch_size * input_size * hidden_size * 2  # 乘法和加法
            gflops = flops / (time_cost * 1e9)
            print(f"  计算性能: {gflops:.2f} GFLOPS")
            
        except Exception as e:
            print(f"  神经网络演示跳过 (需要 Relax 支持): {e}")
        
        try:
            # 创建简单的神经网络
            batch_size = 32
            input_size = 784
            hidden_size = 256
            output_size = 10
            
            # 使用 Relax 构建模型
            @tvm.script.ir_module
            class SimpleNN:
                @relax.function
                def main(x: relax.Tensor((batch_size, input_size), "float32"),
                        w1: relax.Tensor((input_size, hidden_size), "float32"),
                        b1: relax.Tensor((hidden_size,), "float32"),
                        w2: relax.Tensor((hidden_size, output_size), "float32"),
                        b2: relax.Tensor((output_size,), "float32")) -> relax.Tensor:
                    # 第一层
                    h1 = relax.nn.linear(x, w1, b1)
                    h1_relu = relax.nn.relu(h1)
                    
                    # 第二层
                    output = relax.nn.linear(h1_relu, w2, b2)
                    
                    return output
            
            # 编译模型
            target = tvm.target.Target("llvm")
            ex = relax.build(SimpleNN, target)
            vm = relax.VirtualMachine(ex, self.device, profile=True)
            
            # 准备数据
            x_np = np.random.randn(batch_size, input_size).astype("float32")
            w1_np = np.random.randn(input_size, hidden_size).astype("float32") * 0.1
            b1_np = np.zeros(hidden_size).astype("float32")
            w2_np = np.random.randn(hidden_size, output_size).astype("float32") * 0.1
            b2_np = np.zeros(output_size).astype("float32")
            
            # 转换为 TVM 数组
            x_tvm = tvm.nd.array(x_np, self.device)
            w1_tvm = tvm.nd.array(w1_np, self.device)
            b1_tvm = tvm.nd.array(b1_np, self.device)
            w2_tvm = tvm.nd.array(w2_np, self.device)
            b2_tvm = tvm.nd.array(b2_np, self.device)
            
            # 运行推理
            print("  运行神经网络推理...")
            for _ in range(5):  # 预热
                output = vm["main"](x_tvm, w1_tvm, b1_tvm, w2_tvm, b2_tvm)
            
            # 性能测试
            start_time = time.time()
            num_runs = 100
            for _ in range(num_runs):
                output = vm["main"](x_tvm, w1_tvm, b1_tvm, w2_tvm, b2_tvm)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / num_runs
            
            print(f"  神经网络推理 (batch_size: {batch_size})")
            print(f"  平均执行时间: {avg_time * 1000:.4f} ms")
            print(f"  吞吐量: {batch_size / avg_time:.2f} samples/s")
            
            # 获取详细的性能报告
            report = vm.profile()
            print("  详细性能报告:")
            print(report)
            
        except Exception as e:
            print(f"  神经网络演示跳过 (需要 Relax 支持): {e}")
        
        print()
    
    def demo_runtime_profiling(self):
        """演示运行时性能分析"""
        print("4. 运行时性能分析")
        
        # 创建简单的计算
        n = 1024
        A = te.placeholder((n,), name="A", dtype="float32")
        B = te.compute(A.shape, lambda i: A[i] * A[i] + 1.0, name="B")
        
        # 构建函数
        func = tvm.build(te.create_prim_func([A, B]), target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(size=(n,)).astype("float32")
        b_np = np.zeros((n,), dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        
        # 使用 profiling 模块
        with profiling.profile_function(func, self.device) as prof:
            func(a_tvm, b_tvm)
        
        print("  运行时性能分析结果:")
        print(f"  执行时间: {prof.mean * 1000:.4f} ms")
        print()
    
    def demo_comparative_analysis(self):
        """演示不同实现的性能对比"""
        print("5. 性能对比分析")
        
        n = 1024
        
        # 实现1: 简单的元素级操作
        A1 = te.placeholder((n,), name="A1", dtype="float32")
        B1 = te.placeholder((n,), name="B1", dtype="float32")
        C1 = te.compute(A1.shape, lambda i: A1[i] + B1[i], name="C1")
        func1 = tvm.build(te.create_prim_func([A1, B1, C1]), target=self.target)
        
        # 实现2: 向量化操作
        A2 = te.placeholder((n,), name="A2", dtype="float32")
        B2 = te.placeholder((n,), name="B2", dtype="float32")
        C2 = te.compute(A2.shape, lambda i: A2[i] + B2[i], name="C2")
        
        # 添加向量化调度
        s = te.create_schedule(C2.op)
        s[C2].vectorize(C2.op.axis[0])
        func2 = tvm.build(s, [A2, B2, C2], target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(size=(n,)).astype("float32")
        b_np = np.random.uniform(size=(n,)).astype("float32")
        c_np = np.zeros((n,), dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 性能测试
        evaluator1 = func1.time_evaluator(func1.entry_name, self.device, number=100)
        time1 = evaluator1(a_tvm, b_tvm, c_tvm).mean
        
        evaluator2 = func2.time_evaluator(func2.entry_name, self.device, number=100)
        time2 = evaluator2(a_tvm, b_tvm, c_tvm).mean
        
        print(f"  简单实现: {time1 * 1000:.4f} ms")
        print(f"  向量化实现: {time2 * 1000:.4f} ms")
        print(f"  加速比: {time1 / time2:.2f}x")
        print()
    
    def demo_memory_profiling(self):
        """演示内存使用分析"""
        print("6. 内存使用分析")
        
        # 创建大型矩阵操作
        M, N = 1024, 1024
        A = te.placeholder((M, N), name="A", dtype="float32")
        B = te.compute(A.shape, lambda i, j: A[i, j] * 2.0, name="B")
        
        # 构建函数
        func = tvm.build(te.create_prim_func([A, B]), target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(size=(M, N)).astype("float32")
        b_np = np.zeros((M, N), dtype="float32")
        
        # 计算内存使用
        input_memory = a_np.nbytes
        output_memory = b_np.nbytes
        total_memory = input_memory + output_memory
        
        print(f"  矩阵大小: {M} x {N}")
        print(f"  输入内存: {input_memory / 1024 / 1024:.2f} MB")
        print(f"  输出内存: {output_memory / 1024 / 1024:.2f} MB")
        print(f"  总内存: {total_memory / 1024 / 1024:.2f} MB")
        
        # 性能测试
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        
        evaluator = func.time_evaluator(func.entry_name, self.device, number=10)
        mean_time = evaluator(a_tvm, b_tvm).mean
        
        # 计算内存带宽
        memory_bandwidth = total_memory / mean_time / 1024 / 1024 / 1024  # GB/s
        
        print(f"  执行时间: {mean_time * 1000:.4f} ms")
        print(f"  内存带宽: {memory_bandwidth:.2f} GB/s")
        print()
    
    def run_all_demos(self):
        """运行所有演示"""
        print("TVM 基础性能分析演示")
        print("=" * 50)
        
        try:
            self.demo_basic_tensor_operation()
            self.demo_matrix_multiplication()
            self.demo_neural_network_profiling()
            self.demo_runtime_profiling()
            self.demo_comparative_analysis()
            self.demo_memory_profiling()
            
            print("所有演示完成！")
            
        except Exception as e:
            print(f"演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    demo = TVMProfilingDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()