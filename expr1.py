from arpeggio import ZeroOrMore, ParserPython, StrMatch
from arpeggio import RegExMatch as _

from gvgen import *


"""
ExprParser is a parser for c-like expressions that are used in
the [expr] and [expr~] objects.
"""


class ExprParser():

    class SuppressStrMatch(StrMatch):
        suppress = True

    hide = SuppressStrMatch

    def expr():     return ExprParser.lor  # EOF
    def lor():      return ExprParser.land, ZeroOrMore("||", ExprParser.land)
    def land():     return ExprParser.bor, ZeroOrMore("&&", ExprParser.bor)
    def bor():      return ExprParser.xor, ZeroOrMore("|", ExprParser.xor)
    def xor():      return ExprParser.band, ZeroOrMore("^", ExprParser.band)
    def band():     return ExprParser.eq, ZeroOrMore("&", ExprParser.eq)
    def eq():       return ExprParser.gtlt, ZeroOrMore(["==","!="], ExprParser.gtlt)
    def gtlt():     return ExprParser.shift, ZeroOrMore(["<","<=",">",">="], ExprParser.shift)
    def shift():    return ExprParser.term, ZeroOrMore(["<<",">>"], ExprParser.term)
    def term():     return ExprParser.factor, ZeroOrMore(["+","-"], ExprParser.factor)
    def factor():   return ExprParser.unary, ZeroOrMore(["*","/","%"], ExprParser.unary)
    def unary():    return [(["-","~","!"], ExprParser.unary), ExprParser.primary]
    def primary():  return [ExprParser.number, ExprParser.var, ExprParser.func, ExprParser.group]
    def number():   return [ExprParser.num_f, ExprParser.num_i]
    def var():      return _(r"\$[fis]\d+")
    def func():     return [
                        (   # one parameter functions
                            ExprParser.f_name, ExprParser.hide("("),
                            ExprParser.expr, ExprParser.hide(")")
                        ),
                        (   # two parameter functions
                            ExprParser.f_name, ExprParser.hide("("),
                            ExprParser.expr, ExprParser.hide(","),
                            ExprParser.expr, ExprParser.hide(")")
                        ),
                        (   # three parameter functions
                            ExprParser.f_name, ExprParser.hide("("),
                            ExprParser.expr, ExprParser.hide(","),
                            ExprParser.expr, ExprParser.hide(","),
                            ExprParser.expr, ExprParser.hide(")")
                        )
                    ]
    def group():    return ExprParser.hide("("), ExprParser.expr, ExprParser.hide(")")
    def num_f():    return _(r"\d+\.\d+")
    def num_i():    return _(r"\d+")
    def f_name():   return [
                        "abs", "acos", "acosh", "asin", "asinh", "atan", "atan2",
                        "cbrt", "ceil", "copysign", "cos", "cosh", "drem", "erf",
                        "erfc", "exp", "expm1", "fact", "finite", "float", "floor",
                        "fmod", "ldexp", "if", "imodf", "int", "isinf", "isnan",
                        "ln", "log", "log10", "log1p", "max", "min", "modf", "pow",
                        "rint", "sin", "sinh", "size", "sqrt", "sum", "Sum",
                        "tan", "tanh",
                    ]

parser = ParserPython(ExprParser.expr, reduce_tree=True)


op_map = {
    "~": "",
    "-": "__hv_neg_f",
    "*": "__hv_mul_f",
    "/": "__hv_div_f",
    # "%": "__hv__f",
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
    # "cbrt": "__hv__f",
    "ceil": "__hv_ceil_f",
    # "copysign": "__hv__f",  # does this just return +/- 1? It doesn't come up in pd...
    "cos": "__hv_cos_f",
    "cosh": "__hv_cosh_f",
    # "drem": "__hv__f",
    # "erf": "__hv__f",
    # "erfc": "__hv__f",
    "exp": "__hv_exp_f",
    # "expm1": "__hv__f",
    # "fact": "__hv__f",
    # "finite": "__hv__f",
    "float": "__hv_cast_if",
    "floor": "__hv_floor_f",
    # "fmod": "__hv__f",
    # "ldexp": "__hv__f",
    # "if": "__hv__f",
    # "imodf": "__hv__f",
    "int": "__hv_cast_fi",
    # "isinf": "__hv__f",
    # "isnan": "__hv__f",
    # "ln": "__hv__f",
    # "log": "__hv__f",
    # "log10": "__hv__f",
    # "log1p": "__hv__f",
    "max": "__hv_max_f",
    "min": "__hv_min_f",
    # "modf": "__hv__f",
    "pow": "__hv_pow_f",
    # "rint": "__hv__f",  # round to nearest int
    "sin": "__hv_sin_f",
    "sinh": "__hv_sinh_f",
    # "size": "__hv__f",
    "sqrt": "__hv_sqrt_f",
    # "sum": "__hv__f",  # sum of all elements of a table
    # "Sum": "__hv__f",  # sum of elemnets of a specified boundary of a table???
    "tan": "__hv_tan_f",
    "tanh": "__hv_tanh_f",
}

