import os

def Ast2Latex(ast, show_answer=True):
    os.makedirs("Generation_result", exist_ok=True)

    def escape_latex(text):
        # 转义字符特殊处理
        replacements = {
            '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
            '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
            '^': r'\^{}',
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    # 添加相应依赖包
    lines = []
    lines.append(r"\documentclass[12pt]{article}")
    lines.append(r"\usepackage{ctex}")
    lines.append(r"\usepackage{geometry}")
    lines.append(r"\usepackage{enumitem}")
    lines.append(r"\geometry{a4paper, margin=2.5cm}")
    lines.append(r"\begin{document}")

    # 上标题和说明
    title = escape_latex(ast.get("title", ""))
    instruction = escape_latex(ast.get("instruction", ""))
    lines.append(r"\begin{center}")
    lines.append(r"\LARGE\textbf{%s}" % title)
    lines.append(r"\end{center}")
    lines.append(r"\vspace{0.5cm}")
    lines.append(instruction)
    lines.append(r"\vspace{0.5cm}")

    # 遍历每大题
    for idx, qtype in enumerate(ast.get("types", []), 1):
        # 提取题型名、小题数、小题分、总分
        type_name = escape_latex(qtype.get("type", ""))
        count = qtype.get("count", 0)
        each_score = qtype.get("each_score", 0)
        total = qtype.get("total", 0)
        cn_index = "一二三四五六七八九十"[idx - 1]

        lines.append(r"\section*{%s、%s（共%d题，每题%d分，共%d分）}" %
                     (cn_index, type_name, count, each_score, total))

        # 遍历每小题
        for question in qtype.get("questions", []):
            # 提取小题号、小题干、选项（如有）和答案
            qid = escape_latex(question.get("id", "").strip('.'))
            qtext = escape_latex(question.get("text", ""))
            options = question.get("options", {})
            answer = escape_latex(question.get("answer", ""))

            lines.append(r"\noindent\textbf{%s.} %s\\[0.2em]" % (qid, qtext))

            # 假如有选项，则添加选项信息
            if options:
                lines.append(r"\begin{itemize}[label=~]")
                for label in sorted(options):
                    opt_text = escape_latex(options[label])
                    lines.append(r"\item[\textbf{%s.}] %s" % (label, opt_text))
                lines.append(r"\end{itemize}")

            # 根据参数决定是否显示答案
            if show_answer:
                lines.append(r"\textbf{答案：} %s\\[0.5em]" % answer)
            else:
                lines.append(r"\vspace{0.5cm}")

            # lines.append(r"\vspace{0.5cm}")

    lines.append(r"\end{document}")

    tex_code = "\n".join(lines)

    # 分别生成有无答案两个版本
    if show_answer:
        save_dir = "Generation_result/exam_answer.tex"
    else:
        save_dir = "Generation_result/exam_no_answer.tex"
    with open(save_dir, "w", encoding="utf-8") as f:
        f.write(tex_code)

    print(f"Latex 文件已生成：{save_dir}")
