from mySemanticAnalyzer import MySemanticAnalyzer

import json

# 从 txt 文件中读取 AST
with open("../Analysis_Result/parser_output.txt", "r", encoding="utf-8") as f:
    ast = json.load(f)

mySemanticAnalyzer = MySemanticAnalyzer()
mySemanticAnalyzer.check(ast)
mySemanticAnalyzer.report()
