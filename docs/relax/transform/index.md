---
title: TVM Relax Transform Passes
description: TVM Relax Transform Pass API 文档索引
---

# TVM Relax Transform Passes

本文档包含 TVM Relax Transform 中所有 Pass 的详细 API 文档。


## General Passes

- [AdjustMatmulOrder](./adjustmatmulorder.md) - 
- [AllocateWorkspace](./allocateworkspace.md) - 
- [AnnotateTIROpPattern](./annotatetiroppattern.md) - 
- [AttachAttrLayoutFreeBuffers](./attachattrlayoutfreebuffers.md) - 
- [AttachGlobalSymbol](./attachglobalsymbol.md) - 
- [BindParams](./bindparams.md) - 
- [BundleModelParams](./bundlemodelparams.md) - 
- [CallTIRRewrite](./calltirrewrite.md) - 
- [CanonicalizeBindings](./canonicalizebindings.md) - 
- [CanonicalizeRelaxBindings](./canonicalizerelaxbindings.md) - 
- [CanonicalizeTIRVariables](./canonicalizetirvariables.md) - 
- [CombineParallelMatmul](./combineparallelmatmul.md) - 
- [ComputePrimValue](./computeprimvalue.md) - 
- [ConvertLayout](./convertlayout.md) - 
- [ConvertToDataflow](./converttodataflow.md) - 
- [DataflowUseInplaceCalls](./dataflowuseinplacecalls.md) - 
- [DeadCodeElimination](./deadcodeelimination.md) - 
- [DecomposeOps](./decomposeops.md) - 
- [EliminateCommonSubexpr](./eliminatecommonsubexpr.md) - 
- [ExpandMatmulOfSum](./expandmatmulofsum.md) - 
- [ExpandTupleArguments](./expandtuplearguments.md) - 
- [FewShotTuning](./fewshottuning.md) - 
- [FuseTIR](./fusetir.md) - 
- [InlinePrivateFunctions](./inlineprivatefunctions.md) - 
- [KillAfterLastUse](./killafterlastuse.md) - 
- [LambdaLift](./lambdalift.md) - 
- [LazyGetInput](./lazygetinput.md) - 
- [LazySetOutput](./lazysetoutput.md) - 
- [LegalizeOps](./legalizeops.md) - 
- [LiftTransformParams](./lifttransformparams.md) - 
- [LowerAllocTensor](./loweralloctensor.md) - 
- [MergeCompositeFunctions](./mergecompositefunctions.md) - 
- [MetaScheduleApplyDatabase](./metascheduleapplydatabase.md) - 
- [MetaScheduleTuneTIR](./metascheduletunetir.md) - 
- [MutateOpsForTraining](./mutateopsfortraining.md) - 
- [Normalize](./normalize.md) - 
- [NormalizeGlobalVar](./normalizeglobalvar.md) - 
- [PartitionTransformParams](./partitiontransformparams.md) - 
- [RealizeVDevice](./realizevdevice.md) - 
- [RemovePurityChecking](./removepuritychecking.md) - 
- [RemoveUnusedOutputs](./removeunusedoutputs.md) - 
- [RemoveUnusedParameters](./removeunusedparameters.md) - 
- [ReorderPermuteDimsAfterConcat](./reorderpermutedimsafterconcat.md) - 
- [ReorderTakeAfterMatmul](./reordertakeaftermatmul.md) - 
- [RewriteCUDAGraph](./rewritecudagraph.md) - 
- [RewriteDataflowReshape](./rewritedataflowreshape.md) - 
- [SplitCallTIRByPattern](./splitcalltirbypattern.md) - 
- [SplitLayoutRewritePreproc](./splitlayoutrewritepreproc.md) - 
- [StaticPlanBlockMemory](./staticplanblockmemory.md) - 
- [ToNonDataflow](./tonondataflow.md) - 
- [TopologicalSort](./topologicalsort.md) - 
- [UpdateParamStructInfo](./updateparamstructinfo.md) - 
- [UpdateVDevice](./updatevdevice.md) - 

## Optimization Passes

- [DecomposeOpsForInference](./decomposeopsforinference.md) - 推理阶段操作分解 Pass
- [DecomposeOpsForTraining](./decomposeopsfortraining.md) - 训练阶段操作分解 Pass
- [FoldConstant](./foldconstant.md) - 常量折叠 Pass
- [FuseOps](./fuseops.md) - 算子融合 Pass


## 统计信息

- 总 Pass 数量: 57
- 分类数量: 2
