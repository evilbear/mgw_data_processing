#!/usr/bin/python3
# -*- coding: utf-8 -*-
# **************************
# * Author      :  evilbear
# * Email       :  evilbear@live.cn
# * Description :  Mongolian pre-processing entry file, support for processing of sentence level and file level.
#                  > python processing.py --function="pretreatmentSentence" --line="ᠦᠪᠦᠷ ᠮᠣᠩᠭᠤᠯ ‍ᠤᠨ ᠶᠡᠬᠡ ᠰᠤᠷᠭᠠᠭᠤᠯᠢ"
#                  > python processing.py --function="pretreatmentFile" --inFilePath="allmergetxt-org-GB.txt" --outFilePath="data.txt"
#                  inFilePath and outFilePath support folders and files.
# * create time :  22/12/2018
# * file name   :  processing.py

import os, argparse, ast
from mongolianPretreatment import pretreatmentSentence, pretreatmentFile

# hyperparameters
parser = argparse.ArgumentParser(description='Mongolian pretreatmnet')
parser.add_argument('--line', type=str, default='', help='A mongolian sentence')
parser.add_argument('--inFilePath', type=str, default='', help='Input text path')
parser.add_argument('--outFilePath', type=str, default='', help='Output text path')
parser.add_argument('--num', type=int, default=50, help='Number of sentences processed in parallel')
parser.add_argument('--deduplication', type=ast.literal_eval, default=False, help='Whether to perform deduplication')
parser.add_argument('--menk2unicode', type=ast.literal_eval, default=True, help='Whether to convert menksoft to Unicode')
parser.add_argument('--split202F', type=ast.literal_eval, default=False, help='Whether to perform the processing of the segmentation U+202F')
parser.add_argument('--function', type=str, default='pretreatmentFile', help='pretreatmentFile or pretreatmentSentence')
args = parser.parse_args()

if args.function == 'pretreatmentFile':
    if args.inFilePath and args.outFilePath:
        inFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.inFilePath)
        outFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.outFilePath)
        # By default, when '.' exists in outFilePath, outFilePath is the file.
        outIsFile = True if ('.' in args.outFilePath) else False
        # When inFilePath and outFilePath are folders.
        if os.path.isdir(inFilePath) and not outIsFile:
            if not os.path.exists(outFilePath): os.makedirs(outFilePath)
            corpus_list = os.listdir(inFilePath)
            for i_corpus in corpus_list:
                inPath = os.path.join(inFilePath, i_corpus)
                outPath = os.path.join(outFilePath, i_corpus)
                pretreatmentFile(inPath, outPath, num=args.num, deduplication=args.deduplication, menk2unicode=args.menk2unicode, split202F=args.split202F)
        # When inFilePath is a folder and outFilePath is a file.
        elif os.path.isdir(inFilePath) and outIsFile:
            corpus_list = os.listdir(inFilePath)
            for i_corpus in corpus_list:
                inPath = os.path.join(inFilePath, i_corpus)
                pretreatmentFile(inPath, outFilePath, num=args.num, deduplication=args.deduplication, menk2unicode=args.menk2unicode, split202F=args.split202F)
        # When inFilePath and outFilePath are files.
        elif os.path.isfile(inFilePath) and outIsFile:
            pretreatmentFile(inFilePath, outFilePath, num=args.num, deduplication=args.deduplication, menk2unicode=args.menk2unicode, split202F=args.split202F)
        else:
            print("inFilePath is a file, outFilePath is a folder, this case is not supported.")
    else:
        print("Please enter the path.")
elif args.function == 'pretreatmentSentence':
    if args.line:
        line = pretreatmentSentence(args.line, menk2unicode=args.menk2unicode, split202F=args.split202F)
        print(line)
    else:
        print("Please enter mongolian sentence.")
else:
    print("The function is pretreatmentFile or pretreatmentSentence.")