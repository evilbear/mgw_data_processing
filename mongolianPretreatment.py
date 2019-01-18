#!/usr/bin/python3
# -*- coding: utf-8 -*-
# **************************
# * Author      :  evilbear
# * Email       :  evilbear@live.cn
# * Dependency  :  zeep, urllib3 and beautifulsoup4
# * Description :  Pretreatment Mongolian sentence, including coding conversion, text proofreading,
#                  punctuation processing, suffix spliting and segmentation of sentence.
#                  Entry function: pretreatmentSentence() or pretreatmentFile()
# * create time :  21/12/2018
# * file name   :  mongolianPretreatment.py

import re, math
from zeep import Client
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def conversion(line):
    """Convert Menksoft coded mongolian to Unicode.
       By using the services provided by College of Computer Science,
       Inner Mongolia University,Inner Mongolia Mongolian Information Processing Laboratory.
       URL: http://mtg.mglip.com/
    Args:
        line: A Menksoft coded mongolian sentence.
    Returns:
        A Unicode mongolian sentence.
    Raises:
        Error: Empty string, ''.
    """
    try:
        url = 'http://mtg.mglip.com/'
        # Web interface parameters.
        params = urlencode({
                            '__VIEWSTATE':'/wEPDwULLTEyMjA2MDAyOTJkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYCBRFCdXR0b25UcmFuX0lEQmFjawUNQnV0dG9uVHJhbl9JRPCzb3uVDl5G8nD1zvyUhU5wMUnbC2zYh3+8Wld2ogB2',
                            '__EVENTVALIDATION':'/wEdAAU30dcFl6Eqz9lyNLRaEnQ5Taw2keI+7zV+INMO8AHzSUHIbZyaqTF+z9onQgXSv3QGd75SsxXhlZrnKIv47ot/SFXHjTDBqsCa3dYPptywffSmvx+0qadnMZ/QXHQ6lJoNQ/nGVxuVrJSpK02v6qy6',
                            'inputCyrillic_ID':line,
                            'ButtonTran_ID.x':28,
                            'ButtonTran_ID.y':10
                            }).encode('utf-8')
        headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        req = Request(url=url,data=params,headers=headers)
        response = urlopen(req)
        soup = BeautifulSoup(response,'html.parser',from_encoding='utf-8')
        links = soup.find_all('textarea',id='outPutTraditonalM_ID')
        result = ""
        for link in links:
            result += link.get_text()
        return result.strip()
    except:
        return ''

def textProofreading(line):
    """Call interface for Mongolian text proofreading.
       By using the services provided by College of Computer Science,
       Inner Mongolia University,Inner Mongolia Mongolian Information Processing Laboratory.
       URL: http://mc.mglip.com:8080/
       reList[2] corresponds to Proofreading results.
    Args:
        line: A Menksoft coded mongolian sentence.
    Returns:
        A Proofreading mongolian sentence.
    """
    client = Client('http://202.207.12.187/newChecker/PortFunctionPort?wsdl')
    try:
        result = client.service.function(line)
        reList = result.split(r'/**/')
        return reList[2]
    except:
        return ""

def processPunctuation(line, split202F=False):
    """Unify punctuation in the sentence and separate punctuation from words.
       Spliting suffix by U+202F, remove extra spaces.
       Mongolian control symbols that need to be noted: {'U+202F':" ", 'U+200C':"‌", 'U+200D':"‍", 'U+180A':"᠊", 'U+180B':"᠋", 'U+180C':"᠌", 'U+180D':"᠍", 'U+180E':"᠎"}
    Args:
        line: A Menksoft coded mongolian sentence.
        split202F: Whether to perform the processing of the segmentation U+202F.
    """
    # Unify punctuation
    original_punctuation = ['︵', '︶', '（', '）', '《', '》', '︿', '﹀', '【', '】', '﹇', '﹈', '〔', '〕', '“', '”', '，', '︔', '︖', '︕', '●', '', '•', '', '－', '—', '％', '：', ' ', '　', '']
    replace_punctuation = ['(', ')', '(', ')', '︽', '︾', '〈', '〉', '[', ']', '[', ']', '[', ']', '"', '"', ',', ';', '?', '!', '·', '·', '·', '–', '–', '–', '%', ':', ' ', ' ', '᠃']
    for (i_original, i_replace) in zip(original_punctuation, replace_punctuation):
        line = re.sub(i_original, i_replace, line)
    # Separate punctuation from words.
    # "( ) ? + * [" have a special usage in re, need to add escape char '\'.
    mgw_punctuation = ['᠀', '᠁', '᠂', '᠃', '᠄', '᠅', '᠆', '᠇', '᠈', '᠉', '᠊']
    common_punctuation = ['\(', '\)', '\?', '\+', '\*', '\[', ']', '︽', '︾', '〈', '〉', '"', ',', ';', '!', '-', '/', '。', '、', ':', '<', '>', '︱', '—', '', '·']
    for i_punctuation in (mgw_punctuation + common_punctuation):
        # " " is a space. Need to remove escape char '\' here.
        temp_replace = " " + i_punctuation[-1] + " "
        line = re.sub(i_punctuation, temp_replace, line)
    if split202F:
        line = re.sub(" ", "  ", line)#Front is space. Back is space + 202F.
    line = re.sub(" +", " ", line)#Both are space.
    line = re.sub("〈 〈", "︽", line)
    line = re.sub("〉 〉", "︾", line)
    return line

