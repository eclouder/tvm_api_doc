import torch
from torch import nn
from torch.export import export
from tvm.relax.frontend.torch import from_exported_program
import numpy as np
import tvm
from tvm import relax
from tvm.script import relax as R

# Create a dummy model
class TorchModel(nn.Module):
    def __init__(self):
        super(TorchModel, self).__init__()
        self.fc1 = nn.Linear(784, 256)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        return x


# Give an example argument to torch.export
example_args = (torch.randn(1, 784, dtype=torch.float32),)

# Convert the model to IRModule
with torch.no_grad():
    exported_program = export(TorchModel().eval(), example_args)
    mod_from_torch = from_exported_program(
        exported_program, keep_params_as_input=True, unwrap_unit_return_tuple=True
    )

mod_from_torch, params_from_torch = relax.frontend.detach_params(mod_from_torch)
mod_from_torch.show()

def benchmark_ir_module(
    mod: tvm.IRModule,
    params: dict,
    target: str = "llvm",
    device: tvm.runtime.Device = None,
    input_shape: tuple = (1, 784),
    input_dtype: str = "float32",
    func_name: str = "main",
    warmup: int = 3,
    repeat: int = 10,
) -> dict:
    """
    通用 IRModule 性能测试函数
    参数:
        mod: 待测试的 IRModule
        params: 模型参数字典
        target: 编译目标，如 "llvm", "cuda" 等
        device: 运行设备，默认根据 target 自动选择
        input_shape: 输入张量形状
        input_dtype: 输入张量数据类型
        func_name: 主函数名，默认 "main"
        warmup: 预热次数
        repeat: 正式测试重复次数
    返回:
        包含 mean/median/max/min/std 的性能指标字典（单位 ms）
    """
    if device is None:
        device = tvm.cpu() if target == "llvm" else tvm.cuda(0)

    # 编译
    ex = tvm.compile(mod, target=target)

    # 创建虚拟机
    vm = relax.VirtualMachine(ex, device)

    # 构造输入张量
    dummy_input = torch.randn(*input_shape, dtype=getattr(torch, input_dtype))



    
    # 预热
    for _ in range(warmup):
        _ = vm[func_name](dummy_input, *(list(params_from_torch.values())[0]))

    # 正式测试
    timing_res = vm.time_evaluator(func_name, device, number=1, repeat=repeat)(
        dummy_input, *(list(params_from_torch.values())[0])
    )

    # 解析结果
    stats = {
        "mean_ms": timing_res.mean * 1000,
        "median_ms": timing_res.median * 1000,
        "max_ms": timing_res.max * 1000,
        "min_ms": timing_res.min * 1000,
        "std_ms": timing_res.std * 1000,
    }

    # 打印摘要
    print("Execution time summary:")
    for k, v in stats.items():
        print(f"{k}: {v:.4f}")

    return stats


# 调用示例
# benchmark_ir_module(
#     mod=mod_from_torch,
#     params=params_from_torch,
#     target="llvm",
#     input_shape=(1, 784),
#     input_dtype="float32",
# )

def profiling_ir_module(
    mod: tvm.IRModule,
    params: dict,
    target: str = "llvm",
    device: tvm.runtime.Device = None,
    input_shape: tuple = (1, 784),
    input_dtype: str = "float32",
    func_name: str = "main",
    warmup: int = 3,
    repeat: int = 10,
) -> dict:
    """
    通用 IRModule 性能测试函数
    参数:
        mod: 待测试的 IRModule
        params: 模型参数字典
        target: 编译目标，如 "llvm", "cuda" 等
        device: 运行设备，默认根据 target 自动选择
        input_shape: 输入张量形状
        input_dtype: 输入张量数据类型
        func_name: 主函数名，默认 "main"
        warmup: 预热次数
        repeat: 正式测试重复次数
    返回:
        包含 mean/median/max/min/std 的性能指标字典（单位 ms）
    """
    if device is None:
        device = tvm.cpu() if target == "llvm" else tvm.cuda(0)

    # 编译
    ex = tvm.compile(mod, target=target)

    # 创建虚拟机
    vm = relax.VirtualMachine(ex, device)

    # 构造输入张量
    dummy_input = np.random.randn(*input_shape).astype(input_dtype)




    
    # # 预热
    # for _ in range(warmup):
    #     _ = vm[func_name](dummy_input, *(list(params_from_torch.values())[0]))

    # 正式测试
    profile_res = vm.profile(func_name, dummy_input, *(list(params_from_torch.values())[0]))

    # 解析结果
    stats = {
        "mean_ms": profile_res.mean * 1000,
        "median_ms": profile_res.median * 1000,
        "max_ms": profile_res.max * 1000,
        "min_ms": profile_res.min * 1000,
        "std_ms": profile_res.std * 1000,
    }

    # 打印摘要
    print("Execution time summary:")
    for k, v in stats.items():
        print(f"{k}: {v:.4f}")

    return stats

profiling_ir_module(
    mod=mod_from_torch,
    params=params_from_torch,
    target="llvm",
    input_shape=(1, 784),
    input_dtype="float32",
)

# from tvm.relax.frontend import nn


# class RelaxModel(nn.Module):
#     def __init__(self):
#         super(RelaxModel, self).__init__()
#         self.fc1 = nn.Linear(784, 256)
#         self.relu1 = nn.ReLU()
#         self.fc2 = nn.Linear(256, 10)

#     def forward(self, x):
#         x = self.fc1(x)
#         x = self.relu1(x)
#         x = self.fc2(x)
#         return x


# mod_from_relax, params_from_relax = RelaxModel().export_tvm(
#     {"forward": {"x": nn.spec.Tensor((1, 784), "float32")}}
# )
# mod_from_relax.show()
# import tvm.relax.backend.cuda.cublas as _cublas
# from tvm import IRModule, relax


# # Define a new pass for CUBLAS dispatch
# @tvm.transform.module_pass(opt_level=0, name="CublasDispatch")
# class CublasDispatch:
#     def transform_module(self, mod: IRModule, _ctx: tvm.transform.PassContext) -> IRModule:
#         # Check if CUBLAS is enabled
#         if not tvm.get_global_func("relax.ext.cublas", True):
#             raise Exception("CUBLAS is not enabled.")

#         # Get interested patterns
#         patterns = [relax.backend.get_pattern("cublas.matmul_transposed_bias_relu")]
#         # Note in real-world cases, we usually get all patterns
#         # patterns = relax.backend.get_patterns_with_prefix("cublas")

#         # Fuse ops by patterns and then run codegen
#         mod = relax.transform.FuseOpsByPattern(patterns, annotate_codegen=True)(mod)
#         mod = relax.transform.RunCodegen()(mod)
#         return mod
# import os
# import tempfile

# mod = CublasDispatch()(mod_from_relax)
# mod.show()
# device = tvm.cuda(0)
# target = tvm.target.Target.from_device(device)
# if os.getenv("CI", "") != "true":
#     trials = 2000
#     with target, tempfile.TemporaryDirectory() as tmp_dir:
#         mod = tvm.ir.transform.Sequential(
#             [
#                 relax.get_pipeline("zero"),
#                 relax.transform.MetaScheduleTuneTIR(work_dir=tmp_dir, max_trials_global=trials),
#                 relax.transform.MetaScheduleApplyDatabase(work_dir=tmp_dir),
#             ]
#         )(mod)

#     mod.show()