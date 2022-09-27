from expr_arpeggio_grammar import expr_grammar


class ExprArpeggioParser():   
    """
    These two methods are the "public" API
    """
    @classmethod
    def parse(cls, expr):
        """Parse the input expression and return a parse tree"""
        return expr_grammar.parse(expr)

    @classmethod
    def parse_to_ast(cls, expr):
        """Parse the input expression and return an AST"""
        return cls.to_expr_tree(cls.parse(expr))

   
    """
    Helper methods below
    """
    @classmethod
    def to_expr_tree(cls, expr):
        match expr.rule_name:
            case "num_i"|"num_f":
                return ExprNode("num", expr.value)
            case "var":
                return ExprNode("var", expr.value)
            case "func":
                return ExprNode("func", expr[0].value, [cls.to_expr_tree(p) for p in expr[1:]])
            case "unary":
                return ExprNode("unary", expr[0].value, [cls.to_expr_tree(expr[1])])
            case "term":
                # this is RtoL associativity
                val = None
                tmp = None
                subtree = None
                for i in range(len(expr)):
                    if i % 2 == 0:
                        val = cls.to_expr_tree(expr[i])
                    else:
                        foo = ExprNode("binary", str(expr[i]), [val])
                        if not subtree:
                            subtree = foo
                        else:
                            tmp.nodes.append(foo)
                        tmp = foo
                tmp.nodes.append(val)
                return subtree

            case "lor"|"land"|"bor"|"xor"|"band"|"eq"|"gtlt"|"shift"|"factor":
                # this is LtoR associativity
                subtree = None
                for i in range(len(expr)):
                    if i % 2 == 0:
                        if not subtree:
                            subtree = cls.to_expr_tree(expr[i])
                        else:
                            subtree.nodes.append(cls.to_expr_tree(expr[i]))
                    else:
                        subtree = ExprNode("binary", str(expr[i]), [subtree])
                return subtree


class ExprNode:
    def __init__(self, node_type, value, nodes=[]):
        self.type = node_type
        self.value = value
        self.nodes = nodes

    def __str__(self):
        """Output that kinda shows the shape of the tree. This
        could be improved, but is better than flying blind.
        """

        match self.type:
            case "num" | "var":
                return f"{{type: {self.type}, value: {self.value}}}"
            case _:
                return f"""{{type: {self.type}, value: {self.value}
                    {','.join([str(p) for p in self.nodes])}
                }}"""
