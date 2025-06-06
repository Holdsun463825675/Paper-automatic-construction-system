from collections import defaultdict
import pandas as pd

# 定义 LL(1) 形式的文法产生式
grammar_productions = {
    "试卷": [["标题", "说明", "题型列表", "ENDMARK"]],
    "标题": [["HEADER", "TEXT"]],
    "说明": [["HEADER", "TEXT"]],
    "题型列表": [["题型", "题型列表_续"]],
    "题型列表_续": [["题型", "题型列表_续"], ["ε"]],
    "题型": [["SECTION_INDEX", "QUESTION_TYPE", "分值说明", "题目列表"]],
    "分值说明": [["META_INFO", "NUMBER", "META_INFO", "NUMBER", "META_INFO", "NUMBER", "META_INFO"]],
    "题目列表": [["题目", "题目列表_续"]],
    "题目列表_续": [["题目", "题目列表_续"], ["ε"]],
    "题目": [["QUESTION_INDEX", "题干", "题尾"]],
    "题干": [["字符串"]],
    "题尾": [["选项列表", "答案"], ["答案"]],
    "选项列表": [["OPTION_LABEL", "答案值", "选项列表_续"]],
    "选项列表_续": [["OPTION_LABEL", "答案值", "选项列表_续"], ["ε"]],
    "答案": [["ANSWER_TAG", "答案值"]],
    "答案值": [["OPTION_KEY"], ["TEXT"], ["NUMBER"], ["TF_ANSWER"]],
    "整数": [["NUMBER"]],
    "正误": [["TF_ANSWER"]],
    "字符串": [["TEXT"]]
}

# 初始化集合
first_sets = defaultdict(set)
follow_sets = defaultdict(set)
non_terminals = set(grammar_productions.keys())
terminals = set()

# 计算 FIRST 集合：对 symbol 求可推出的首字符终结符集合
def compute_first(symbol):
    if symbol in terminals:
        return {symbol}
    if first_sets[symbol]:
        return first_sets[symbol]

    result = set()
    for rule in grammar_productions[symbol]: # 每个规则的每一项计算 first
        for item in rule:
            item_first = compute_first(item)
            result.update(item_first - {"ε"})
            if "ε" not in item_first:
                break
        else:
            result.add("ε")
    first_sets[symbol] = result
    return result

# 提取 FIRST 和 FOLLOW 集合
def get_first_follow_sets(grammar_productions):
    # 提取终结符（不在产生式左部出现的符号）
    for rules in grammar_productions.values():
        for rule in rules:
            for symbol in rule:
                if symbol not in grammar_productions:
                    terminals.add(symbol)

    # 计算 FIRST 集
    for non_terminal in non_terminals:
        compute_first(non_terminal)

    # 设置起始符号的 FOLLOW 集（加上 $）
    start_symbol = "试卷"
    follow_sets[start_symbol].add("$")

    # 使用迭代法计算 FOLLOW 集直到收敛
    changed = True
    while changed:
        changed = False
        # 遍历每条产生式
        for head, rules in grammar_productions.items():
            for rule in rules:
                # trailer 暂存 FOLLOW(head)，用于向右传播
                trailer = follow_sets[head].copy()
                # 从右向左遍历产生式右部
                for symbol in reversed(rule):
                    if symbol in non_terminals:
                        # 若 trailer 中有新元素添加到 FOLLOW(symbol)，则标记 changed
                        if not trailer.issubset(follow_sets[symbol]):
                            follow_sets[symbol].update(trailer)
                            changed = True
                        # 若 symbol 的 FIRST 集包含 ε，则 trailer 扩展为 FIRST(symbol) - {ε}
                        if "ε" in first_sets[symbol]:
                            trailer.update(first_sets[symbol] - {"ε"})
                        else:
                            # 否则 trailer 替换为 FIRST(symbol)
                            trailer = first_sets[symbol]
                    else:
                        # 若 symbol 为终结符，直接将其 FIRST 作为新的 trailer
                        trailer = compute_first(symbol)

    # 输出结果为排序后的字典（可打印）
    first_sets_out = {k: sorted(v) for k, v in first_sets.items()}
    follow_sets_out = {k: sorted(v) for k, v in follow_sets.items()}
    return first_sets_out, follow_sets_out

