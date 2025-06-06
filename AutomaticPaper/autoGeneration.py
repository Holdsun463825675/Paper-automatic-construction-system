import os
import pandas as pd
from CodeGeneration.Ast2Latex import Ast2Latex
from CodeGeneration.Ast2MarkDown import Ast2MarkDown
from Lexer.myLexer import tokenize_dfa
from Parser.myParser import MyParser
from SemanticAnalyzer.mySemanticAnalyzer import MySemanticAnalyzer

# 组卷功能，提供基础配置与扩展配置
# 基础配置（标题、说明、题型数量、题型分数）、扩展配置（打乱顺序：大题、小题、选项等）

def splice_questions(structure_config=None):
    print("-----------------------正在执行题目拼接-----------------------")

    # 基础组卷配置
    default_config = {
        "title": "编译原理试题",
        "instruction": "这是编译原理试题。",
        "选择题": {"count": 2, "score": 10},
        "填空题": {"count": 1, "score": 10},
        "判断题": {"count": 1, "score": 10},
        "简答题": {"count": 0, "score": 10}
    }
    if structure_config is None:
        structure_config = default_config

    # 中文编号映射
    type_index_map = {
        "选择题": "一",
        "填空题": "二",
        "判断题": "三",
        "简答题": "四"
    }

    # 加载Excel文件（每个sheet是一种题型，A列是题目完整内容）
    xls = pd.ExcelFile("AutomaticPaper/question_bank.xlsx")
    question_types = ["选择题", "填空题", "判断题", "简答题"]

    # 预组卷，生成标题、说明，然后根据题型进行拼接
    exam_lines = []
    exam_lines.append(f"试卷标题：{structure_config['title']}")
    exam_lines.append(f"说明：{structure_config['instruction']}")
    question_id = 1

    for qtype in question_types:
        if qtype not in xls.sheet_names or structure_config[qtype]["count"] == 0:
            continue

        df = xls.parse(qtype, usecols="A").dropna()
        if len(df) < structure_config[qtype]["count"]:
            raise ValueError(f"{qtype} 题目数量不足，至少需要 {structure_config[qtype]['count']} 道题")

        selected = df.sample(structure_config[qtype]["count"], random_state=42)

        exam_lines.append("")
        exam_lines.append(
            f"{type_index_map[qtype]}、{qtype}（共 {structure_config[qtype]['count']} 小题，每题 {structure_config[qtype]['score']} 分，共 {structure_config[qtype]['count'] * structure_config[qtype]['score']} 分）"
        )

        for _, row in selected.iterrows():
            question_text = row.iloc[0].strip()
            exam_lines.append(f"{question_id}. {question_text}")
            question_id += 1

    exam_lines.append("$")

    with open("Generation_result/spliced.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(exam_lines))
        print("题目已拼接：Generation_result/spliced.txt")


def compiler_front_end():
    filepath = os.path.join(f"Generation_result/spliced.txt")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"测试文件不存在: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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
        mySemanticAnalyzer.report()
        return semantic_success
    else:
        return False


import json
import random
import copy

def advanced_generation(advanced_config=None):
    # 默认配置项
    default_config = {
        "shuffle_sections": True,         # 是否打乱大题顺序
        "shuffle_questions": True,        # 是否打乱大题内的小题顺序
        "shuffle_options": True           # 是否打乱选项顺序（自动调整答案）
    }

    if advanced_config:
        config = {**default_config, **advanced_config}
    else:
        config = default_config

    # 读取 AST 文件
    with open("Analysis_Result/parser_output.txt", "r", encoding="utf-8") as f:
        ast = json.load(f)

    modified_ast = copy.deepcopy(ast)

    # 打乱大题顺序
    if config["shuffle_sections"]:
        random.shuffle(modified_ast["types"]) # 对 types 字段打乱

    question_counter = 1  # 全局小题编号

    for section in modified_ast["types"]:
        # 打乱小题顺序
        if config["shuffle_questions"]:
            random.shuffle(section["questions"]) # 对 questions 字段打乱

        # 重设小题编号并处理选择题选项
        for q in section["questions"]:
            q["id"] = f"{question_counter}."
            question_counter += 1

            if section["type"] == "选择题" and config["shuffle_options"]: # 选择题打乱选项
                options = q["options"]
                correct_answer = q["answer"] # 记录正确答案

                items = list(options.items())
                random.shuffle(items) # 打乱选项

                # 重新组织打乱后的选项顺序与答案
                new_options = {}
                new_answer = None
                for idx, (opt_key, opt_text) in enumerate(items):
                    new_label = chr(ord('A') + idx)
                    new_options[new_label] = opt_text
                    if opt_key == correct_answer:
                        new_answer = new_label

                q["options"] = new_options
                q["answer"] = new_answer

    return modified_ast



def code_generation(ast):
    print("-----------------------正在进行代码生成-----------------------")
    Ast2Latex(ast, show_answer=True)
    Ast2Latex(ast, show_answer=False)
    Ast2MarkDown(ast, show_answer=True)
    Ast2MarkDown(ast, show_answer=False)


def auto_generation(structure_config=None, advanced_config=None):
    splice_questions(structure_config)
    if compiler_front_end():
        code_generation(advanced_generation(advanced_config))
