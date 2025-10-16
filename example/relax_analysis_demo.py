#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVM Relax 分析功能综合演示

本文件展示了如何使用 TVM Relax 分析模块中的各种功能：
1. analysis.py 中的分析函数
2. estimate_memory_usage.py 中的内存使用估算
3. post_order_visit 遍历功能
"""

import torch
import torch.nn as nn
import tvm
from tvm import relax, tir
from tvm.relax.analysis import (
    get_static_type, erase_to_well_defined, struct_info_base_check,
    derive_call_ret_struct_info, struct_info_lca, bound_vars, free_vars,
    all_vars, all_global_vars, post_order_visit, well_formed,
    detect_recursion, computable_at_compile_time, estimate_memory_usage
)
from tvm.relax.struct_info import TensorStructInfo, FuncStructInfo
from tvm.relax.expr import Function, Var
import numpy as np
from tvm.relax.frontend.torch import from_exported_program
from torch.export import export


class SimpleModel(nn.Module):
    """简单的PyTorch模型用于演示"""
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(10, 20)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(20, 1)
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        return x


def create_sample_relax_module():
    """创建一个示例 Relax 模块用于分析"""
    print("=== 创建示例 Relax 模块 ===")
    
    # 创建 PyTorch 模型
    model = SimpleModel()
    model.eval()
    
    # 创建示例输入
    example_input = torch.randn(1, 10)
    
    # 导出为 TorchScript
    
    # 转换为 TVM Relax 模块
    with torch.no_grad():
        exported_program = export(model, (example_input,))
        mod = from_exported_program(exported_program, keep_params_as_input=True)

    mod, params = relax.frontend.detach_params(mod)
    print(f"模块创建成功，包含函数: {list(mod.functions.keys())}")
    return mod, example_input


def demo_struct_info_analysis():
    """演示 StructInfo 相关的分析功能"""
    print("\n=== StructInfo 分析演示 ===")
    
    # 创建示例 TensorStructInfo
    shape = [10, 20]
    dtype = "float32"
    tensor_sinfo = TensorStructInfo(shape, dtype)
    
    print(f"原始 TensorStructInfo: {tensor_sinfo}")
    
    # 1. 获取静态类型
    static_type = get_static_type(tensor_sinfo)
    print(f"静态类型: {static_type}")
    
    # 2. 擦除到良定义形式
    erased_sinfo = erase_to_well_defined(tensor_sinfo)
    print(f"擦除后的 StructInfo: {erased_sinfo}")
    
    # 3. 创建另一个 StructInfo 进行比较
    tensor_sinfo2 = TensorStructInfo([10, 20], "float32")
    
    # 4. 基础检查
    check_result = struct_info_base_check(tensor_sinfo, tensor_sinfo2)
    print(f"基础检查结果: {check_result}")
    
    # 5. 最小公共祖先
    lca_result = struct_info_lca(tensor_sinfo, tensor_sinfo2)
    print(f"LCA 结果: {lca_result}")


def demo_variable_analysis(mod):
    """演示变量分析功能"""
    print("\n=== 变量分析演示 ===")
    
    # 获取主函数
    main_func = mod["main"]
    print(f"分析函数: {main_func}")
    
    # 1. 绑定变量
    bound_variables = bound_vars(main_func)
    print(f"绑定变量 ({len(bound_variables)}): {[var.name_hint for var in bound_variables]}")
    
    # 2. 自由变量
    free_variables = free_vars(main_func)
    print(f"自由变量 ({len(free_variables)}): {[var.name_hint for var in free_variables]}")
    
    # 3. 所有变量
    all_variables = all_vars(main_func)
    print(f"所有变量 ({len(all_variables)}): {[var.name_hint for var in all_variables]}")
    
    # 4. 全局变量
    global_variables = all_global_vars(main_func)
    print(f"全局变量 ({len(global_variables)}): {[var.name_hint for var in global_variables]}")


def demo_post_order_visit(mod):
    """演示后序遍历功能"""
    print("\n=== 后序遍历演示 ===")
    
    main_func = mod["main"]
    visit_count = 0
    node_types = {}
    
    def visit_function(node):
        nonlocal visit_count, node_types
        visit_count += 1
        node_type = type(node).__name__
        node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"访问节点 {visit_count}: {node_type}")
        
        # 根据节点类型打印详细信息
        if hasattr(node, 'name_hint'):
            print(f"  - 名称: {node.name_hint}")
        elif hasattr(node, 'op') and hasattr(node, 'args'):
            print(f"  - 操作: {node.op}")
            print(f"  - 参数数量: {len(node.args)}")
        elif hasattr(node, 'value'):
            print(f"  - 值: {node.value}")
    
    # 执行后序遍历
    post_order_visit(main_func, visit_function)
    
    print(f"\n遍历统计:")
    print(f"总访问节点数: {visit_count}")
    print("节点类型分布:")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")


def demo_memory_usage_estimation(mod):
    """演示内存使用估算功能"""
    print("\n=== 内存使用估算演示 ===")
    
    # 估算内存使用
    memory_est = estimate_memory_usage(mod)
    print("内存使用估算结果:")
    print(memory_est)


def demo_module_analysis(mod):
    """演示模块级别的分析功能"""
    print("\n=== 模块分析演示 ===")
    
    # 1. 检查模块是否良构
    is_well_formed = well_formed(mod)
    print(f"模块是否良构: {is_well_formed}")
    
    # 2. 检测递归
    recursive_functions = detect_recursion(mod)
    print(f"递归函数组: {len(recursive_functions)}")
    for i, group in enumerate(recursive_functions):
        print(f"  组 {i+1}: {[func.name_hint for func in group]}")
    
    # 3. 编译时可计算的变量
    main_func = mod["main"]
    computable_vars = computable_at_compile_time(main_func)
    print(f"编译时可计算变量 ({len(computable_vars)}): {[var.name_hint for var in computable_vars]}")


def demo_advanced_analysis():
    """演示高级分析功能"""
    print("\n=== 高级分析演示 ===")
    
    # 创建一个更复杂的示例来演示高级功能
    print("创建复杂示例用于高级分析...")
    
    # 这里可以添加更复杂的 Relax IR 构造和分析
    print("高级分析功能需要更复杂的 IR 结构，此处展示基础框架")


def run_comprehensive_demo():
    """运行综合演示"""
    print("TVM Relax 分析功能综合演示")
    print("=" * 50)
    
    try:
        # 1. 创建示例模块
        mod, example_input = create_sample_relax_module()
        
        # 2. StructInfo 分析
        demo_struct_info_analysis()
        
        # 3. 变量分析
        demo_variable_analysis(mod)
        
        # 4. 后序遍历
        demo_post_order_visit(mod)
        
        # 5. 内存使用估算
        demo_memory_usage_estimation(mod)
        
        # 6. 模块分析
        demo_module_analysis(mod)
        
        # 7. 高级分析
        demo_advanced_analysis()
        
        print("\n" + "=" * 50)
        print("所有演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


def demo_individual_functions():
    """演示各个独立函数的使用"""
    print("\n=== 独立函数演示 ===")
    
    # 这里可以添加对特定函数的详细演示
    print("独立函数演示 - 可以根据需要添加特定函数的详细用法")


if __name__ == "__main__":
    # 运行综合演示
    run_comprehensive_demo()
    
    # 可选：运行独立函数演示
    # demo_individual_functions()