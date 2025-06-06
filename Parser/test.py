import json
from Parser.myParser import MyParser

# 读取 lexer_output.txt 并解析成 token 列表
tokens = []
with open("../Analysis_Result/lexer_output.txt", "r", encoding="utf-8") as f:
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
print(ll1_df, "\n")
print("\n".join(analysis_log))
print(result_message)
# 若成功则输出 AST 并保存为 TXT 文件
if success:
    ast_str = json.dumps(ast, indent=2, ensure_ascii=False)
    print(ast_str)

    # 保存为 TXT 文件
    with open("../Analysis_Result/parser_output.txt", "w", encoding="utf-8") as f:
        f.write(ast_str)

    print("抽象语法树已写入 parser_output.txt 文件")
