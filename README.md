# INTRODUCE
蒙古文语料预处理相关内容。
考虑到标注语料的版权为内蒙古大学计算机学院所有，本人不会也不能公开。

## Process
1. 校正人工标注实体边界误差
> python correctBoundary.py 和一些人工校对
2. 对标注和无标注语料进行预处理
> python processing.py --inFilePath="allmergetxt-org-GB-Correction.txt" --outFilePath="data.txt" --deduplication=True --menk2unicode=False --split202F=True
    因在人工标注后后进行蒙古文校正，出现如“[ PERᠳᠦ”这种情况，使用正则匹配“\[\s(GPE|OGR|PER)[^\s]+”出现85次，人工分隔
> python processing.py --inFilePath="data_none.txt" --outFilePath="unlabel.txt" --deduplication=True --menk2unicode=False --split202F=True
3. 语料的相应预处理操作，准备实验所需文件，如：5折交叉验证数据集，词表，词向量表等
> python corpusPreprocessingFunctions.py


## FILE
allmergetxt-org-GB.txt 原始标注语料 25.8MB 33209句
allmergetxt-org-GB-Correction.txt 对allmergetxt-org-GB.txt的实体边界进行校正 25.8MB 33207句
data.txt 对allmergetxt-org-GB-Correction.txt进行预处理后获得 26.2MB 34519句	PER:12408个; ORG:18639个; LOC:28104个
corpus.txt 处理成CONLL2003格式的标注数据，BIOES标签
label.txt 把标注语料去标签处理成无标注语料
words_label.txt label.txt统计出来的词频表
corpus文件夹 把corpus.txt中词数超300的句子删除，后随机打乱，剩下34433句 PER:12170个; ORG:17690个; LOC:27279个 将其划分成5折交叉验证数据集
    part0.txt 6887句   PER:2501个; ORG:3525个; LOC:5510个
    part1.txt 6887句   PER:2509个; ORG:3593个; LOC:5336个
    part2.txt 6887句   PER:2299个; ORG:3410个; LOC:5414个
    part3.txt 6887句   PER:2461个; ORG:3473个; LOC:5513个
    part4.txt 6885句   PER:2400个; ORG:3689个; LOC:5506个

data_none.txt 通过蒙古语新闻网站爬取的无标注语料 371.2MB 733955句
unlabel.txt 对data_none.txt进行预处理后获得 347MB 570733句
words_unlabel.txt unlabel.txt统计出来的词频表
none.txt 把标注语料添加进无标注语料中，进行去重和随机打乱顺序 372.5MB 604867句
words_none.txt 由none.txt统计出来的词频表

words.txt 使用words_none.txt中频次>=3的单词 68384个
    添加 $UNK$:未登录词; $NUM$:替代数字; $EOS$:在训练LM时，做句子结尾标记

chars.txt 蒙古文字符1800-18AF和一些统计出来的高频字符 219个
    添加 $UNK$:未登录词; $NUM$:替代数字

tags.txt NER标签BIOES

glove_vectors.txt 对none.txt使用Glove训练获得，频次3，维度300，窗口15

word2vec_vectors.txt 对none.txt使用word2vec训练获得，频次3，维度300

monglianPretreatment.py 蒙古语预处理函数

processing.py 入口文件

corpusPreprocessingFunctions.py 语料准备函数

convert.py 标记转换(BIO->BIOES) By JieYang
    > python convert.py "BIO2BIOES" inFilePath outFilePath

GloVe-master 斯坦福的Glove开源工具包，参数配置在demo.sh中
    (http://github.com/stanfordnlp/glove)

## DEPENDENCY
> zeep：pip install zeep
> urllib3：pip install urllib3
> beautifulsoup4：pip install beautifulsoup4
> word2vec：conda install word2vec
    说明：使用pip安装word2vec失败，没有进一步尝试。因为实验使用的anaconda版本python，使用conda安装成功

## ATTENTION
实验中可能会遇到的BUG：
问题1：在执行"> python corpusPreprocessingFunctions.py"时，可能报如下错误
    """
    mkdir -p build
    gcc src/glove.c -o build/glove -lm -pthread -Ofast -march=native -funroll-loops -Wno-unused-result
    /tmp/cc6xkKuG.o: In function `glove_thread':
    glove.c:(.text+0xe6b): undefined reference to `check_nan'
    glove.c:(.text+0xeab): undefined reference to `check_nan'
    collect2: error: ld returned 1 exit status
    make: *** [Makefile:12: glove] Error 1
    """
描述：本人使用anaconda的source activate虚拟环境做开发，在用python执行Glove-master的shell脚本时报错。
    # os.system("cd GloVe-master; sh demo.sh") 对应代码中trainVectors()函数内
    原因待分析。
解决：退出虚拟环境，直接执行
    > python3.6 corpusPreprocessingFunctions.py
    本人python3.6对应anaconda的python，包含conda安装的word2vec，执行成功。
    如报word2vec缺失，请切换python版本或研究如何给指定版本安装word2vec。

问题2：在执行"> python corpusPreprocessingFunctions.py"时，可能报python3错误
描述：定位corpusPreprocessingFunctions.py中第234-236行，如下。使用os模块执行终端命令
    # > python convert.py "BIO2BIOES" "data_temp.txt" "corpus.txt"
    command = "python3 {0} 'BIO2BIOES' {1} {2}".format(convert_path, data_temp_path, corpus_path)
    os.system(command)
解决：可能终端中没有配置名为“python3”的环境，可以对代码中的“python3”进行相应修改。

## RESOURCE
蒙古文字符百科：https://unicode-table.com/cn/blocks/mongolian/
蒙古文校正：http://mc.mglip.com:8080/
蒙科立转国标码：http://mtg.mglip.com/
蒙古文翻译：http://fy.mglip.com/
需要被注意的蒙古语控制符:
    {'U+202F':" ", 'U+200C':"‌", 'U+200D':"‍", 'U+180A':"᠊", 'U+180B':"᠋", 'U+180C':"᠌", 'U+180D':"᠍", 'U+180E':"᠎"}
