#!/usr/bin/python3
# -*- coding: utf-8 -*-
# **************************
# * Author      :  evilbear
# * Email       :  evilbear@live.cn
# * Dependency  :  word2vec
# * Description :  Corresponding preprocessing operations, prepare the documents required for the experiment.
#                  such as: 5 cross-validation dataset, vocabulary, word vectors table...
# * create time :  23/12/2018
# * file name   :  corpusPreprocessingFunctions.py

import os, random, math, shutil, word2vec
import numpy as np
from itertools import islice

# Convert corpus into BIOES label.
def corpus2BIO(inFilePath, outFilePath):
    data_file = open(inFilePath, "r")
    save_file = open(outFilePath, "w")
    tag_dict = {'GPE':'LOC', 'OGR':'ORG', 'PER':'PER'}
    for line in data_file:
        line = line.strip().split(' ')
        tag_list = ['O'] * len(line)
        state = False
        for idx, word in enumerate(line):
            if word in tag_dict and line[idx-1] == '[':
                tag_list[idx-1], tag_list[idx] = '', ''
                state = True
                entity_structure = [tag_dict[word]]
                continue
            if state == True:
                if word != ']':
                    entity_structure.append(idx)
                else:
                    tag_list[idx] = ''
                    state = False
                    entity = entity_structure[0]
                    entity_left = entity_structure[1]
                    entity_right = entity_structure[-1]
                    entity_len = len(entity_structure[1:])
                    if entity_len == 1:
                        tag_list[entity_left] = 'S-' + entity
                    else:
                        tag_list[entity_left : entity_right+1] = ['I-' + entity] * entity_len 
                        tag_list[entity_left] = 'B-' + entity
                        tag_list[entity_right] = 'E-' + entity
        for word, tag in zip(line, tag_list):
            if tag:
                save_file.write(word + " " + tag + '\n')
        save_file.write('\n')
    data_file.close()
    save_file.close()

# Convert label corpus into unlabel corpus.
def label2unlabel(inFilePath, outFilePath):
    data_file = open(inFilePath, "r")
    save_file = open(outFilePath, "w")
    for line in data_file:
        line = line.strip('\n')
        if (len(line) != 0):
            word = line.split(' ')[0]
            save_file.write(word + ' ')
        else:
            save_file.write('\n')
    data_file.close()
    save_file.close()

# Statistical word frequency.
def statisticsWord(inFilePath, outFilePath):
    data_file = open(inFilePath, "r")
    save_file = open(outFilePath, "w")
    words_dict = dict()
    for line in data_file:
        line = line.strip().split(' ')
        for word in line:
            if word.isdigit():
                continue
            if word in words_dict:
                words_dict[word] += 1
            else:
                words_dict[word] = 1
    data = sorted(words_dict.items(), key=lambda x:x[1], reverse=True)
    for i in range(len(data)):
       save_file.write(data[i][0]+' '+str(data[i][1])+'\n')
    data_file.close()
    save_file.close()

# Combine label and unlabel, deduplication and randomly
def mergingUnlabel(FilePath1, FilePath2, outFilePath):
    sentence_set = set()
    with open(FilePath1, 'r') as fr:
        for line in fr:
            sentence_set.add(line.strip())
    with open(FilePath2, 'r') as fr:
        for line in fr:
            sentence_set.add(line.strip())
    sentence_list = list(sentence_set)
    random.shuffle(sentence_list)
    with open(outFilePath, 'w') as fw:
        for line in sentence_list:
            fw.write(line + '\n')

# Statistics vocabulary contains information
def statisticsWordState(FilePath1, FilePath2, frequency1, frequency2):
    words1, words2 = set(), set()
    with open(FilePath1, "r") as fr:
        for line in fr:
            line = line.strip('\n').split(' ')
            if int(line[1]) >= frequency1:
                words1.add(line[0])
    with open(FilePath2, "r") as fr:
        for line in fr:
            line = line.strip('\n').split(' ')
            try:
                if int(line[1]) >= frequency2:
                    words2.add(line[0])
            except:
                pass
    print("Words in former, not in latter. The number is {}".format(len(words1-words2)))
    print("Words in latter, not in former. The number is {}".format(len(words2-words1)))
    words1.update(words2)
    print("Words in former and latter. The number is {}".format(len(words1)))

# Preparation vocabulary
def preparationVocabulary(inFilePath, outFilePath, frequency):
    with open(outFilePath, "w") as fw:
        with open(inFilePath, "r") as fr:
            for line in fr:
                line = line.strip('\n').split(' ')
                if int(line[1]) >= frequency:
                    fw.write(line[0] + '\n')
                else:
                    break

