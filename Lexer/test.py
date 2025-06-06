from Test_Case.test_demo import py_text, word_text
from myLexer import tokenize_dfa

text = py_text # 识别 demo 试卷
# text = word_text # 识别各词素

# 执行词法分析
tokens = tokenize_dfa(text)

# 打印结果到控制台
for token in tokens:
    print(token)

# 保存结果到 TXT 文件
output_path = "../Analysis_Result/lexer_output.txt"
with open(output_path, "w", encoding="utf-8") as f:
    for token in tokens:
        f.write(f"{token}\n")

print(f"\n词法分析结果已保存到：{output_path}")