def splitSentence(line):
    """Segmentation of sentences by punctuation
       Do not handle newline symbols in parentheses
       Do not split two consecutive newline symbols, such as ?!
    """
    line = line.strip()
    split_punctuation = ['᠁', '\?', '᠃', '᠅', '᠉', '!', '。']
    for i_punctuation in split_punctuation:
        temp_replace = i_punctuation[-1] + "\n"
        line = re.sub(i_punctuation + " ", temp_replace, line) # " " is a space.
    line = re.sub("\n+", "\n", line)
    punctuation = ['᠀', '᠁', '᠂', '᠃', '᠄', '᠅', '᠆', '᠇', '᠈', '᠉', '᠊', '(', ')', '?', '+', '*', '[', ']', '︽', '︾', '〈', '〉', '"', ',', ';', '!', '-', '/', '。', '、', ':', '<', '>', '︱', '—', '', '·']
    line_list = line.strip().split("\n")
    # Delete rows with only punctuation.
    sentence = ""
    for i, i_line in enumerate(line_list):
        state = False
        # Determine if it is the split punctuation between parentheses.
        for left, right in zip(['\(', '\[', '︽', '〈', '<'], ['\)', '\]', '︾', '〉', '>']):
            string = "^[^{}]+{}".format(left, right)
            if re.search(string, i_line):
                state = True
        if state:
            sentence += ' ' + line_list[i].strip()
        else:
            # If there is only punctuation after split, then cancel split.
            i_line = i_line.strip().split(" ") # " " is a space.
            if set(i_line) - set(punctuation):
                sentence += '\n' + line_list[i].strip()
            else:
                sentence += ' ' + line_list[i].strip()
    sentence = re.sub(" +", " ", sentence)#Both are space.
    return sentence.strip()

def pretreatmentSentence(line, menk2unicode=True, split202F=False):
    """This is entry function, processing snetences.
    Args:
        line: A mongolian sentence.
        menk2unicode: When the input sentence is Unicode, no need to conversion, set to False.
        split202F: Whether to perform the processing of the segmentation U+202F.
    Returns:
        Mongolian sentence after processing.
    """
    if menk2unicode:
        line = conversion(line)
    line = textProofreading(line)
    line = processPunctuation(line, split202F)
    line = splitSentence(line)
    return line

def pretreatmentFile(inFilePath, outFilePath, num=50, deduplication=False, menk2unicode=True, split202F=False):
    """This is entry function, processing file.
    Args:
        inFilePath: Input text path.
        outFilePath: output text path.
        num: Number of sentences processed in parallel.
        deduplication: Whether to perform deduplication.
        menk2unicode: When the input sentence is Unicode, no need to conversion, set to False.
        split202F: Whether to perform the processing of the segmentation U+202F.
    """
    sentence_list = list()
    with open(inFilePath, 'r') as fr:
        for line in fr:
            line = line.strip()
            if line:
                sentence_list.append(line)
    if deduplication:
        sentence_list = list(set(sentence_list))
    batch = math.ceil(len(sentence_list) / num)
    data = list()
    for i_batch in range(batch):
        start = num * i_batch
        line = "\n".join(sentence_list[start : start+num])
        line = pretreatmentSentence(line, menk2unicode, split202F)
        data.extend(line.split('\n'))
    if deduplication:
        data = set(data)
    with open(outFilePath, 'a') as fa:
        for line in data:
            if line.strip():
                fa.write(line.strip() + '\n')