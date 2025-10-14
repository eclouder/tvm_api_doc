#!/usr/bin/env python3
"""
TVM Relax 虚拟机性能分析演示
基于 TVM 测试文件中的示例，展示如何使用 Relax VM 进行性能分析
"""

import numpy as np
import tvm
from tvm import relax
from tvm.relax.testing import nn
from tvm.script import relax as R
import json


class RelaxVMProfilingDemo:
    """Relax VM 性能分析演示类"""
    
    def __init__(self):
        self.device = tvm.cpu()
        self.target = "llvm"
        print(f"Relax VM Profiling Demo 初始化")
        print(f"目标设备: {self.target}")
        print("-" * 50)
    
    def create_mlp_model(self, input_shape, hidden_sizes, output_size):
        """创建多层感知机模型"""
        builder = relax.BlockBuilder()
        
        # 生成权重参数
        weights = {}
        layer_sizes = [input_shape[1]] + hidden_sizes + [output_size]
        
        for i in range(len(layer_sizes) - 1):
            weight_name = f"linear_weight_{i}"
            bias_name = f"linear_bias_{i}"
            
            weights[weight_name] = np.random.randn(layer_sizes[i+1], layer_sizes[i]).astype("float32")
            weights[bias_name] = np.random.randn(layer_sizes[i+1]).astype("float32")
        
        with builder.function("main"):
            # 创建模型层
            layers = []
            for i, hidden_size in enumerate(hidden_sizes):
                if i == 0:
                    layers.append(nn.Linear(input_shape[1], hidden_size, bias=True))
                else:
                    layers.append(nn.Linear(hidden_sizes[i-1], hidden_size, bias=True))
                layers.append(nn.ReLU())
            
            # 输出层
            if hidden_sizes:
                layers.append(nn.Linear(hidden_sizes[-1], output_size, bias=True))
            else:
                layers.append(nn.Linear(input_shape[1], output_size, bias=True))
            
            model = nn.Sequential(*layers)
            data = nn.Placeholder(input_shape, name="data")
            output = model(data)
            params = [data] + model.parameters()
            builder.emit_func_output(output, params=params)
        
        mod = builder.get()
        
        # 绑定参数
        try:
            mod = relax.transform.BindParams("main", weights)(mod)
        except:
            print("参数绑定失败，使用默认参数")
        
        return mod
    
    def demo_basic_mlp_profiling(self):
        """演示基础 MLP 模型性能分析"""
        print("1. 基础 MLP 模型性能分析")
        
        try:
            # 创建简单的 MLP 模型
            input_shape = (1, 784)
            hidden_sizes = [256, 128]
            output_size = 10
            
            mod = self.create_mlp_model(input_shape, hidden_sizes, output_size)
            
            # 编译模型
            ex = tvm.compile(mod, target=self.target)
            
            # 创建启用性能分析的虚拟机
            vm = relax.VirtualMachine(ex, self.device, profile=True)
            
            # 准备输入数据
            data_np = np.random.randn(*input_shape).astype("float32")
            data_tensor = tvm.runtime.tensor(data_np, self.device)
            
            # 执行性能分析
            print("执行模型推理并收集性能数据...")
            report = vm.profile("main", data_tensor)
            
            print("MLP 模型性能分析报告:")
            print(report)
            print()
            
            # 多次执行以获得稳定的性能数据
            print("执行多次推理以获得平均性能:")
            times = []
            for i in range(10):
                start_time = tvm.runtime.time_evaluator(lambda: vm["main"](data_tensor), self.device, number=1, repeat=1)()
                times.append(start_time.mean * 1000)  # 转换为毫秒
            
            avg_time = np.mean(times)
            std_time = np.std(times)
            
            print(f"平均推理时间: {avg_time:.4f} ms")
            print(f"标准差: {std_time:.4f} ms")
            print(f"最小时间: {np.min(times):.4f} ms")
            print(f"最大时间: {np.max(times):.4f} ms")
            print()
            
        except Exception as e:
            print(f"MLP 性能分析失败: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    def demo_different_model_sizes(self):
        """演示不同模型大小的性能对比"""
        print("2. 不同模型大小性能对比")
        
        model_configs = [
            ("小模型", (1, 128), [64], 10),
            ("中模型", (1, 512), [256, 128], 10),
            ("大模型", (1, 1024), [512, 256, 128], 10)
        ]
        
        results = {}
        
        for name, input_shape, hidden_sizes, output_size in model_configs:
            try:
                print(f"测试 {name}...")
                
                mod = self.create_mlp_model(input_shape, hidden_sizes, output_size)
                ex = tvm.compile(mod, target=self.target)
                vm = relax.VirtualMachine(ex, self.device, profile=True)
                
                # 准备数据
                data_np = np.random.randn(*input_shape).astype("float32")
                data_tensor = tvm.runtime.tensor(data_np, self.device)
                
                # 性能测试
                times = []
                for _ in range(5):
                    start = tvm.runtime.time_evaluator(lambda: vm["main"](data_tensor), self.device, number=1, repeat=1)()
                    times.append(start.mean * 1000)
                
                avg_time = np.mean(times)
                
                # 计算模型参数数量
                total_params = 0
                layer_sizes = [input_shape[1]] + hidden_sizes + [output_size]
                for i in range(len(layer_sizes) - 1):
                    total_params += layer_sizes[i] * layer_sizes[i+1] + layer_sizes[i+1]  # 权重 + 偏置
                
                results[name] = {
                    "avg_time_ms": avg_time,
                    "total_params": total_params,
                    "input_shape": input_shape,
                    "hidden_sizes": hidden_sizes,
                    "output_size": output_size
                }
                
                print(f"  平均时间: {avg_time:.4f} ms")
                print(f"  参数数量: {total_params:,}")
                print()
                
            except Exception as e:
                print(f"  {name} 测试失败: {e}")
                results[name] = {"error": str(e)}
                print()
        
        # 性能对比总结
        print("模型大小性能对比总结:")
        print(f"{'模型':<10} {'时间(ms)':<12} {'参数数量':<12} {'每参数时间(ns)':<15}")
        print("-" * 55)
        
        for name, data in results.items():
            if "error" not in data:
                time_per_param = (data["avg_time_ms"] * 1e6) / data["total_params"]  # ns per parameter
                print(f"{name:<10} {data['avg_time_ms']:<12.4f} {data['total_params']:<12,} {time_per_param:<15.2f}")
            else:
                print(f"{name:<10} {'错误':<12} {'N/A':<12} {'N/A':<15}")
        print()
    
    def demo_layer_wise_profiling(self):
        """演示逐层性能分析"""
        print("3. 逐层性能分析")
        
        # 创建一个可以逐层分析的模型
        @tvm.script.ir_module
        class LayerWiseModel:
            @R.function
            def main(x: R.Tensor((1, 128), "float32")) -> R.Tensor((1, 10), "float32"):
                with R.dataflow():
                    # 第一层
                    w1 = R.const(np.random.randn(256, 128).astype("float32"))
                    b1 = R.const(np.random.randn(256).astype("float32"))
                    h1 = R.nn.dense(x, w1, b1)
                    a1 = R.nn.relu(h1)
                    
                    # 第二层
                    w2 = R.const(np.random.randn(128, 256).astype("float32"))
                    b2 = R.const(np.random.randn(128).astype("float32"))
                    h2 = R.nn.dense(a1, w2, b2)
                    a2 = R.nn.relu(h2)
                    
                    # 输出层
                    w3 = R.const(np.random.randn(10, 128).astype("float32"))
                    b3 = R.const(np.random.randn(10).astype("float32"))
                    output = R.nn.dense(a2, w3, b3)
                    
                    R.output(output)
                return output
        
        try:
            # 编译模型
            ex = tvm.compile(LayerWiseModel, target=self.target)
            vm = relax.VirtualMachine(ex, self.device, profile=True)
            
            # 准备数据
            data_np = np.random.randn(1, 128).astype("float32")
            data_tensor = tvm.runtime.tensor(data_np, self.device)
            
            # 执行性能分析
            report = vm.profile("main", data_tensor)
            
            print("逐层性能分析报告:")
            print(report)
            print()
            
            # 分析报告中的各个操作
            report_str = str(report)
            if "dense" in report_str.lower():
                print("检测到密集层操作")
            if "relu" in report_str.lower():
                print("检测到 ReLU 激活操作")
            
        except Exception as e:
            print(f"逐层性能分析失败: {e}")
            print()
    
    def demo_batch_size_impact(self):
        """演示批次大小对性能的影响"""
        print("4. 批次大小对性能的影响")
        
        batch_sizes = [1, 4, 8, 16, 32]
        feature_size = 512
        hidden_size = 256
        output_size = 10
        
        results = {}
        
        for batch_size in batch_sizes:
            try:
                print(f"测试批次大小: {batch_size}")
                
                input_shape = (batch_size, feature_size)
                mod = self.create_mlp_model(input_shape, [hidden_size], output_size)
                ex = tvm.compile(mod, target=self.target)
                vm = relax.VirtualMachine(ex, self.device, profile=True)
                
                # 准备数据
                data_np = np.random.randn(*input_shape).astype("float32")
                data_tensor = tvm.runtime.tensor(data_np, self.device)
                
                # 性能测试
                times = []
                for _ in range(5):
                    start = tvm.runtime.time_evaluator(lambda: vm["main"](data_tensor), self.device, number=1, repeat=1)()
                    times.append(start.mean * 1000)
                
                avg_time = np.mean(times)
                time_per_sample = avg_time / batch_size
                
                results[batch_size] = {
                    "total_time_ms": avg_time,
                    "time_per_sample_ms": time_per_sample,
                    "throughput_samples_per_sec": 1000 / time_per_sample
                }
                
                print(f"  总时间: {avg_time:.4f} ms")
                print(f"  每样本时间: {time_per_sample:.4f} ms")
                print(f"  吞吐量: {1000/time_per_sample:.2f} samples/sec")
                print()
                
            except Exception as e:
                print(f"  批次大小 {batch_size} 测试失败: {e}")
                results[batch_size] = {"error": str(e)}
                print()
        
        # 批次大小性能总结
        print("批次大小性能总结:")
        print(f"{'批次大小':<10} {'总时间(ms)':<12} {'每样本(ms)':<12} {'吞吐量(sps)':<15}")
        print("-" * 55)
        
        for batch_size, data in results.items():
            if "error" not in data:
                print(f"{batch_size:<10} {data['total_time_ms']:<12.4f} {data['time_per_sample_ms']:<12.4f} {data['throughput_samples_per_sec']:<15.2f}")
            else:
                print(f"{batch_size:<10} {'错误':<12} {'N/A':<12} {'N/A':<15}")
        print()
    
    def demo_profiling_report_export(self):
        """演示性能分析报告导出"""
        print("5. 性能分析报告导出")
        
        try:
            # 创建测试模型
            input_shape = (1, 256)
            mod = self.create_mlp_model(input_shape, [128, 64], 10)
            ex = tvm.compile(mod, target=self.target)
            vm = relax.VirtualMachine(ex, self.device, profile=True)
            
            # 准备数据
            data_np = np.random.randn(*input_shape).astype("float32")
            data_tensor = tvm.runtime.tensor(data_np, self.device)
            
            # 执行性能分析
            report = vm.profile("main", data_tensor)
            
            # 解析报告信息
            report_str = str(report)
            
            # 创建结构化报告
            structured_report = {
                "model_info": {
                    "input_shape": input_shape,
                    "hidden_layers": [128, 64],
                    "output_size": 10,
                    "target": self.target,
                    "device": str(self.device)
                },
                "raw_report": report_str,
                "timestamp": tvm.runtime.time_evaluator(lambda: None, self.device, number=1, repeat=1)().mean
            }
            
            # 保存报告
            report_file = "relax_vm_profiling_report.json"
            with open(report_file, 'w') as f:
                json.dump(structured_report, f, indent=2, default=str)
            
            print(f"性能分析报告已保存到: {report_file}")
            print("报告内容预览:")
            print(json.dumps(structured_report["model_info"], indent=2))
            print()
            
        except Exception as e:
            print(f"报告导出失败: {e}")
            print()
    
    def run_all_demos(self):
        """运行所有演示"""
        print("=" * 60)
        print("TVM Relax VM 性能分析演示")
        print("=" * 60)
        print()
        
        try:
            self.demo_basic_mlp_profiling()
            self.demo_different_model_sizes()
            self.demo_layer_wise_profiling()
            self.demo_batch_size_impact()
            self.demo_profiling_report_export()
            
            print("=" * 60)
            print("所有 Relax VM 演示完成!")
            print("=" * 60)
            
        except Exception as e:
            print(f"演示过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    demo = RelaxVMProfilingDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()