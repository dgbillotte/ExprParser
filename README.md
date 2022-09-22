# ExprParserWriter

## 🚧 NOTE: This is a work in progress, variables are not yet bound and there is at least one BUG in it. 🚧

ExprParserWriter is a parser / re-writer for the C-like expressions that are
used in the expr/expr~ objects of the PureData programming language.

Its intended purpose is for the continued development of the [Heavy/HVCC
PureData compiler (my fork)](https://github.com/dgbillotte/hvcc) which will
turn a valid Pd patch into executable C-code. Below is an example of a
simple expression and the resulting nested C-code that gets generated from
it.

```c
// input expression
sin($f1 + 2) / sqrt($f2)

// generated nested C-code
hv_div_f(hv_sin_f(hv_add_f($f1, 2)), hv_sqrt_f($f2));

// generated sequential SIMD ready C-code
__hv_add_f($f1, 2, BO0);
__hv_sin_f(BO0, BO1);
__hv_sqrt_f($f2, BO0);
__hv_div_f(BO1, BO0, BO2);
```

Pd provides two versions of expr: `[expr]` and `[expr~]` where the `~`
indicates that the object runs at "signal rate". Objects without the `~`
are run at control rate which is a couple orders of magnitude slower.

Because of this difference in needed execution speed, the audio-rate objects
rely on heavily optimized code to ensure that they can run at full speed without
buffer underflows. This is a case where it can never be fast enough because
further improvements will always allow a user to do more with a given piece of
hardware. It should be noted that smaller ARM μ-controllers are a common target
for HVCC generated code, so being precious with resources is a requirement.

The existing HVCC infrastructure provides wrappers for most of the native C
operators and functions from `math.h` of the form `hv_FUNC_f()` or
`__hv_FUNC_f()`, for example: `hv_add_f(a, b)` or `__hv_add_f(a, b, out)`. They
are designed this way to facilitate compiling for different SIMD instruction
sets, namely: AVX and SSE for the x86 architecture and NEON for ARM. If none of
these SIMD optimizations are applied the code falls back to the native C
function calls. The functions with the leading `__` are the SIMD ready functions
and the functions without can be thought of as straight wrappers around
the C library functions.



