#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVM Relax 内存使用估算功能详细演示

本文件专门展示 estimate_memory_usage 函数的使用方法和各种应用场景
"""

import torch
import torch.nn as nn
import tvm
from tvm import relax
from tvm.ir import IRModule
from tvm.relax.analysis.estimate_memory_usage import estimate_memory_usage
import numpy as np
from tvm.relax.frontend.torch import from_exported_program


class SmallModel(nn.Module):
    """小型模型"""
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 5)
    
    def forward(self, x):
        return self.fc(x)


class MediumModel(nn.Module):
    """中型模型"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64, 10)
    
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x


class LargeModel(nn.Module):
    """大型模型"""
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 512, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(512 * 8 * 8, 1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 100)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def create_model_variants():
    """创建不同大小的模型用于内存估算比较"""
    models = {}
    
    # 小型模型
    small_model = SmallModel()
    small_input = torch.randn(1, 10)
    models['small'] = {
        'model': small_model,
        'input': small_input,
        'input_spec': [("input", small_input.shape, "float32")]
    }
    
    # 中型模型
    medium_model = MediumModel()
    medium_input = torch.randn(1, 3, 32, 32)
    models['medium'] = {
        'model': medium_model,
        'input': medium_input,
        'input_spec': [("input", medium_input.shape, "float32")]
    }
    
    # 大型模型
    large_model = LargeModel()
    large_input = torch.randn(1, 3, 32, 32)
    models['large'] = {
        'model': large_model,
        'input': large_input,
        'input_spec': [("input", large_input.shape, "float32")]
    }
    
    return models


def convert_to_relax(model_info):
    """将PyTorch模型转换为Relax模块"""
    model = model_info['model']
    input_tensor = model_info['input']
    input_spec = model_info['input_spec']
    
    model.eval()
    
    # 使用 from_exported_program 转换为TVM Relax模块
    exported = torch.export.export(model, (model_info['input'],))
    mod = from_exported_program(exported)
    
    return mod


def demo_basic_memory_estimation():
    """基础内存估算演示"""
    print("=== 基础内存估算演示 ===")
    
    models = create_model_variants()
    
    for model_name, model_info in models.items():
        print(f"\n--- {model_name.upper()} 模型 ---")
        
        # 转换为Relax模块
        mod = convert_to_relax(model_info)
        
        # 估算内存使用
        memory_est = estimate_memory_usage(mod)
        print(f"内存估算结果:")
        print(memory_est)
        
        # 计算模型参数数量
        total_params = sum(p.numel() for p in model_info['model'].parameters())
        param_memory = total_params * 4 / (1024 * 1024)  # MB (假设float32)
        print(f"PyTorch模型参数: {total_params:,} ({param_memory:.2f} MB)")


def demo_function_level_estimation():
    """函数级别内存估算演示"""
    print("\n=== 函数级别内存估算演示 ===")
    
    # 使用中型模型进行详细分析
    models = create_model_variants()
    model_info = models['medium']
    mod = convert_to_relax(model_info)
    
    print("模块中的函数:")
    for func_name in mod.functions.keys():
        print(f"  - {func_name}")
    
    # 对每个函数进行内存估算
    for func_name, func in mod.functions_items():
        if isinstance(func, relax.Function):
            print(f"\n--- 函数 {func_name} ---")
            
            # 创建只包含这个函数的模块
            single_func_mod = tvm.IRModule({func_name: func})
            
            # 估算内存
            memory_est = estimate_memory_usage(single_func_mod)
            print(memory_est)


def demo_memory_planning_comparison():
    """内存规划前后对比演示"""
    print("\n=== 内存规划前后对比演示 ===")
    
    models = create_model_variants()
    
    for model_name, model_info in models.items():
        print(f"\n--- {model_name.upper()} 模型内存规划对比 ---")
        
        mod = convert_to_relax(model_info)
        
        # 原始模块内存估算
        print("原始模块:")
        original_est = estimate_memory_usage(mod)
        print(original_est)
        
        # 应用内存规划优化
        try:
            # 这里可以添加内存规划的transform
            # optimized_mod = relax.transform.PlanMemory()(mod)
            # optimized_est = estimate_memory_usage(optimized_mod)
            # print("优化后模块:")
            # print(optimized_est)
            print("注意: 内存规划优化需要额外的transform步骤")
        except Exception as e:
            print(f"内存规划优化暂不可用: {e}")


