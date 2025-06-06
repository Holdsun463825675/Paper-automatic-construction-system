import os
def Ast2MarkDown(ast, show_answer=True):
    os.makedirs("Generation_result", exist_ok=True)

    def escape_md(text):
        # 转义字符特殊处理
        for ch in ['#', '*', '_', '-', '`']:
            text = text.replace(ch, f"\\{ch}")
        return text

    # 上标题和说明
    lines = []
    lines.append(f"# {escape_md(ast.get('title', ''))}")
    lines.append("")
    lines.append(escape_md(ast.get("instruction", "")))
    lines.append("")

    cn_index_list = "一二三四五六七八九十"

    # 遍历每大题
    for idx, qtype in enumerate(ast.get("types", []), 1):
        # 提取题型名、小题数、小题分、总分
        type_name = qtype.get("type", "")
        count = qtype.get("count", 0)
        each_score = qtype.get("each_score", 0)
        total = qtype.get("total", 0)
        cn_index = cn_index_list[idx - 1] if idx <= len(cn_index_list) else str(idx)

        lines.append(f"## {cn_index}、{type_name}（共{count}题，每题{each_score}分，共{total}分）")
        lines.append("")

        # 遍历每小题
        for question in qtype.get("questions", []):
            # 提取小题号、小题干、选项（如有）和答案
            qid = question.get("id", "").strip('.')
            qtext = escape_md(question.get("text", ""))
            options = question.get("options", {})
            answer = escape_md(question.get("answer", ""))

            lines.append(f"**{qid}. {qtext}**")

            # 假如有选项，则添加选项信息
            if options:
                for label in sorted(options.keys()):
                    opt = escape_md(options[label])
                    lines.append(f"- **{label}.** {opt}")

            # 根据参数决定是否显示答案
            if show_answer:
                lines.append("")
                lines.append(f"**答案：** {answer}")
            lines.append("")

    md_output = "\n".join(lines)

    # 分别生成有无答案两个版本
    if show_answer:
        save_dir = "Generation_result/exam_answer.md"
    else:
        save_dir = "Generation_result/exam_no_answer.md"
    with open(save_dir, "w", encoding="utf-8") as f:
        f.write(md_output)

    print(f"Markdown 文件已生成：{save_dir}")
