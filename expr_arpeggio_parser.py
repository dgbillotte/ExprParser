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
            case "lor"|"land"|"bor"|"xor"|"band"|"eq"|"gtlt"|"shift"|"term"|"factor":
                return ExprNode("binary", str(expr[1]), [cls.to_expr_tree(expr[0]), cls.to_expr_tree(expr[2])])


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
