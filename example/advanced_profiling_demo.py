#!/usr/bin/env python3
"""
TVM 高级性能分析演示
展示更复杂的性能分析场景，包括优化前后对比、不同调度策略的性能分析等
"""

import numpy as np
import tvm
from tvm import te, tir, auto_scheduler, meta_schedule
from tvm.runtime import profiling
import time
import json


class AdvancedProfilingDemo:
    """高级性能分析演示类"""
    
    def __init__(self):
        self.device = tvm.cpu()
        self.target = "llvm"
        
        # 检查 CUDA 支持
        if tvm.cuda().exist:
            try:
                self.cuda_device = tvm.cuda()
                self.cuda_target = "cuda"
                print("检测到 CUDA 支持")
            except:
                self.cuda_device = None
                self.cuda_target = None
        else:
            self.cuda_device = None
            self.cuda_target = None

    def demo_schedule_optimization_comparison(self):
        """演示调度优化前后的性能对比"""
        print("1. 调度优化性能对比")
        
        M, K, N = 1024, 1024, 1024
        
        def create_matmul_original():
            """创建原始矩阵乘法"""
            A = te.placeholder((M, K), name="A", dtype="float32")
            B = te.placeholder((K, N), name="B", dtype="float32")
            k = te.reduce_axis((0, K), name="k")
            C = te.compute((M, N), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k), name="C")
            return te.create_prim_func([A, B, C])
        
        def create_matmul_optimized():
            """创建优化的矩阵乘法（分块）"""
            A = te.placeholder((M, K), name="A", dtype="float32")
            B = te.placeholder((K, N), name="B", dtype="float32")
            k = te.reduce_axis((0, K), name="k")
            C = te.compute((M, N), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k), name="C")
            
            # 创建调度并应用分块优化
            s = te.create_schedule(C.op)
            
            # 分块优化
            block_size = 32
            xo, yo, xi, yi = s[C].tile(C.op.axis[0], C.op.axis[1], block_size, block_size)
            ko, ki = s[C].split(k, factor=4)
            s[C].reorder(xo, yo, ko, xi, yi, ki)
            
            return tvm.lower(s, [A, B, C], simple_mode=True)
        
        # 构建函数 - 修复：使用 tvm.build 而不是 tvm.tir.build
        func_orig = tvm.build(create_matmul_original(), target=self.target)
        try:
            func_opt = tvm.build(create_matmul_optimized(), target=self.target)
        except:
            print("  优化版本构建失败，使用原始版本进行对比")
            func_opt = func_orig
        
        # 准备数据
        a_np = np.random.uniform(size=(M, K)).astype("float32")
        b_np = np.random.uniform(size=(K, N)).astype("float32")
        c_np = np.zeros((M, N), dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 性能测试
        evaluator_orig = func_orig.time_evaluator(func_orig.entry_name, self.device, number=5)
        evaluator_opt = func_opt.time_evaluator(func_opt.entry_name, self.device, number=5)
        
        time_orig = evaluator_orig(a_tvm, b_tvm, c_tvm).mean
        time_opt = evaluator_opt(a_tvm, b_tvm, c_tvm).mean
        
        # 计算 GFLOPS
        flops = 2 * M * K * N
        gflops_orig = flops / time_orig / 1e9
        gflops_opt = flops / time_opt / 1e9
        
        print(f"  矩阵乘法 ({M}x{K} @ {K}x{N})")
        print(f"  原始实现: {time_orig*1000:.2f} ms, {gflops_orig:.2f} GFLOPS")
        print(f"  优化实现: {time_opt*1000:.2f} ms, {gflops_opt:.2f} GFLOPS")
        print(f"  加速比: {time_orig/time_opt:.2f}x")
        print()

    def demo_operator_profiling(self):
        """演示算子级别的性能分析"""
        print("2. 算子级别性能分析")
        
        # 卷积操作参数
        batch, in_channel, in_height, in_width = 1, 64, 56, 56
        out_channel, kernel_h, kernel_w = 64, 3, 3
        pad_h, pad_w = 1, 1
        stride_h, stride_w = 1, 1
        
        def create_conv2d():
            """创建卷积操作"""
            Input = te.placeholder((batch, in_channel, in_height, in_width), name="Input", dtype="float32")
            Filter = te.placeholder((out_channel, in_channel, kernel_h, kernel_w), name="Filter", dtype="float32")
            
            # 计算输出尺寸
            out_height = (in_height + 2 * pad_h - kernel_h) // stride_h + 1
            out_width = (in_width + 2 * pad_w - kernel_w) // stride_w + 1
            
            # 定义卷积计算
            rc = te.reduce_axis((0, in_channel), name="rc")
            ry = te.reduce_axis((0, kernel_h), name="ry")
            rx = te.reduce_axis((0, kernel_w), name="rx")
            
            Output = te.compute(
                (batch, out_channel, out_height, out_width),
                lambda n, f, y, x: te.sum(
                    Input[n, rc, y * stride_h + ry - pad_h, x * stride_w + rx - pad_w] * 
                    Filter[f, rc, ry, rx],
                    axis=[rc, ry, rx]
                ),
                name="Output"
            )
            
            return te.create_prim_func([Input, Filter, Output])
        
        try:
            # 构建函数 - 修复：使用 tvm.build 而不是 tvm.tir.build
            func = tvm.build(create_conv2d(), target=self.target)
            
            # 准备数据
            input_np = np.random.uniform(size=(batch, in_channel, in_height, in_width)).astype("float32")
            filter_np = np.random.uniform(size=(out_channel, in_channel, kernel_h, kernel_w)).astype("float32")
            
            out_height = (in_height + 2 * pad_h - kernel_h) // stride_h + 1
            out_width = (in_width + 2 * pad_w - kernel_w) // stride_w + 1
            output_np = np.zeros((batch, out_channel, out_height, out_width), dtype="float32")
            
            input_tvm = tvm.nd.array(input_np, self.device)
            filter_tvm = tvm.nd.array(filter_np, self.device)
            output_tvm = tvm.nd.array(output_np, self.device)
            
            # 性能测试
            evaluator = func.time_evaluator(func.entry_name, self.device, number=10)
            mean_time = evaluator(input_tvm, filter_tvm, output_tvm).mean
            
            # 计算 GFLOPS
            flops = batch * out_channel * out_height * out_width * in_channel * kernel_h * kernel_w * 2
            gflops = flops / mean_time / 1e9
            
            print(f"  Conv2D ({batch}x{in_channel}x{in_height}x{in_width} -> {batch}x{out_channel}x{out_height}x{out_width})")
            print(f"  卷积核: {kernel_h}x{kernel_w}, 填充: {pad_h}x{pad_w}, 步长: {stride_h}x{stride_w}")
            print(f"  执行时间: {mean_time*1000:.2f} ms")
            print(f"  性能: {gflops:.2f} GFLOPS")
            
        except Exception as e:
            print(f"  卷积操作分析遇到问题: {e}")
            print("  跳过此演示...")
        
        print()

    def demo_memory_access_pattern_analysis(self):
        """演示内存访问模式分析"""
        print("3. 内存访问模式分析")
        
        sizes = [1024, 2048, 4096]
        
        for size in sizes:
            # 顺序访问
            A = te.placeholder((size, size), name="A", dtype="float32")
            B = te.compute((size, size), lambda i, j: A[i, j] + 1.0, name="B")
            
            # 构建函数 - 修复：使用 tvm.build 而不是 tvm.tir.build
            func = tvm.build(te.create_prim_func([A, B]), target=self.target)
            
            # 准备数据
            a_np = np.random.uniform(size=(size, size)).astype("float32")
            b_np = np.zeros((size, size), dtype="float32")
            
            a_tvm = tvm.nd.array(a_np, self.device)
            b_tvm = tvm.nd.array(b_np, self.device)
            
            # 性能测试
            evaluator = func.time_evaluator(func.entry_name, self.device, number=20)
            mean_time = evaluator(a_tvm, b_tvm).mean
            
            # 计算带宽
            memory_bytes = size * size * 4 * 2  # 读A + 写B
            bandwidth = memory_bytes / mean_time / 1e9  # GB/s
            
            print(f"  矩阵大小: {size}x{size}")
            print(f"  内存使用: {memory_bytes/1024/1024:.1f} MB")
            print(f"  执行时间: {mean_time*1000:.2f} ms")
            print(f"  内存带宽: {bandwidth:.2f} GB/s")
            print()

    def demo_profiling_with_different_targets(self):
        """演示不同目标平台的性能对比"""
        print("4. 不同目标平台性能对比")
        
        # 定义简单的矩阵乘法
        M, K, N = 512, 512, 512
        
        def create_matmul():
            A = te.placeholder((M, K), name="A", dtype="float32")
            B = te.placeholder((K, N), name="B", dtype="float32")
            k = te.reduce_axis((0, K), name="k")
            C = te.compute((M, N), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k), name="C")
            return te.create_prim_func([A, B, C])
        
        prim_func = create_matmul()
        
        # 测试不同目标
        targets = [
            ("llvm", tvm.cpu()),
            ("llvm -mcpu=core-avx2", tvm.cpu()),
        ]
        
        if self.cuda_device:
            targets.append(("cuda", self.cuda_device))
        
        # 准备数据
        a_np = np.random.uniform(size=(M, K)).astype("float32")
        b_np = np.random.uniform(size=(K, N)).astype("float32")
        c_np = np.zeros((M, N), dtype="float32")
        
        results = []
        
        for target_str, device in targets:
            try:
                # 构建函数 - 修复：使用 tvm.build 而不是 tvm.tir.build
                func = tvm.build(prim_func, target=target)
                
                # 转换数据到对应设备
                a_tvm = tvm.nd.array(a_np, device)
                b_tvm = tvm.nd.array(b_np, device)
                c_tvm = tvm.nd.array(c_np, device)
                
                # 性能测试
                evaluator = func.time_evaluator(func.entry_name, device, number=10)
                mean_time = evaluator(a_tvm, b_tvm, c_tvm).mean
                
                # 计算 GFLOPS
                flops = 2 * M * K * N
                gflops = flops / mean_time / 1e9
                
                results.append((target_str, mean_time, gflops))
                
            except Exception as e:
                print(f"  目标 {target_str} 测试失败: {e}")
        
        # 显示结果
        print(f"  矩阵乘法 ({M}x{K} @ {K}x{N}) 性能对比:")
        for target_str, time_val, gflops in results:
            print(f"    {target_str:20s}: {time_val*1000:6.2f} ms, {gflops:6.2f} GFLOPS")
        
        print()

    def demo_profiling_report_generation(self):
        """演示性能分析报告生成"""
        print("5. 性能分析报告生成")
        
        # 定义测试函数
        n = 2048
        A = te.placeholder((n,), name="A", dtype="float32")
        B = te.placeholder((n,), name="B", dtype="float32")
        C = te.compute(A.shape, lambda i: A[i] * B[i] + A[i] * 0.5, name="C")
        
        # 构建函数 - 修复：使用 tvm.build 而不是 tvm.tir.build
        func = tvm.build(te.create_prim_func([A, B, C]), target=self.target)
        
        # 准备数据
        a_np = np.random.uniform(size=(n,)).astype("float32")
        b_np = np.random.uniform(size=(n,)).astype("float32")
        c_np = np.zeros((n,), dtype="float32")
        
        a_tvm = tvm.nd.array(a_np, self.device)
        b_tvm = tvm.nd.array(b_np, self.device)
        c_tvm = tvm.nd.array(c_np, self.device)
        
        # 生成详细的性能报告
        report_data = {
            "function_name": "vector_multiply_add",
            "input_size": n,
            "data_type": "float32",
            "target": self.target,
            "measurements": []
        }
        
        # 多次测量
        num_measurements = 10
        for i in range(num_measurements):
            evaluator = func.time_evaluator(func.entry_name, self.device, number=1)
            exec_time = evaluator(a_tvm, b_tvm, c_tvm).mean
            
            report_data["measurements"].append({
                "run": i + 1,
                "execution_time_ms": exec_time * 1000,
                "throughput_elements_per_sec": n / exec_time
            })
        
        # 计算统计信息
        times = [m["execution_time_ms"] for m in report_data["measurements"]]
        report_data["statistics"] = {
            "mean_time_ms": np.mean(times),
            "std_time_ms": np.std(times),
            "min_time_ms": np.min(times),
            "max_time_ms": np.max(times),
            "cv_percent": (np.std(times) / np.mean(times)) * 100
        }
        
        # 显示报告
        print("  性能分析报告:")
        print(f"    函数: {report_data['function_name']}")
        print(f"    输入大小: {report_data['input_size']}")
        print(f"    数据类型: {report_data['data_type']}")
        print(f"    目标平台: {report_data['target']}")
        print("  统计信息:")
        stats = report_data["statistics"]
        print(f"    平均时间: {stats['mean_time_ms']:.4f} ± {stats['std_time_ms']:.4f} ms")
        print(f"    时间范围: {stats['min_time_ms']:.4f} - {stats['max_time_ms']:.4f} ms")
        print(f"    变异系数: {stats['cv_percent']:.2f}%")
        
        # 保存报告到文件
        try:
            with open("profiling_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            print("    报告已保存到: profiling_report.json")
        except Exception as e:
            print(f"    保存报告失败: {e}")
        
        print()

    def run_all_demos(self):
        """运行所有演示"""
        print("=" * 60)
        print("TVM 高级性能分析演示")
        print("=" * 60)
        
        try:
            self.demo_schedule_optimization_comparison()
            self.demo_operator_profiling()
            self.demo_memory_access_pattern_analysis()
            self.demo_profiling_with_different_targets()
            self.demo_profiling_report_generation()
            
            print("=" * 60)
            print("所有高级演示完成！")
            print("=" * 60)
            
        except Exception as e:
            print(f"演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    demo = AdvancedProfilingDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()