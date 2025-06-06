import json
from Test_Case.test_demo import py_text
from Test_Case.get_test import getTest
from Lexer.myLexer import tokenize_dfa
from Parser.myParser import MyParser
from SemanticAnalyzer.mySemanticAnalyzer import MySemanticAnalyzer
from CodeGeneration.Ast2Latex import Ast2Latex
from CodeGeneration.Ast2MarkDown import Ast2MarkDown

content = py_text
# content = getTest(0)
# 执行词法分析
print("-----------------------正在执行词法分析-----------------------")
tokens = tokenize_dfa(content)

# 保存结果到 TXT 文件
output_path = "Analysis_Result/lexer_output.txt"
with open(output_path, "w", encoding="utf-8") as f:
    for token in tokens:
        f.write(f"{token}\n")

print(f"词法分析结果已保存到：{output_path}")

# 执行语法分析
print("-----------------------正在执行语法分析-----------------------")
# 读取 lexer_output.txt 并解析成 token 列表
tokens = []
with open("Analysis_Result/lexer_output.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # 将字符串形式的元组转换为实际元组
        try:
            token = eval(line)
            if isinstance(token, tuple) and len(token) == 4:
                tokens.append(token)
        except Exception as e:
            continue

# 实例化并分析
ll1_df, success, analysis_log, result_message, ast = MyParser().parse(tokens)

# 返回分析日志
print(result_message)
# 若成功则输出 AST 并保存为 TXT 文件
if success:
    ast_str = json.dumps(ast, indent=2, ensure_ascii=False)

    # 保存为 TXT 文件
    with open("Analysis_Result/parser_output.txt", "w", encoding="utf-8") as f:
        f.write(ast_str)

    print("抽象语法树已写入 parser_output.txt 文件")

    print("-----------------------正在执行语义分析-----------------------")
    # 从 txt 文件中读取 AST
    with open("Analysis_Result/parser_output.txt", "r", encoding="utf-8") as f:
        ast = json.load(f)

    mySemanticAnalyzer = MySemanticAnalyzer()
    semantic_success = mySemanticAnalyzer.check(ast)
    if not semantic_success:
        mySemanticAnalyzer.report()
    else:
        mySemanticAnalyzer.report()

        print("-----------------------正在进行代码生成-----------------------")
        Ast2Latex(ast, show_answer=True)
        Ast2Latex(ast, show_answer=False)
        Ast2MarkDown(ast, show_answer=True)
        Ast2MarkDown(ast, show_answer=False)
