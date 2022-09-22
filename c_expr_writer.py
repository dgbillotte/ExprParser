from expr_arpeggio_parser import ExprArpeggioParser
from gvgen import *

class CExprWriter:
    def __init__(self, expression):
        self.expression = expression
        self.expr_tree = ExprArpeggioParser.parse_to_ast(expression)
        
    def to_ast(self):
        return self.expr_tree

    def to_c_simd(self):
        return self._to_c_simd()

    def to_c_nested(self):
        return self._to_c_nested()

    def to_dot(self, expr):
        graph = GvGen()
        CExprWriter._expr_node_to_gv(self.expr_tree, graph)
        CExprWriter._write_dot(graph)

    def _expr_node_to_gv(tree, graph):
        new_node = graph.newItem(f"{tree.type}:{tree.value}")
        for node in tree.nodes:
            graph.newLink(new_node, CExprWriter._exprNode_to_gv(node, graph))
        return new_node

    def _write_dot(graph, fname):
        with open(fname, "w") as f:
            graph.dot(f)

    class BufferAllocator:
        """Inner class for managing the swapping of buffers from
           output to input in successive calls
        """
        def __init__(self):
            self._avail = set()
            self._next = 0

        def next(self):
            if len(self._avail) > 0:
                return self._avail.pop()
            nxt = self._next
            self._next += 1
            return nxt

        def free(self, n):
            self._avail.add(n)

        def num_allocated(self):
            return self._next

    def _to_c_simd(self):
        ba = CExprWriter.BufferAllocator()
        lines = []

        def _to_c_simd_R(expr_tree):
            if expr_tree.type in ("num", "var"):
                return expr_tree.value

            args = []
            buffers = []
            for node in expr_tree.nodes:
                val = _to_c_simd_R(node)
                args.append(val)
                if type(val) == str and val.startswith("B"):
                    buffers.append(val)

            next_buf = f"BO{ba.next()}"
            args.append(next_buf)
            f_name = ExprOpMap.get_hv_func(expr_tree.value)
            lines.append(f"{f_name}({', '.join(args)});")
            [ba.free(int(b[2])) for b in buffers]

            return next_buf

        lines.append(_to_c_simd_R(self.expr_tree))
        return lines


    def _to_c_nested(self):
        """Output C-code as nested function calls"""

        def _to_c_nested_R(expr_tree):
            match expr_tree.type:
                case "num"|"var":
                    return expr_tree.value
                case _:  #"func":
                    f_name = ExprOpMap.get_hv_func(expr_tree.value)
                    args = [_to_c_nested_R(p) for p in expr_tree.nodes]
                    # return expr_tree.nodes[0].value + "(" + params + ")"
                    return f"{f_name}({', '.join(args)})"
                # case "unary":
                #     param = _to_c_nested_R(expr_tree.nodes[1])
                #     return f"op{expr_tree.nodes[0].value}({param})"
                # case "binary":
                #     params = ", ".join([
                #         _to_c_nested_R(expr_tree.nodes[0]),
                #         _to_c_nested_R(expr_tree.nodes[1])
                #     ])
                #     return f"op{str(expr_tree.nodes[1])}({params})"

        return _to_c_nested_R(self.expr_tree) + ";"

class ExprOpMap:
    op_map = {
        "~": "",
        "-": "__hv_neg_f",
        "*": "__hv_mul_f",
        "/": "__hv_div_f",
        "%": "__hv_?_f",
        "+": "__hv_add_f",
        "-": "__hv_sub_f",
        "<": "__hv_lt_f",
        "<=": "__hv_lte_f",
        ">": "__hv_gt_f",
        ">=": "__hv_gte_f",
        "!=": "__hv_neq_f",
        "&&": "__hv_and_f",
        "||": "__hv_or_f",
        "abs": "__hv_abs_f",
        "acos": "__hv_acos_f",
        "acosh": "__hv_acosh_f",
        "asin": "__hv_asin_f",
        "asinh": "__hv_asinh_f",
        "atan": "__hv_atan_f",
        "atan2": "__hv_atan2_f",
        "cbrt": "__hv_?_f",
        "ceil": "__hv_ceil_f",
        "copysign": "__hv_?_f",  # does this just return +/- 1? It doesn't come up in pd...
        "cos": "__hv_cos_f",
        "cosh": "__hv_cosh_f",
        "drem": "__hv_?_f",
        "erf": "__hv_?_f",
        "erfc": "__hv_?_f",
        "exp": "__hv_exp_f",
        "expm1": "__hv_?_f",
        "fact": "__hv_?_f",
        "finite": "__hv_?_f",
        "float": "__hv_cast_if",
        "floor": "__hv_floor_f",
        "fmod": "__hv_?_f",
        "ldexp": "__hv_?_f",
        "if": "__hv_?_f",
        "imodf": "__hv_?_f",
        "int": "__hv_cast_fi",
        "isinf": "__hv_?_f",
        "isnan": "__hv_?_f",
        "ln": "__hv_?_f",
        "log": "__hv_?_f",
        "log10": "__hv_?_f",
        "log1p": "__hv_?_f",
        "max": "__hv_max_f",
        "min": "__hv_min_f",
        "modf": "__hv_?_f",
        "pow": "__hv_pow_f",
        "rint": "__hv_?_f",  # round to nearest int
        "sin": "__hv_sin_f",
        "sinh": "__hv_sinh_f",
        "size": "__hv_?_f",
        "sqrt": "__hv_sqrt_f",
        "sum": "__hv_?_f",  # sum of all elements of a table
        "Sum": "__hv_?_f",  # sum of elemnets of a specified boundary of a table???
        "tan": "__hv_tan_f",
        "tanh": "__hv_tanh_f",
    }

    @classmethod
    def get_hv_func(cls, symbol):
        return cls.op_map.get(symbol, symbol)