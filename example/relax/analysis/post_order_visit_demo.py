#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVM Relax post_order_visit 功能详细演示

本文件专门展示 post_order_visit 函数的各种使用方法和应用场景
"""

import torch
import torch.nn as nn
import tvm
from tvm import relax
from tvm.relax.analysis import post_order_visit
from tvm.relax.expr import Function, Call, Var, Constant, Tuple, DataflowBlock
import json
from tvm.relax.frontend.torch import from_exported_program


class DemoModel(nn.Module):
    """演示用的PyTorch模型"""
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2)
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(32 * 8 * 8, 10)
    
    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = self.flatten(x)
        x = self.fc(x)
        return x


def create_demo_module():
    """创建演示用的Relax模块"""
    print("创建演示模块...")
    
    model = DemoModel()
    model.eval()
    
    # 创建示例输入 (batch_size=1, channels=3, height=32, width=32)
    example_input = torch.randn(1, 3, 32, 32)
    
    # 转换为TVM Relax模块
    with torch.no_grad():
        exported_program = torch.export.export(model, (example_input,))
        mod = from_exported_program(exported_program, keep_params_as_input=True)

    mod, params = relax.frontend.detach_params(mod)
    print(f"模块创建完成，包含函数: {list(mod.functions.keys())}")
    return mod


def demo_basic_traversal(mod):
    """基础遍历演示"""
    print("\n=== 基础后序遍历演示 ===")
    
    main_func = mod["main"]
    visit_order = []
    
    def basic_visitor(node):
        node_info = {
            'type': type(node).__name__,
            'id': id(node)
        }
        
        # 添加节点特定信息
        if hasattr(node, 'name_hint'):
            node_info['name'] = node.name_hint
        elif isinstance(node, Call) and hasattr(node, 'op'):
            node_info['op'] = str(node.op)
        elif isinstance(node, Constant):
            node_info['value'] = str(node.data)[:50]  # 限制长度
        
        visit_order.append(node_info)
        print(f"访问: {node_info}")
    
    post_order_visit(main_func, basic_visitor)
    
    print(f"\n总共访问了 {len(visit_order)} 个节点")
    return visit_order


def demo_node_counting(mod):
    """节点计数演示"""
    print("\n=== 节点计数演示 ===")
    
    main_func = mod["main"]
    node_counts = {}
    
    def counting_visitor(node):
        node_type = type(node).__name__
        node_counts[node_type] = node_counts.get(node_type, 0) + 1
    
    post_order_visit(main_func, counting_visitor)
    
    print("节点类型统计:")
    for node_type, count in sorted(node_counts.items()):
        print(f"  {node_type}: {count}")
    
    return node_counts


def demo_operation_analysis(mod):
    """操作分析演示"""
    print("\n=== 操作分析演示 ===")
    
    main_func = mod["main"]
    operations = {}
    call_depth = 0
    
    def operation_visitor(node):
        nonlocal call_depth
        
        if isinstance(node, Call):
            op_name = str(node.op)
            operations[op_name] = operations.get(op_name, 0) + 1
            
            print(f"发现操作: {op_name}")
            print(f"  参数数量: {len(node.args)}")
            
            # 分析参数类型
            arg_types = [type(arg).__name__ for arg in node.args]
            print(f"  参数类型: {arg_types}")
            
            call_depth += 1
    
    post_order_visit(main_func, operation_visitor)
    
    print(f"\n操作统计 (总调用深度: {call_depth}):")
    for op_name, count in sorted(operations.items()):
        print(f"  {op_name}: {count}")
    
    return operations


def demo_variable_tracking(mod):
    """变量跟踪演示"""
    print("\n=== 变量跟踪演示 ===")
    
    main_func = mod["main"]
    variables = {}
    variable_usage = {}
    
    def variable_visitor(node):
        if isinstance(node, Var):
            var_name = node.name_hint
            var_id = id(node)
            
            if var_id not in variables:
                variables[var_id] = {
                    'name': var_name,
                    'type': str(node.struct_info) if hasattr(node, 'struct_info') else 'unknown',
                    'first_seen': len(variables)
                }
                print(f"新变量: {var_name} (ID: {var_id})")
            
            # 跟踪使用次数
            variable_usage[var_id] = variable_usage.get(var_id, 0) + 1
    
    post_order_visit(main_func, variable_visitor)
    
    print(f"\n变量统计:")
    print(f"总变量数: {len(variables)}")
    
    print("\n变量使用频率:")
    for var_id, usage_count in sorted(variable_usage.items(), key=lambda x: x[1], reverse=True):
        var_info = variables[var_id]
        print(f"  {var_info['name']}: {usage_count} 次")
    
    return variables, variable_usage


def demo_structure_analysis(mod):
    """结构分析演示"""
    print("\n=== 结构分析演示 ===")
    
    main_func = mod["main"]
    structure_info = {
        'max_depth': 0,
        'current_depth': 0,
        'blocks': 0,
        'functions': 0,
        'calls': 0
    }
    
    def structure_visitor(node):
        node_type = type(node).__name__
        
        if node_type == 'Function':
            structure_info['functions'] += 1
            print(f"函数: {getattr(node, 'name_hint', 'anonymous')}")
        
        elif node_type == 'DataflowBlock':
            structure_info['blocks'] += 1
            print(f"数据流块 #{structure_info['blocks']}")
        
        elif node_type == 'Call':
            structure_info['calls'] += 1
            structure_info['current_depth'] += 1
            structure_info['max_depth'] = max(structure_info['max_depth'], structure_info['current_depth'])
            
            # 调用完成后减少深度
            structure_info['current_depth'] = max(0, structure_info['current_depth'] - 1)
    
    post_order_visit(main_func, structure_visitor)
    
    print(f"\n结构统计:")
    print(f"  函数数: {structure_info['functions']}")
    print(f"  数据流块数: {structure_info['blocks']}")
    print(f"  调用数: {structure_info['calls']}")
    print(f"  最大调用深度: {structure_info['max_depth']}")
    
    return structure_info


def demo_custom_analysis(mod):
    """自定义分析演示"""
    print("\n=== 自定义分析演示 ===")
    
    main_func = mod["main"]
    
    # 自定义分析：查找特定模式
    patterns = {
        'conv_relu_pattern': 0,
        'linear_operations': 0,
        'activation_functions': 0
    }
    
    recent_ops = []
    
    def pattern_visitor(node):
        if isinstance(node, Call):
            op_name = str(node.op)
            recent_ops.append(op_name)
            
            # 保持最近3个操作的记录
            if len(recent_ops) > 3:
                recent_ops.pop(0)
            
            # 检查模式
            if 'conv2d' in op_name.lower():
                patterns['linear_operations'] += 1
                
                # 检查是否紧跟ReLU
                if len(recent_ops) >= 2 and 'relu' in recent_ops[-2].lower():
                    patterns['conv_relu_pattern'] += 1
            
            elif 'relu' in op_name.lower() or 'sigmoid' in op_name.lower() or 'tanh' in op_name.lower():
                patterns['activation_functions'] += 1
            
            elif 'dense' in op_name.lower() or 'linear' in op_name.lower():
                patterns['linear_operations'] += 1
    
    post_order_visit(main_func, pattern_visitor)
    
    print("模式分析结果:")
    for pattern_name, count in patterns.items():
        print(f"  {pattern_name}: {count}")
    
    return patterns


def demo_memory_footprint_analysis(mod):
    """内存足迹分析演示"""
    print("\n=== 内存足迹分析演示 ===")
    
    main_func = mod["main"]
    memory_info = {
        'total_tensors': 0,
        'total_parameters': 0,
        'tensor_shapes': [],
        'estimated_memory': 0
    }
    
    def memory_visitor(node):
        if hasattr(node, 'struct_info'):
            sinfo = node.struct_info
            if hasattr(sinfo, 'shape') and hasattr(sinfo, 'dtype'):
                memory_info['total_tensors'] += 1
                
                # 计算张量大小
                if hasattr(sinfo.shape, 'values'):
                    shape = [int(dim) for dim in sinfo.shape.values if hasattr(dim, 'value')]
                    memory_info['tensor_shapes'].append(shape)
                    
                    # 估算内存使用（假设float32）
                    size = 1
                    for dim in shape:
                        size *= dim
                    memory_info['estimated_memory'] += size * 4  # 4 bytes per float32
        
        elif isinstance(node, Constant):
            memory_info['total_parameters'] += 1
    
    post_order_visit(main_func, memory_visitor)
    
    print("内存分析结果:")
    print(f"  张量数量: {memory_info['total_tensors']}")
    print(f"  参数数量: {memory_info['total_parameters']}")
    print(f"  估算内存使用: {memory_info['estimated_memory'] / (1024*1024):.2f} MB")
    
    if memory_info['tensor_shapes']:
        print("  张量形状样例:")
        for i, shape in enumerate(memory_info['tensor_shapes'][:5]):  # 显示前5个
            print(f"    张量 {i+1}: {shape}")
    
    return memory_info


def run_all_demos():
    """运行所有演示"""
    print("TVM Relax post_order_visit 功能演示")
    print("=" * 60)
    
    try:
        # 创建演示模块
        mod = create_demo_module()
        
        # 运行各种演示
        visit_order = demo_basic_traversal(mod)
        node_counts = demo_node_counting(mod)
        operations = demo_operation_analysis(mod)
        variables, variable_usage = demo_variable_tracking(mod)
        structure_info = demo_structure_analysis(mod)
        patterns = demo_custom_analysis(mod)
        memory_info = demo_memory_footprint_analysis(mod)
        
        # 总结
        print("\n" + "=" * 60)
        print("演示总结:")
        print(f"- 总节点数: {len(visit_order)}")
        print(f"- 节点类型数: {len(node_counts)}")
        print(f"- 操作类型数: {len(operations)}")
        print(f"- 变量数: {len(variables)}")
        print(f"- 估算内存: {memory_info['estimated_memory'] / (1024*1024):.2f} MB")
        
        print("\n所有演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()