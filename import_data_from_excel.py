# -*- coding: utf-8 -*-

import os, sqlite3, jieba, re
from xlrd import open_workbook


base = os.path.dirname(__file__)
excel_path = base+"/test.xls"

stop_words = []
with open(base + '/stop_words.txt', encoding='gbk') as f:
    for line in f.readlines():
        stop_words.append(line.strip('\n'))

def import_from_excel(excel_path):
    conn = sqlite3.connect(base + '/QA.db')
    cursor = conn.cursor()
    cursor.execute("drop table QA")
    cursor.execute("create table QA (ID integer primary key, Q text, A text, TAG text)")

    wb = open_workbook(excel_path, encoding_override="utf-8")
    sh = None
    try:
        sh = wb.sheet_by_index(0)
    except:
        print("no sheet")
    nrows = sh.nrows
    ncols = sh.ncols
    print(os.getcwd(), "========== nrows %d,ncols %d ==========" % (nrows, ncols))
    row_list = []
    print("开始导入------------------->>>>>>>")
    for i in range(1, nrows):
        row_data = sh.row_values(i)
        row_list.append(row_data)
        n = i - 1
        cursor.execute(
            "insert into QA(Q,A,TAG)values (?,?,?)",
            (row_list[n][0], row_list[n][1], get_tags(row_list[n][0])))
    result = cursor.execute("SELECT * FROM QA limit 100")
    for row in result:
        print(row)
    conn.commit()
    conn.close()
    print("导入完成------------------->>>>>>>")
    # print len(row_list[3])


def drop_and_create_table():
    conn = sqlite3.connect(base + '/QA.db')
    cursor = conn.cursor()
    cursor.execute("drop table QA")
    cursor.execute("create table QA (ID integer primary key, Q text, A text, TAG text)")
    result = cursor.execute("SELECT name FROM sqlite_master where type='table' order by name")
    for row in result:
        print(row)
    conn.commit()
    conn.close()

def get_tags(input_question):
    input_question.strip().replace('\n', '')
    # input_question = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", " ", input_question)
    tag = jieba.lcut(input_question, cut_all=False)
    for word in reversed(tag):  #去除停用词
        if word in stop_words:
            tag.remove(word)
    return "|".join(filter(None, tag))

if __name__ == "__main__":
    import_from_excel(excel_path)
