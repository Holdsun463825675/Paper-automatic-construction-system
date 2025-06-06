from AutomaticPaper.autoGeneration import auto_generation

def input_int(prompt, default):
    try:
        val = input(f"{prompt}（默认 {default}）：").strip()
        return int(val) if val else default
    except ValueError:
        print("请输入有效整数！使用默认值。")
        return default

def input_bool(prompt, default=True):
    val = input(f"{prompt}（Y/n，默认 {'Y' if default else 'N'}）：").strip().lower()
    return default if val == '' else val in ('y', 'yes')

def build_structure_config():
    print("请输入试卷结构设置：")
    title = "编译原理试题"
    instruction = "请完成以下试题"

    structure_config = {
        "title": title,
        "instruction": instruction,
        "选择题": {
            "count": input_int("选择题数量（1-20）", 2),
            "score": input_int("选择题每题分值", 10)
        },
        "填空题": {
            "count": input_int("填空题数量（1-20）", 1),
            "score": input_int("填空题每题分值", 10)
        },
        "判断题": {
            "count": input_int("判断题数量（1-20）", 1),
            "score": input_int("判断题每题分值", 10)
        },
        "简答题": {
            "count": input_int("简答题数量（1-20）", 0),
            "score": input_int("简答题每题分值", 10)
        }
    }
    return structure_config

def build_advanced_config():
    print("\n请输入高级生成配置：")
    return {
        "shuffle_sections": input_bool("是否打乱大题顺序", True),
        "shuffle_questions": input_bool("是否打乱小题顺序", True),
        "shuffle_options": input_bool("是否打乱选择题选项顺序（自动调整答案）", True)
    }

if __name__ == "__main__":
    print("欢迎使用自动组卷系统")
    structure_config = build_structure_config()
    advanced_config = build_advanced_config()
    print("\n开始生成试卷...\n")
    auto_generation(structure_config, advanced_config)
