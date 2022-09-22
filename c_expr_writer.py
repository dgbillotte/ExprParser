from expr_arpeggio_parser import ExprArpeggioGrammar as grammar
from gvgen import *

class CExprWriter:
    def __init__(self, expression):
        self.expression = expression
        self.expr_tree = grammar.parse_to_ast(expression)
        
    def to_ast(self):
        return self.expr_tree

    def to_c_simd(self):
        return CExprWriter._output_c_simd(self.expr_tree)

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

    def _output_c_simd(expr_tree):
        ba = BufferAllocator()
        lines = []

        def _output_c_simd_R(expr_tree):
            if expr_tree.type in ("num", "var"):
                return expr_tree.value

            args = []
            buffers = []
            for node in expr_tree.nodes:
                val = _output_c_simd_R(node)
                args.append(val)
                if type(val) == str and val.startswith("B"):
                    buffers.append(val)

            next_buf = f"BO{ba.next()}"
            args.append(next_buf)
            lines.append(f"{get_hv_func(expr_tree.value)}({', '.join(args)});")
            [ba.free(int(b[2])) for b in buffers]

            return next_buf

        lines.append(_output_c_simd_R(expr_tree))
        return lines


    # def to_c_nested(self):
        # This works off of the raw parse tree and outputs 
        # c-code as nested function calls
        # It needs slight tweaking to work off of the AST
        # match expr.rule_name:
        #     case "num_i"|"num_f"|"var":
        #         return expr.value
        #     case "func":
        #         return expr[0].value + "(" + ", ".join([to_c(p) for p in expr[1:]]) + ")"
        #     case "unary":
        #         return f"op{expr[0].value}({to_c(expr[1])})"
        #     case "lor"|"land"|"bor"|"xor"|"band"|"eq"|"gtlt"|"shift"|"term"|"factor":
        #         return f"op{str(expr[1])}({to_c(expr[0])}, {to_c(expr[2])})"