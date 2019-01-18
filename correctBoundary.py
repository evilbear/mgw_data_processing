#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, re

# 校正人工标注实体边界误差
def CorrectBoundaryError(inFilePath, outFilePath):
    fw = open(outFilePath, "w")
    with open(inFilePath, "r") as fr:
        for line in fr:
            # 处理标签中的标点符号; 数字是匹配的次数
            line = re.sub("᠃\s\]", " ] ᠃ ", line) # 5
            line = re.sub("᠂\s\]", " ] ᠂ ", line) # 158
            line = re.sub("\[\s(PER|GPE|OGR)\s᠂", lambda x: " ᠂ [ "+x.group(1), line) # 189
            line = re.sub("·\s\]", " ] · ", line) # 3
            line = re.sub("\[\s(PER|GPE|OGR)\s·", lambda x: " · [ "+x.group(1), line) # 5; 人工校对对应原文件的第28687行
            line = re.sub("\[\sMoney([^\[\]]+)\]", lambda x: x.group(1), line) # 46
            line = re.sub("(\[\sPER[^\[\]]+)᠂([^\[\]]+\])", lambda x: x.group(1)+"·"+x.group(2), line) # 63
            # 下面的需要人工判断
            # (\[\sOGR[^\[\]]+)᠂([^\[\]]+\]) # 7; 删除逗号; 删除对应原文件的10814行
            # (\[\sGPE[^\[\]]+)᠂([^\[\]]+\]) # 1; 删除逗号
            # \[[^\[\]]+[︽|︾][^\[\]]+\] # 82; 处理︽和︾在人工标注时被手误分开问题; 删除对应原文件的4565和15947行
            fw.write(line)
    fw.close()

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'allmergetxt-org-GB.txt')
save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'allmergetxt-org-GB-Correction.txt')
CorrectBoundaryError(data_path, save_path)