def demo_batch_size_impact():
    """批次大小对内存使用的影响演示"""
    print("\n=== 批次大小对内存使用的影响 ===")
    
    batch_sizes = [1, 4, 8, 16, 32]
    
    for batch_size in batch_sizes:
        print(f"\n--- Batch Size: {batch_size} ---")
        
        # 创建不同批次大小的输入
        model = MediumModel()
        model.eval()
        
        input_tensor = torch.randn(batch_size, 3, 32, 32)
        input_spec = [("input", input_tensor.shape, "float32")]
        
        # 使用 from_exported_program 转换为 Relax 模块
        exported = torch.export.export(model, (input_tensor,))
        mod = from_exported_program(exported)
        
        # 估算内存
        memory_est = estimate_memory_usage(mod)
        print(memory_est)


def demo_dtype_impact():
    """数据类型对内存使用的影响演示"""
    print("\n=== 数据类型对内存使用的影响 ===")
    
    dtypes = ["float32", "float16", "int8"]
    
    model = SmallModel()
    model.eval()
    
    for dtype in dtypes:
        print(f"\n--- 数据类型: {dtype} ---")
        
        input_tensor = torch.randn(1, 10)
        input_spec = [("input", input_tensor.shape, dtype)]
        
        try:
            # 转换为Relax模块
            mod = relax.frontend.from_pytorch(model, input_spec)
            
            # 估算内存
            memory_est = estimate_memory_usage(mod)
            print(memory_est)
            
        except Exception as e:
            print(f"数据类型 {dtype} 转换失败: {e}")


def demo_custom_memory_analysis():
    """自定义内存分析演示"""
    print("\n=== 自定义内存分析演示 ===")
    
    model_info = create_model_variants()['medium']
    mod = convert_to_relax(model_info)
    
    # 直接使用estimate_memory_usage函数
    print("\n--- 标准内存分析 ---")
    memory_est = estimate_memory_usage(mod)
    print(memory_est)
    
    # 注意：MemoryEstimator是内部类，不能直接导入使用
    # 如果需要更详细的分析，可以通过其他方式实现
    print("\n--- 模块信息 ---")
    for func_name, func in mod.functions_items():
        if isinstance(func, relax.Function):
            print(f"函数: {func_name}")
            print(f"参数数量: {len(func.params)}")
            print(f"函数体类型: {type(func.body)}")
            
            # 使用estimate_memory_usage分析单个函数
            single_func_mod = IRModule({func_name: func})
            func_memory_est = estimate_memory_usage(single_func_mod)
            print(f"单函数内存估算:\n{func_memory_est}")


def demo_memory_optimization_suggestions():
    """内存优化建议演示"""
    print("\n=== 内存优化建议演示 ===")
    
    models = create_model_variants()
    
    for model_name, model_info in models.items():
        print(f"\n--- {model_name.upper()} 模型优化建议 ---")
        
        mod = convert_to_relax(model_info)
        memory_est = estimate_memory_usage(mod)
        
        print("当前内存使用:")
        print(memory_est)
        
        # 分析并提供优化建议
        print("\n优化建议:")
        
        # 基于模型大小提供建议
        if model_name == 'small':
            print("- 小型模型，内存使用已经很少")
            print("- 可以考虑使用更小的数据类型（如float16）")
        elif model_name == 'medium':
            print("- 中型模型，可以考虑以下优化:")
            print("  * 使用梯度检查点减少中间激活的内存")
            print("  * 应用算子融合减少临时张量")
        elif model_name == 'large':
            print("- 大型模型，强烈建议以下优化:")
            print("  * 使用混合精度训练（float16/bfloat16）")
            print("  * 应用内存规划和重用")
            print("  * 考虑模型并行或流水线并行")
            print("  * 使用动态形状优化")


def run_all_memory_demos():
    """运行所有内存估算演示"""
    print("TVM Relax 内存使用估算功能演示")
    print("=" * 60)
    
    try:
        # 基础内存估算
        demo_basic_memory_estimation()
        
        # 函数级别估算
        demo_function_level_estimation()
        
        # 内存规划对比
        demo_memory_planning_comparison()
        
        # 批次大小影响
        demo_batch_size_impact()
        
        # 数据类型影响
        demo_dtype_impact()
        
        # 自定义内存分析
        demo_custom_memory_analysis()
        
        # 优化建议
        demo_memory_optimization_suggestions()
        
        print("\n" + "=" * 60)
        print("所有内存估算演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_memory_demos()