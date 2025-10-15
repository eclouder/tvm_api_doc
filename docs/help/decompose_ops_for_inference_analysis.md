# TVM Relax DecomposeOpsForInference PASS 优化流程分析

## 概述

`DecomposeOpsForInference` 是 TVM Relax 框架中的一个重要的编译器优化 Pass，主要用于在推理阶段将复合操作分解为更基础的操作。该 Pass 位于 `tvm/src/relax/transform/decompose_ops.cc` 文件中，是 Relax 变换管道中的关键组件。

## 函数签名

```cpp
Pass DecomposeOpsForInference(ffi::Optional<ffi::String> func_name)
```

**参数说明：**
- `func_name`: 可选参数，指定要应用 Pass 的特定函数名称。如果为空，则应用到整个模块。

## 核心实现分析

### 1. 主函数逻辑

```cpp
Pass DecomposeOpsForInference(ffi::Optional<ffi::String> func_name) {
  if (func_name) {
    return ApplyPassToFunction(DecomposeOps(), func_name.value());
  } else {
    return DecomposeOps();
  }
}
```

**执行流程：**
1. **条件判断**: 检查是否提供了特定的函数名称
2. **分支处理**:
   - 如果提供了 `func_name`：调用 `ApplyPassToFunction` 将 `DecomposeOps` Pass 应用到指定函数
   - 如果未提供：直接返回 `DecomposeOps()` Pass，应用到整个模块

### 2. DecomposeOps Pass 实现

```cpp
Pass DecomposeOps() {
  auto pass_func = [](Function func, IRModule, PassContext) -> Function {
    OpDecomposer mutator;
    return Downcast<Function>(mutator(func));
  };
  return CreateFunctionPass(/*pass_function=*/pass_func,
                            /*opt_level=*/0,
                            /*pass_name=*/"DecomposeOps",
                            /*required=*/{});
}
```

**关键组件：**
- **Lambda 函数**: 定义了 Pass 的核心逻辑
- **OpDecomposer**: 实际执行操作分解的变换器
- **CreateFunctionPass**: 创建函数级别的 Pass

### 3. OpDecomposer 类实现

```cpp
class OpDecomposer : public ExprMutator {
 private:
  using ExprMutator::VisitExpr_;

  Expr VisitExpr_(const CallNode* call_node) final {
    Call call = Downcast<Call>(VisitExprPostOrder_(call_node));
    if (call->op == batch_norm_op_) {
      return DecomposeBatchNorm(call);
    } else if (call->op == tensor_to_shape_op_) {
      return TensorToShape(call, builder_);
    }
    return call;
  }

  /* composite operator list */
  const Op& batch_norm_op_ = Op::Get("relax.nn.batch_norm");
  const Op& tensor_to_shape_op_ = Op::Get("relax.tensor_to_shape");
};
```

**功能特性：**
- **继承关系**: 继承自 `ExprMutator`，提供表达式变换能力
- **访问者模式**: 重写 `VisitExpr_` 方法处理特定的调用节点
- **操作识别**: 识别需要分解的复合操作（如 batch_norm、tensor_to_shape）
- **分解调用**: 调用相应的分解函数处理复合操作

## 详细函数调用链

### 调用链路图
DecomposeOpsForInference(func_name)
├── if (func_name.has_value())
│   └── ApplyPassToFunction(DecomposeOps(), func_name.value())
│       ├── CreateModulePass(pass_func, 0, pass_name, {})
│       └── pass_func(IRModule mod, PassContext)
│           ├── 正则匹配函数名
│           ├── 创建子集模块
│           ├── 应用 DecomposeOps Pass
│           └── 合并结果回原模块
└── else
└── DecomposeOps()
└── CreateFunctionPass(pass_func, 0, "DecomposeOps", {})
└── pass_func(Function func, IRModule, PassContext)
└── OpDecomposer mutator
└── mutator(func)
└── VisitExpr_(CallNode*)
├── if (batch_norm_op_)
│   └── DecomposeBatchNorm(call)
├── if (tensor_to_shape_op_)
│   └── TensorToShape(call, builder_)
└── return call

### 1. ApplyPassToFunction 详细流程

当提供了 `func_name` 参数时，会调用 `ApplyPassToFunction`：

```cpp
Pass ApplyPassToFunction(Pass pass, ffi::String func_name_regex,
                         bool error_if_no_function_matches_regex) {
  // 创建模块级 Pass
  auto pass_func = [pass, func_name_regex, error_if_no_function_matches_regex](
                       IRModule mod, PassContext) -> IRModule {
    // 1. 函数匹配和筛选
    bool at_least_one_function_matched_regex = false;
    std::unordered_set<ffi::String> keep_original_version;
    std::unordered_set<ffi::String> internal_functions;
    IRModule subset;

    // 2. 遍历模块中的所有函数
    for (auto [gvar, func] : mod->functions) {
      std::string name = gvar->name_hint;
      if (tvm::runtime::regex_match(name, func_name_regex)) {
        // 匹配的函数：标记为需要变换
        at_least_one_function_matched_regex = true;
        // 处理内部函数的全局符号
      } else {
        // 不匹配的函数：替换为外部函数引用
        keep_original_version.insert(gvar->name_hint);
        func = relax::ExternFunc("dummy_" + name);
      }
      subset->Add(gvar, func);
    }

    // 3. 应用 Pass 到子集
    IRModule new_subset = pass(subset);
    
    // 4. 合并结果回原模块
    auto write_ptr = mod.CopyOnWrite();
    for (auto [gvar, func] : new_subset->functions) {
      if (!keep_original_version.count(gvar->name_hint)) {
        // 更新变换后的函数
        write_ptr->Remove((*it).second);
        write_ptr->Add(gvar, func);
      }
    }
    return mod;
  };

  return CreateModulePass(pass_func, 0, pass_name, {});
}
```

