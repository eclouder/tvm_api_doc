# TVM Relax Analysis API 演示示例

本目录包含了 TVM Relax 分析模块的完整演示示例，展示了如何使用 TVM Relax 的各种分析功能进行深度学习模型的分析和优化。

## 📁 文件概览

### 🔍 [relax_analysis_demo.py](./relax_analysis_demo.py)
**综合分析功能演示** 
- 展示 TVM Relax `analysis.py` 模块中的核心分析功能
- 集成多个分析 API 的协同使用
- 提供完整的 TVM Relax 分析工作流

### 💾 [memory_estimation_demo.py](./memory_estimation_demo.py)
**内存使用估算演示** 
- 专门展示 `estimate_memory_usage` 函数的使用方法
- 多维度内存分析（批次大小、数据类型、模型规模）
- 内存优化建议和最佳实践

### 🌲 [post_order_visit_demo.py](./post_order_visit_demo.py)
**后序遍历功能演示** 
- 深度展示 `post_order_visit` 函数的各种应用场景
- IR 节点分析、模式识别、结构分析
- 自定义遍历和分析功能

## 🚀 快速开始

### 环境要求

```bash
# 必需依赖
pip install torch torchvision
pip install numpy

# TVM 安装（请参考 TVM 官方文档）
# https://tvm.apache.org/docs/install/index.html
```

### 运行示例

```bash
# 运行综合分析演示
python relax_analysis_demo.py

# 运行内存估算演示
python memory_estimation_demo.py

# 运行后序遍历演示
python post_order_visit_demo.py
```

## 📚 功能详解

### 1. 综合分析功能 (`relax_analysis_demo.py`)

#### 🔧 核心功能
- **StructInfo 分析**: 类型检查、擦除、最小公共祖先（LCA）
- **变量分析**: 绑定变量、自由变量、全局变量识别
- **模块分析**: 良构性检查、递归检测
- **编译时分析**: 可计算变量识别

#### 📋 演示内容
```python
# 主要演示函数
demo_struct_info_analysis()      # StructInfo 相关分析
demo_variable_analysis(mod)      # 变量分析
demo_post_order_visit(mod)       # 后序遍历集成
demo_memory_usage_estimation(mod) # 内存估算集成
demo_module_analysis(mod)        # 模块级别分析
```

#### 🎯 适用场景
- 学习 TVM Relax 分析 API
- 模型 IR 结构理解
- 编译器开发和调试

### 2. 内存估算功能 (`memory_estimation_demo.py`)

#### 🔧 核心功能
- **多模型对比**: 小型、中型、大型模型内存使用对比
- **批次影响分析**: 不同批次大小对内存的影响
- **数据类型分析**: float32、float16、int8 等类型的内存差异
- **优化建议**: 基于分析结果提供内存优化建议

#### 📋 演示内容
```python
# 主要演示函数
demo_basic_memory_estimation()      # 基础内存估算
demo_function_level_estimation()    # 函数级别分析
demo_batch_size_impact()           # 批次大小影响
demo_dtype_impact()                # 数据类型影响
demo_memory_optimization_suggestions() # 优化建议
```

#### 🎯 适用场景
- 模型内存使用评估
- 部署前的资源规划
- 内存优化策略制定

### 3. 后序遍历功能 (`post_order_visit_demo.py`)

#### 🔧 核心功能
- **节点统计**: IR 中各类型节点的统计分析
- **操作分析**: 深度学习操作的识别和分析
- **模式识别**: 自定义模式检测（如 Conv-ReLU 模式）
- **结构分析**: 模型结构的深度和复杂度分析

#### 📋 演示内容
```python
# 主要演示函数
demo_basic_traversal(mod)          # 基础遍历
demo_node_counting(mod)            # 节点计数
demo_operation_analysis(mod)       # 操作分析
demo_variable_tracking(mod)        # 变量跟踪
demo_structure_analysis(mod)       # 结构分析
demo_custom_analysis(mod)          # 自定义分析
demo_memory_footprint_analysis(mod) # 内存足迹分析
```