# 构建 LL(1) 预测分析表
def build_ll1_table(grammar_productions):
    ll1_table = defaultdict(dict)
    conflicts = []

    for A in grammar_productions:
        for rule in grammar_productions[A]:
            first_alpha = set()
            for symbol in rule:
                sym_first = compute_first(symbol)
                first_alpha.update(sym_first - {"ε"})
                if "ε" not in sym_first:
                    break
            else:
                first_alpha.add("ε")

            for terminal in first_alpha:
                if terminal == "ε":
                    for b in follow_sets[A]:
                        if b in ll1_table[A]:
                            conflicts.append((A, b))  # 冲突检测
                        ll1_table[A][b] = rule
                else:
                    if terminal in ll1_table[A]:
                        conflicts.append((A, terminal))  # 冲突检测
                    ll1_table[A][terminal] = rule

    # 可视化为 Pandas 表格
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_colwidth", None)
    pd.set_option("expand_frame_repr", False)

    all_terminals = sorted(terminals)
    all_non_terminals = sorted(non_terminals)
    ll1_df = pd.DataFrame(index=all_non_terminals, columns=all_terminals)

    for A in ll1_table:
        for a in ll1_table[A]:
            ll1_df.at[A, a] = ' '.join(ll1_table[A][a])

    ll1_df = ll1_df.fillna("")

    return ll1_table, ll1_df


