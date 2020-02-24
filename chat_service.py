# -*- coding: utf-8 -*-
import os
import sqlite3
import jieba
import logging
import train_eval
from config import Config
jieba.setLogLevel(logging.INFO) #设置不输出信息


stop_words = []
cwd = os.path.dirname(__file__)
opt = Config()
searcher, sos, eos, unknown, word2ix, ix2word = train_eval.test(opt)


with open(cwd+'/stop_words.txt', encoding='gbk') as f:
    for line in f.readlines():
        stop_words.append(line.strip('\n'))

def match(input_question):
    conn = sqlite3.connect(cwd + '/QA.db')
    cursor = conn.cursor()
    res = []
    cnt = {}
    question = list(jieba.cut(input_question, cut_all=False)) #对查询字符串进行分词
    for word in reversed(question):  #去除停用词
        if word in stop_words:
            question.remove(word)
    for tag in question: #按照每个tag，循环构造查询语句
        keyword = "'%" + tag + "%'"
        result = cursor.execute("select * from QA where tag like " + keyword)
        for row in result:
            if row[0] not in cnt.keys():
                cnt[row[0]]  = 0
            cnt[row[0]] += 1 #统计记录出现的次数
    try:
        res_id = sorted(cnt.items(), key=lambda d:d[1],reverse=True)[0][0] #返回出现次数最高的记录的id
    except:
        return tuple() #若查询不出则返回空
    cursor.execute("select * from QA where id= " + str(res_id))
    res = cursor.fetchone()
    conn.close()
    if type(res) == type(tuple()):
        return res[2] #返回元组类型(id, question, answer, tag)
    else:
        return tuple() #若查询不出则返回空


def chat(input_sentence):
    output_words = match(input_sentence)
    if (output_words != tuple()):
        return output_words
    output_words = train_eval.output_answer(input_sentence, searcher, sos, eos, unknown, opt, word2ix, ix2word)
    if len(output_words) == 0 or '</SOS>' in output_words or '</EOS>' in output_words or '</UNK>' in output_words:
        return "不好意思，我没有明白您的问题 =。=！"
    return output_words

