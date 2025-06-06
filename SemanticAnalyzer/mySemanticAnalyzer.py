class MySemanticAnalyzer:
    chinese_digits = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]

    def __init__(self):
        self.ast = None
        self.errors = []

    def check(self, ast): # 语义分析，结构性检查、内容性检查
        self.ast = ast

        self.errors.clear()

        self.ast = ast
        if not ast:
            self.errors.append("[错误] AST 为空")
            return

        self.check_sections()

        if self.errors:
            return False
        return True

    def check_sections(self):
        seen_type_names = set()
        expected_chinese_index = 0
        expected_question_number = 1

        # 结构性检查
        for idx, section in enumerate(self.ast["types"]):
            type_name = section.get("type")
            section_id = self.chinese_digits[expected_chinese_index] if expected_chinese_index < len(self.chinese_digits) else f"未知({idx})"

            # 大题编号递增
            expected_chinese_index += 1

            # 大题名称重复检查
            if type_name in seen_type_names:
                self.errors.append(f"[错误] 出现重复的大题名称：{type_name}")
            else:
                seen_type_names.add(type_name)

            # 分值说明合理性（计算是否正确）
            declared_count = section.get("count", 0)
            declared_each = section.get("each_score", 0)
            declared_total = section.get("total", 0)
            real_questions = section.get("questions", [])

            if declared_count != len(real_questions): # 小题数对应
                self.errors.append(f"[错误] {type_name} 小题数声明为 {declared_count}，但实际为 {len(real_questions)}")
            if declared_count * declared_each != declared_total: # 分值计算验证
                self.errors.append(f"[错误] {type_name} 总分声明为 {declared_total}，但 {declared_count} × {declared_each} = {declared_count * declared_each}")

            for qidx, q in enumerate(real_questions):
                qid = q.get("id", "").strip(".")
                try:
                    qnum = int(qid)
                    if qnum != expected_question_number: # 小题号是否递增
                        self.errors.append(f"[错误] 小题号应为 {expected_question_number}，但出现了 {qid}.")
                    expected_question_number += 1
                except ValueError: # 小题号不是数字
                    self.errors.append(f"[错误] 无法识别的小题号：{qid}")

                # 内容性检查：检查题干、答案等
                if not q.get("text"):
                    self.errors.append(f"[错误] 第 {qid} 题缺失题干")
                if type_name == "选择题":
                    self._check_options(q, type_name, qid)
                elif type_name == "判断题":
                    self._check_tf_answer(q, qid)

    # 内容性检查，选择题：选项数量、顺序，答案是否合理
    def _check_options(self, question, type_name, qid):
        options = question.get("options", {})
        answer = question.get("answer", "")

        if not isinstance(options, dict) or len(options) < 2:
            self.errors.append(f"[错误] 第 {qid} 题为选择题，但选项不足两个")

        sorted_keys = sorted(options.keys())
        expected_keys = [chr(ord('A') + i) for i in range(len(sorted_keys))]

        if sorted_keys != expected_keys:
            self.errors.append(f"[错误] 第 {qid} 题选项顺序应为 {expected_keys}，实际为 {sorted_keys}")

        if answer not in options:
            self.errors.append(f"[错误] 第 {qid} 题答案 '{answer}' 不在选项中")

    # 内容性检查，判断题：答案是否合理
    def _check_tf_answer(self, question, qid):
        answer = question.get("answer", "")
        if answer not in ["正确", "错误"]:
            self.errors.append(f"[错误] 第 {qid} 题为判断题，但答案为非法值：{answer}")

    def report(self):
        if not self.errors:
            print("未发现语义错误")
        else:
            print("存在语义错误：")
            for e in self.errors:
                print(f"  - {e}")
