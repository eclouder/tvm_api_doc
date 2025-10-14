import tvm
x = tvm.tir.Var("x", "int32")
y = tvm.tir.Add(x, x)
# a and b are fields of a tir.Add node
# we can directly use the field name to access the IR structures
assert y.a == x