def get_hv_func(symbol):
    return op_map.get(symbol, symbol)


from arpeggio.export import PTDOTExporter
def dot(tree, file):
    PTDOTExporter().exportFile(tree, file)



class ExprNode:
    def __init__(self, node_type, value, nodes=[]):
        self.type = node_type
        self.value = value
        self.nodes = nodes

    def __str__(self):
        match self.type:
            case "num" | "var":
                return f"{{type: {self.type}, value: {self.value}}}"
            case _:
                return f"""{{type: {self.type}, value: {self.value}
                    {','.join([str(p) for p in self.nodes])}
                }}"""

def to_ExprNode(expr):
    match expr.rule_name:
        case "num_i"|"num_f":
            return ExprNode("num", expr.value)
        case "var":
            return ExprNode("var", expr.value)
        case "func":
            return ExprNode("func", expr[0].value, [to_ExprNode(p) for p in expr[1:]])
        case "unary":
            return ExprNode("unary", expr[0].value, [to_ExprNode(expr[1])])
        case "lor"|"land"|"bor"|"xor"|"band"|"eq"|"gtlt"|"shift"|"term"|"factor":
            return ExprNode("binary", str(expr[1]), [to_ExprNode(expr[0]), to_ExprNode(expr[2])])


class BufferAllocator:
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


ba = BufferAllocator()

def output_c_simd(expr_tree):
    if expr_tree.type in ("num", "var"):
        return expr_tree.value

    args = []
    used_bs = []
    for node in expr_tree.nodes:
        val = output_c_simd(node)
        if type(val) == str and val.startswith("B"):
            used_bs.append(val)
        args.append(val)

    b_next = f"BO{ba.next()}"
    args.append(b_next)
    func = f"{get_hv_func(expr_tree.value)}({', '.join(args)});"
    # free up old_bs here
    [ba.free(int(b[2])) for b in used_bs]
    print(func)
    return b_next


            
# ------------------------- testing scripty stuff
def exprNode_to_gv(tree, graph):
    new_node = graph.newItem(f"{tree.type}:{tree.value}")
    for node in tree.nodes:
        graph.newLink(new_node, exprNode_to_gv(node, graph))
    return new_node

def write_dot(graph, fname="test.dot"):
    with open(fname, "w") as f:
        graph.dot(f)

expr = "(sin($f1-$f3)/$i2)-$f3"
expr1 = "6<4.5/(sqrt(asin(~$f3&3,exp($f1),!6))-3^5)"
tree = parser.parse(expr1)
en_tree = to_ExprNode(tree)
graph = GvGen()
exprNode_to_gv(en_tree, graph)
write_dot(graph)
output_c_simd(en_tree)
print("num buffers", ba.num_allocated())



# -------------- Boneyard ------------------------------------

# this works off of the raw parse tree and outputs 
# c-code as nested function calls
def to_c(expr):
    match expr.rule_name:
        case "num_i"|"num_f"|"var":
            return expr.value
        case "func":
            return expr[0].value + "(" + ", ".join([to_c(p) for p in expr[1:]]) + ")"
        case "unary":
            return f"op{expr[0].value}({to_c(expr[1])})"
        case "lor"|"land"|"bor"|"xor"|"band"|"eq"|"gtlt"|"shift"|"term"|"factor":
            return f"op{str(expr[1])}({to_c(expr[0])}, {to_c(expr[2])})"


def gp(expr):
    t = parser.parse(expr)
    dot(t, "t1.dot")
    print(to_c(t))