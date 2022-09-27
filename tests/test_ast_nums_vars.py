from expr_arpeggio_parser import ExprArpeggioParser

def test_num_0():
    ast = ExprArpeggioParser.parse_to_ast("0")
    assert ast.type == "num"
    assert ast.value == "0"

def test_num_987654321():
    ast = ExprArpeggioParser.parse_to_ast("987654321")
    assert ast.type == "num"
    assert ast.value == "987654321"

def test_num_13_4():
    ast = ExprArpeggioParser.parse_to_ast("13.4")
    assert ast.type == "num"
    assert ast.value == "13.4"

def test_var_f2():
    ast = ExprArpeggioParser.parse_to_ast("$f2")
    assert ast.type == "var"
    assert ast.value == "$f2"

def test_var_v1():
    ast = ExprArpeggioParser.parse_to_ast("$v1")
    assert ast.type == "var"
    assert ast.value == "$v1"