import os

def getTest(test_id):
    """
    0.txt: 完全正确，无语法错误，无语义错误
    1.txt: 语法错误，缺失头部信息
    2.txt: 语法错误，缺失大题标号
    3.txt: 语法错误，缺失小题标号
    4.txt: 语法错误，缺失部分选项或答案标记
    5.txt: 语法错误，缺失部分题干
    6.txt: 语法错误，缺失大题干分值信息
    7.txt: 语法错误，缺失答案
    8.txt: 语法错误，缺失头部信息、大小题标号、部分选项或答案、部分题干、分值信息
    9.txt: 语义错误，大题重复
    10.txt: 语义错误，题号未递增
    11.txt: 语义错误，分值说明不合理
    12.txt: 语义错误，选择题选项不足
    13.txt: 语义错误，选择题与判断题答案不合理
    14.txt: 语义错误，大题重复、题号未递增、分值说明不合理、选择题选项不足、选择题与判断题答案不合理
    """
    filepath = os.path.join(f"Test_Case/{test_id}.txt")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"测试文件不存在: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return content
