from expr_arpeggio_parser import ExprArpeggioParser

def test_unary_minus():
    ast = ExprArpeggioParser.parse_to_ast("-3")
    assert ast.type == "unary"
    assert ast.value == "-"
    assert len(ast.nodes) == 1
    assert ast.nodes[0].type == "num"
    assert ast.nodes[0].value == "3"

def _test_binary_op(expr, op, arg1, arg2):
    ast = ExprArpeggioParser.parse_to_ast(expr)
    assert ast.type == "binary"
    assert ast.value == op
    assert len(ast.nodes) == 2
    assert ast.nodes[0].type == "num"
    assert ast.nodes[0].value == arg1
    assert ast.nodes[1].type == "num"
    assert ast.nodes[1].value == arg2

def test_binary_plus():
    _test_binary_op("1+2", "+", "1", "2")

def test_binary_minus():
    _test_binary_op("1-2", "-", "1", "2")

def test_term_right_association():
    ast = ExprArpeggioParser.parse_to_ast("1+2+3")
    assert ast.type == "binary"
    assert ast.value == "+"
    assert len(ast.nodes) == 2

    # left sub-tree
    assert ast.nodes[0].type == "num"
    assert ast.nodes[0].value == "1"

    # right sub-tree
    subtree = ast.nodes[1]
    assert subtree.type == "binary"
    assert subtree.value == "+"
    assert len(subtree.nodes) == 2
    assert subtree.nodes[0].type == "num"
    assert subtree.nodes[0].value == "2"
    assert subtree.nodes[1].type == "num"
    assert subtree.nodes[1].value == "3"

def test_factor_left_association():
    ast = ExprArpeggioParser.parse_to_ast("1*2*3")
    assert ast.type == "binary"
    assert ast.value == "*"
    assert len(ast.nodes) == 2
 
    # left sub-tree
    subtree = ast.nodes[0]
    assert subtree.type == "binary"
    assert subtree.value == "*"
    assert len(subtree.nodes) == 2
    assert subtree.nodes[0].type == "num"
    assert subtree.nodes[0].value == "1"
    assert subtree.nodes[1].type == "num"
    assert subtree.nodes[1].value == "2"
    
    # right sub-tree
    assert ast.nodes[1].type == "num"
    assert ast.nodes[1].value == "3"