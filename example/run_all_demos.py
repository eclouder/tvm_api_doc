#!/usr/bin/env python3
"""
运行所有 TVM Profiling 演示的主脚本
"""

import sys
import os
import importlib.util


def run_demo(demo_file, demo_name):
    """运行单个演示"""
    print(f"\n{'='*80}")
    print(f"运行演示: {demo_name}")
    print(f"文件: {demo_file}")
    print(f"{'='*80}")
    
    try:
        # 动态导入模块
        spec = importlib.util.spec_from_file_location("demo_module", demo_file)
        demo_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo_module)
        
        # 运行主函数
        if hasattr(demo_module, 'main'):
            demo_module.main()
        else:
            print(f"警告: {demo_file} 中没有找到 main() 函数")
            
    except Exception as e:
        print(f"运行 {demo_name} 时出现错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("TVM Profiling 演示集合")
    print("=" * 80)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义演示文件列表
    demos = [
        ("basic_profiling_demo.py", "基础性能分析演示"),
        ("advanced_profiling_demo.py", "高级性能分析演示"),
        ("relax_vm_profiling_demo.py", "Relax VM 性能分析演示")
    ]
    
    # 检查文件是否存在
    available_demos = []
    for demo_file, demo_name in demos:
        full_path = os.path.join(current_dir, demo_file)
        if os.path.exists(full_path):
            available_demos.append((full_path, demo_name))
        else:
            print(f"警告: 演示文件 {demo_file} 不存在，跳过...")
    
    if not available_demos:
        print("错误: 没有找到可用的演示文件!")
        return
    
    # 询问用户选择
    print(f"\n找到 {len(available_demos)} 个可用演示:")
    for i, (_, demo_name) in enumerate(available_demos, 1):
        print(f"{i}. {demo_name}")
    print(f"{len(available_demos) + 1}. 运行所有演示")
    print("0. 退出")
    
    try:
        choice = input(f"\n请选择要运行的演示 (0-{len(available_demos) + 1}): ").strip()
        
        if choice == "0":
            print("退出演示程序")
            return
        elif choice == str(len(available_demos) + 1):
            # 运行所有演示
            for demo_file, demo_name in available_demos:
                run_demo(demo_file, demo_name)
        else:
            # 运行单个演示
            try:
                demo_index = int(choice) - 1
                if 0 <= demo_index < len(available_demos):
                    demo_file, demo_name = available_demos[demo_index]
                    run_demo(demo_file, demo_name)
                else:
                    print("无效的选择!")
            except ValueError:
                print("请输入有效的数字!")
                
    except KeyboardInterrupt:
        print("\n\n用户中断，退出演示程序")
    except Exception as e:
        print(f"程序运行出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("演示程序结束")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()