# Extend words to vocabulary
def extendVocab(inFilePath, words_list):
    with open(inFilePath, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        add_content = ''
        for words in words_list:
            add_content += words + '\n'
        f.write(add_content + content)

# Divide corpus into cross validation datasets
def preCrossValidation(inFilePath, outFilePath, batch):
    corpus_list = list()
    with open(inFilePath, "r") as fr:
        sentence = ''
        for line in fr:
            line = line.strip('\n')
            if (len(line) != 0):
                sentence += line + '\n'
            else:
                if len(sentence.split('\n')) < 300:
                    corpus_list.append(sentence + '\n')
                sentence = ''
    random.shuffle(corpus_list)
    batch_size = math.ceil(len(corpus_list) / batch)
    for idx in range(batch):
        file_name = 'part' + str(idx) + '.txt'
        save_path = os.path.join(outFilePath, file_name)
        pointer = idx * batch_size
        with open(save_path, 'w') as fw:
            for line in corpus_list[pointer: pointer+batch_size]:
                fw.write(line)

# Delete the last line of extra '\n'
def delLastLine(inFilePath):
    if os.path.isfile(inFilePath):
        with open(inFilePath, 'rb+') as f:
            f.seek(-1, os.SEEK_END)
            f.truncate()
    elif os.path.isdir(inFilePath):
        file_list = os.listdir(inFilePath)
        for file_name in file_list:
            path = os.path.join(inFilePath, file_name)
            with open(path, 'rb+') as f:
                f.seek(-1, os.SEEK_END)
                f.truncate()
    else:
        pass

# Train vectors through Glove and Word2vec
def trainVectors(inFilePath, data_path, glove_vectors_path, word2vec_vectors_path, dimension=300, min_count=3):
    # Glove, parameters need to be modified in demo.sh
    command = "cd {0}; sh demo.sh".format(inFilePath)
    os.system(command)
    os.remove(os.path.join(inFilePath, 'cooccurrence.bin'))
    os.remove(os.path.join(inFilePath, 'cooccurrence.shuf.bin'))
    os.remove(os.path.join(inFilePath, 'vectors.bin'))
    os.remove(os.path.join(inFilePath, 'vocab.txt'))
    shutil.move(os.path.join(inFilePath, 'vectors.txt'), glove_vectors_path)
    # Word2vec
    word2vec.word2vec(data_path, word2vec_vectors_path, size=dimension, verbose=True, binary=0, min_count=min_count)

# Prepare vectors table corresponding to the vocabulary
def prepareNPZ(FilePathVocab, FilePathVectors, outFilePath, dimension, skipLine=None):
    vocab_dict = dict()
    with open(FilePathVocab, 'r') as fr:
        for idx, word in enumerate(fr):
            word = word.strip('\n')
            vocab_dict[word] = idx
    embeddings = np.random.randn(len(vocab_dict), dimension)
    with open(FilePathVectors, 'r') as fr:
        for line in islice(fr, skipLine, None):
            line = line.strip('\n').split(' ')
            word = line[0]
            embedding = [float(x) for x in line[1 : dimension+1]]
            if word in vocab_dict:
                word_idx = vocab_dict[word]
                embeddings[word_idx] = np.asarray(embedding)
    np.savez_compressed(outFilePath, embeddings=embeddings)

def main():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.txt')
    corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus.txt')
    corpus2BIO(data_path, corpus_path)

    # Get the original corpus when not marked
    label_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'label.txt')
    label2unlabel(corpus_path, label_path)
    
    words_label_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words_label.txt')
    statisticsWord(label_path, words_label_path)

    unlabel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unlabel.txt')
    words_unlabel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words_unlabel.txt')
    statisticsWord(unlabel_path, words_unlabel_path)

    # Combine label and unlabel, deduplication and randomly into new unlabel dataset
    none_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'none.txt')
    mergingUnlabel(label_path, unlabel_path, none_path)

    words_none_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words_none.txt')
    statisticsWord(none_path, words_none_path)
    
    # Prepare vocabulary
    words_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'words.txt')
    statisticsWordState(words_label_path, words_none_path, 2, 3)
    preparationVocabulary(words_none_path, words_path, 3)
    extendVocab(words_path, ['$UNK$', '$NUM$', '$EOS$'])
    chars_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chars.txt')
    extendVocab(chars_path, ['$UNK$', '$NUM$'])

    corpus_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus')
    if not os.path.exists(corpus_dir_path): os.makedirs(corpus_dir_path)
    preCrossValidation(corpus_path, corpus_dir_path, 5)

    # Corpus ends with extra '\n', need to be deleted
    delLastLine(corpus_path)
    delLastLine(corpus_dir_path)

    # Train word vectors
    dimension, min_count = 300, 3
    glove_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GloVe-master')
    glove_none_path = os.path.join(glove_path, os.path.basename(none_path))
    shutil.copyfile(none_path, glove_none_path)
    glove_vectors_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glove_vectors.txt')
    word2vec_vectors_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'word2vec_vectors.txt')
    trainVectors(glove_path, none_path, glove_vectors_path, word2vec_vectors_path, dimension, min_count)

    # Prepare word vectors table
    glove_npz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glove.npz')
    prepareNPZ(words_path, glove_vectors_path, glove_npz_path, dimension)
    word2vec_npz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'word2vec.npz')
    prepareNPZ(words_path, word2vec_vectors_path, word2vec_npz_path, dimension, 1)

    # Delete temporary files
    os.remove(glove_none_path)
    os.remove(words_label_path)
    os.remove(words_unlabel_path)

if __name__ == '__main__':
    main()