from expr_arpeggio_parser import ExprArpeggioParser

def test_sin():
    ast = ExprArpeggioParser.parse_to_ast("sin(4)")
    assert ast.type == "func"
    assert ast.value == "sin"
    assert len(ast.nodes) == 1
    assert ast.nodes[0].type == "num"
    assert ast.nodes[0].value == "4"


def test_max():
    ast = ExprArpeggioParser.parse_to_ast("max(4, $f2)")
    assert ast.type == "func"
    assert ast.value == "max"
    assert len(ast.nodes) == 2
    assert ast.nodes[0].type == "num"
    assert ast.nodes[0].value == "4"
    assert ast.nodes[1].type == "var"
    assert ast.nodes[1].value == "$f2"

    