# LL(1) 分析器类定义
class MyParser:
    def __init__(self):
        get_first_follow_sets(grammar_productions)
        self.ll1_table, self.ll1_df = build_ll1_table(grammar_productions)
        self.start_symbol = "试卷"
        self.stack = [] # 给一个分析栈
        self.analysis_log = []
        self.ast = {
            "title": None,
            "instruction": None,
            "types": []
        }
        self.temp_state = {
            "last_type": None,
            "last_question": None,
            "current_option": None
        }

    def parse(self, tokens):
        # 初始化分析栈：从起始符号开始，底部是 $ 表示栈结束
        self.stack = ["$", self.start_symbol]

        # 给输入 token 序列末尾添加结束标志符 $
        tokens.append(("$", "$", -1, -1))

        idx = 0  # 当前读入 token 的下标
        success = True  # 标记是否成功通过语法分析
        self.analysis_log = []  # 记录匹配/推导/错误信息
        error_summary = []  # 错误汇总信息用于最终提示

        while self.stack:
            top = self.stack.pop() # 取栈顶元素
            current_token, current_value, token_line, token_col = tokens[idx]
            pos_info = f"(行{token_line}, 列{token_col})" if token_line != -1 and token_col != -1 else ""

            if top == "$" and current_token == "$": # 是结束符就结束
                break

            elif top in terminals: # 是终结符
                if top == current_token:
                    # 匹配成功：记录匹配并构建语法树节点
                    self.analysis_log.append(f"[匹配] {top} -> '{current_value}' {pos_info}")
                    self._update_ast(top, current_value, tokens, idx)  # 匹配项加入到AST中
                    idx += 1
                else:
                    # 匹配失败：记录错误并跳过当前输入 token，同时尝试保留 top 再次尝试
                    self.analysis_log.append(
                        f"[错误] 缺少 '{top}'，但当前输入为 '{current_token}' ('{current_value}')，跳过输入 {pos_info}")
                    error_summary.append(f"{pos_info} 期望终结符 {top}，但发现 {current_token}")
                    success = False
                    idx += 1
                    if idx >= len(tokens): break
                    self.stack.append(top) # 重新压入栈顶符号以等待下一轮匹配
                    continue

            elif top in non_terminals: # 是非终结符
                production = self.ll1_table.get(top, {}).get(current_token)
                if production: # 存在表项，则进行推导
                    self.analysis_log.append(f"[推导] {top} -> {' '.join(production)} {pos_info}")
                    for symbol in reversed(production): # 倒序压栈
                        if symbol != "ε":
                            self.stack.append(symbol)
                else: # 不存在表项，则记录错误，进行错误处理，跳过当前输入直到找到 FOLLOW(top) 中的某符号
                    self.analysis_log.append(
                        f"[错误] 非终结符 {top} 无法匹配当前输入 {current_token} ('{current_value}') {pos_info}")
                    expected_set = first_sets.get(top, set()) | follow_sets.get(top, set())
                    expected_str = ', '.join(sorted(expected_set))
                    error_summary.append(
                        f"{pos_info} 非终结符 {top} 匹配失败，期望 FIRST/FOLLOW 中的一个：{{{expected_str}}}，但遇到 {current_token}"
                    )
                    # 错误处理：跳过输入直到找到 FOLLOW(top) 中的某符号
                    follow = follow_sets.get(top, set())
                    while current_token != "$" and current_token not in follow:
                        self.analysis_log.append(
                            f"  → 跳过非法输入 '{current_value}'，等待 FOLLOW({top}) 中的符号 {pos_info}")
                        idx += 1
                        if idx >= len(tokens): break
                        current_token, current_value = tokens[idx][:2]
                        token_line = tokens[idx][2]
                        token_col = tokens[idx][3]
                        pos_info = f"(行{token_line}, 列{token_col})" if token_line != -1 and token_col != -1 else ""
                    # 弹出该非终结符，尝试恢复分析
                    self.analysis_log.append(f"  → 弹出非终结符 {top}，尝试恢复")
                    success = False
                    continue

            else: # 既不是终结符也不是非终结符的额外处理
                self.analysis_log.append(f"[错误] 无法识别的栈顶符号 {top}")
                error_summary.append(f"无法识别的分析栈符号：{top}")
                success = False
                break

        result_message = "通过语法分析！" if success else "存在语法错误：\n" + "\n".join(f"- {msg}" for msg in error_summary)
        return self.ll1_df, success, self.analysis_log, result_message, self.ast

    # AST 构建函数
    def _update_ast(self, token_type, token_value, tokens, idx):
        # 如果当前 token 是 HEADER（标题或说明标识）
        if token_type == "HEADER":
            # 获取当前 token 后面的一个值（作为标题或说明）
            next_val = tokens[idx + 1][1] if idx + 1 < len(tokens) else ""
            # 如果 ast 中还没有设置标题，则设为标题
            if self.ast["title"] is None:
                self.ast["title"] = next_val
            # 如果已有标题但没有说明，则设为说明
            elif self.ast["instruction"] is None:
                self.ast["instruction"] = next_val

        # 如果当前 token 是 SECTION_INDEX（例如“一、二、三”）
        elif token_type == "SECTION_INDEX":
            # 新建一个大题类型结构体，并暂存为 last_type
            self.temp_state["last_type"] = {
                "type": None,  # 大题类型名称（如“选择题”）
                "count": 0,  # 小题数
                "each_score": 0,  # 每小题分值
                "total": 0,  # 总分
                "questions": []  # 小题列表
            }
            # 将该大题结构加入 AST 中的 types 列表
            self.ast["types"].append(self.temp_state["last_type"])

        # 如果当前 token 是 QUESTION_TYPE（如“选择题”）
        elif token_type == "QUESTION_TYPE":
            # 设置最近一次的大题类型名称
            self.temp_state["last_type"]["type"] = token_value

        # 如果当前 token 是 NUMBER（数值，表示题数、每题分、总分）
        elif token_type == "NUMBER":
            lt = self.temp_state["last_type"]
            # 第一个数字是 count（题目数量）
            if lt["count"] == 0:
                lt["count"] = int(token_value)
            # 第二个是 each_score（每题分值）
            elif lt["each_score"] == 0:
                lt["each_score"] = int(token_value)
            # 第三个是 total（总分）
            elif lt["total"] == 0:
                lt["total"] = int(token_value)

        # 如果当前 token 是 QUESTION_INDEX（小题编号，如“1.”）
        elif token_type == "QUESTION_INDEX":
            # 新建小题结构体，并暂存为 last_question
            q = {"id": token_value, "text": "", "options": {}, "answer": ""}
            self.temp_state["last_question"] = q
            # 添加到当前大题类型的 questions 列表中
            self.temp_state["last_type"]["questions"].append(q)

        # 如果当前 token 是 TEXT（正文文本，包括题干、选项、答案）
        elif token_type == "TEXT":
            q = self.temp_state["last_question"]
            # 如果当前处于选项标记状态，则将该文本设为该选项内容
            if self.temp_state.get("current_option"):
                q["options"][self.temp_state["current_option"]] = token_value
                self.temp_state["current_option"] = None
            # 否则，如果题干为空，则设为题干
            elif q and not q["text"]:
                q["text"] = token_value
            # 否则，如果答案为空，则设为答案
            elif q and not q["answer"]:
                q["answer"] = token_value

        # 如果当前 token 是 OPTION_LABEL（如“A.”）
        elif token_type == "OPTION_LABEL":
            # 将当前选项标识保存，等待下一条 TEXT 作为其内容
            self.temp_state["current_option"] = token_value.strip(".")

        # 如果当前 token 是 OPTION_KEY（如“答案：B”）
        elif token_type == "OPTION_KEY":
            q = self.temp_state["last_question"]
            # 直接设为答案（选择题）
            if q:
                q["answer"] = token_value

        # 如果当前 token 是 TF_ANSWER（判断题答案：“正确”或“错误”）
        elif token_type == "TF_ANSWER":
            q = self.temp_state["last_question"]
            # 直接设为答案
            if q:
                q["answer"] = token_value


