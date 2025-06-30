# Paper-automatic-construction-system (试卷自动构建系统)
这是武汉大学编译原理课程大作业的一个选题，难度系数为1.2，需要完成词法分析、语法分析、语义分析、代码生成、组卷等功能。

词法分析器、语法分析器、语义分析器分别在Lexer、Parser、SemanticAnalyzer文件夹内，每个文件夹内还有个test.py文件用于单个分析器的测试。

Analysis_Result文件夹用于存放分析器的分析结果。

Test_Case文件夹存放了与测试用例有关的文件，包括测试用例文件、读取测试用例等。

代码生成器在CodeGeneration文件夹内，其生成结果存放在Generation_result内。

组卷系统在AutomaticPaper文件夹内，其中包含实现函数与供组卷的题库。

外部两个main（main_test、main_generation_paper，分别进行分析器测试、组卷系统的运行）可直接运行。

有py环境可直接运行！！！