### 2. CreateFunctionPass 机制

```cpp
Pass CreateFunctionPass(std::function<Function(Function, IRModule, PassContext)> pass_func,
                        int opt_level, ffi::String name, tvm::ffi::Array<ffi::String> required,
                        bool traceable) {
  PassInfo pass_info = PassInfo(opt_level, name, required, traceable);
  return FunctionPass(std::move(pass_func), pass_info);
}
```

**功能：**
- 创建函数级别的 Pass 对象
- 封装 Pass 元信息（优化级别、名称、依赖等）
- 返回可执行的 Pass 对象

## 操作分解示例

### BatchNorm 分解

`DecomposeBatchNorm` 函数将批量归一化操作分解为基础算术操作：

```cpp
Tuple DecomposeBatchNorm(const Call& call) {
  // 1. 提取参数
  Expr data = call->args[0];           // 输入数据
  Expr gamma = call->args[1];          // 缩放参数
  Expr beta = call->args[2];           // 偏移参数
  Expr moving_mean = call->args[3];    // 移动平均值
  Expr moving_var = call->args[4];     // 移动方差

  // 2. 扩展维度匹配
  Expr moving_mean_expanded = ExpandToMatchInput(moving_mean, sinfo->ndim, {attrs->axis});
  Expr moving_var_expanded = ExpandToMatchInput(moving_var, sinfo->ndim, {attrs->axis});

  // 3. 数学分解：output = (x - mean) / sqrt(var + epsilon) * gamma + beta
  Expr epsilon = MakeConstantScalar(attrs->epsilon, sinfo->dtype);
  Expr sqrt_var = sqrt(add(moving_var_expanded, epsilon));
  Expr out = divide(subtract(data, moving_mean_expanded), sqrt_var);

  // 4. 应用缩放和偏移
  if (attrs->scale) {
    out = multiply(out, ExpandToMatchInput(gamma, sinfo->ndim, {attrs->axis}));
  }
  if (attrs->center) {
    out = add(out, ExpandToMatchInput(beta, sinfo->ndim, {attrs->axis}));
  }

  return Tuple({out, moving_mean, moving_var});
}
```

**分解过程：**
1. **参数提取**: 从调用节点提取所有必要参数
2. **维度处理**: 扩展统计量维度以匹配输入数据
3. **数学变换**: 将 BatchNorm 公式分解为基础算术操作
4. **条件应用**: 根据属性决定是否应用缩放和中心化
5. **结果封装**: 返回包含输出和统计量的元组

## Pass 注册机制

```cpp
TVM_FFI_STATIC_INIT_BLOCK() {
  namespace refl = tvm::ffi::reflection;
  refl::GlobalDef()
      .def("relax.transform.DecomposeOpsForInference", DecomposeOpsForInference)
      .def("relax.transform.DecomposeOpsForTraining", DecomposeOpsForTraining);
}
```

**注册功能：**
- 将 C++ 函数暴露给 Python 接口
- 支持从 Python 调用 `relax.transform.DecomposeOpsForInference`
- 实现跨语言的 Pass 调用

## 优化效果

### 1. 推理优化
- **操作简化**: 将复合操作分解为更简单的基础操作
- **内存优化**: 减少中间结果的内存占用
- **计算优化**: 便于后续的算子融合和优化

### 2. 编译优化
- **代码生成**: 基础操作更容易生成高效的目标代码
- **算子融合**: 分解后的操作更容易进行融合优化
- **硬件适配**: 基础操作更容易映射到不同硬件平台

### 3. 调试支持
- **可视化**: 分解后的计算图更容易理解和调试
- **性能分析**: 可以更精确地分析各个操作的性能
- **错误定位**: 更容易定位和修复计算错误

## 使用场景

### 1. 推理部署
```python
# Python 调用示例
import tvm.relax.transform as transform

# 应用到整个模块
pass1 = transform.DecomposeOpsForInference()

# 应用到特定函数
pass2 = transform.DecomposeOpsForInference("main")

# 在 Pass 管道中使用
seq = tvm.transform.Sequential([
    transform.DecomposeOpsForInference(),
    # 其他优化 Pass
])
```

### 2. 编译流水线
- **预处理阶段**: 在算子融合之前进行操作分解
- **优化阶段**: 配合其他优化 Pass 提升性能
- **代码生成**: 为目标代码生成做准备

## 相关 Pass

### 1. DecomposeOpsForTraining
```cpp
Pass DecomposeOpsForTraining(ffi::Optional<ffi::String> func_name) {
  auto module_pass = tvm::transform::Sequential({MutateOpsForTraining(), DecomposeOps()},
                                                "DecomposeOpsForTraining");
  // 训练模式的操作分解，包含额外的训练相关变换
}
```

### 2. MutateOpsForTraining
- 专门处理训练模式下的操作变换
- 处理梯度计算相关的操作

