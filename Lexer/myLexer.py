TOKEN_MAP = {
    # 头部信息
    "试卷标题：": "HEADER",
    "说明：": "HEADER",

    # 题型
    "选择题": "QUESTION_TYPE",
    "填空题": "QUESTION_TYPE",
    "简答题": "QUESTION_TYPE",
    "判断题": "QUESTION_TYPE",

    # 元信息结构
    "（共": "META_INFO",
    "小题，每题": "META_INFO",
    "分，共": "META_INFO",
    "分）": "META_INFO",

    # 结构元素
    "{单个任意汉字数字}、": "SECTION_INDEX",
    "{任意数字}.": "QUESTION_INDEX",
    "{任意数字}": "NUMBER",
    "{单个任意大写字母}.": "OPTION_LABEL",
    "{单个任意大写字母}": "OPTION_KEY",

    # 答案区
    "答案：": "ANSWER_TAG",
    "正确": "TF_ANSWER",
    "错误": "TF_ANSWER",

    # 文件结束符
    "$": "ENDMARK",

    # 其他普通文本
    "其他文本内容": "TEXT"
}

def tokenize_dfa(input_str):
    tokens = []
    i = 0
    length = len(input_str)
    line, col = 1, 1
    buffer = ""  # 收集非法匹配的部分

    def is_chinese_digit(ch):
        return ch in "一二三四五六七八九十零"

    def is_upper_letter(ch):
        return 'A' <= ch <= 'Z'

    def emit_token(t_type, value, line_no, col_no):
        tokens.append((t_type, value, line_no, col_no))

    while i < length:
        # 跳过空白字符（仅用于行列定位，不跳过内容）
        while i < length and input_str[i] in ' \t\n':
            if input_str[i] == '\n':
                line += 1
                col = 1
            else:
                col += 1
            i += 1
        if i >= length:
            break

        start_line, start_col = line, col

        # === 固定 Token 匹配 ===
        matched = False
        for literal, token_type in TOKEN_MAP.items():
            if literal.startswith("{"):
                continue
            if input_str.startswith(literal, i):  # 能匹配
                emit_token(token_type, literal, start_line, start_col)
                i += len(literal)
                col += len(literal)
                matched = True
                break
        if matched:
            continue

        # === 模板 Token 匹配 ===
        # SECTION_INDEX，要有汉字而且后面有顿号
        if i + 1 < length and is_chinese_digit(input_str[i]) and input_str[i + 1] == '、':
            emit_token("SECTION_INDEX", input_str[i:i + 2], start_line, start_col)
            i += 2
            col += 2
            continue

        # NUMBER or QUESTION_INDEX
        elif input_str[i].isdigit():
            start = i
            while i < length and input_str[i].isdigit(): # 数字没结束
                i += 1
                col += 1
            if i < length and input_str[i] == '.': # 遇到.则认为是小题号
                emit_token("QUESTION_INDEX", input_str[start:i + 1], start_line, start_col)
                i += 1
                col += 1
            elif i >= length or input_str[i] in " \t\n": # 遇到空格/换行则认为是数字
                emit_token("NUMBER", input_str[start:i], start_line, start_col)
            else: # 遇到其他字符认为是普通文本
                buffer += input_str[start:i]
                col -= (i - start)
            continue

        # OPTION_LABEL，匹配逻辑同大题号
        elif i + 1 < length and is_upper_letter(input_str[i]) and input_str[i + 1] == '.':
            emit_token("OPTION_LABEL", input_str[i:i + 2], start_line, start_col)
            i += 2
            col += 2
            continue

        # OPTION_KEY
        elif is_upper_letter(input_str[i]):
            if i + 1 >= length or input_str[i + 1] in " \t\n": # 单个字母才算选项
                emit_token("OPTION_KEY", input_str[i], start_line, start_col)
                i += 1
                col += 1
            else: # 否则认为是普通文本
                buffer += input_str[i]
                i += 1
            continue

        # ENDMARK
        elif input_str[i] == '$':
            emit_token("ENDMARK", "$", start_line, start_col)
            i += 1
            col += 1
            continue

        # === TEXT（合并 buffer 与剩余行内容） ===
        # 把 buffer 与剩余行内容合并
        else:
            start = i
            while i < length and input_str[i] != '\n':
                i += 1
                col += 1
            text = buffer + input_str[start:i].strip()
            if text:
                emit_token("TEXT", text, start_line, start_col)
            buffer = ""
            if i < length and input_str[i] == '\n':
                i += 1
                line += 1
                col = 1

    return tokens
