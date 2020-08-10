import json

import pymysql

db = pymysql.connect(
    host='localhost',
    port=3306,
    user='moai',
    passwd='moai',
    db='ttokdok',
    charset='utf8'
)

with open('data/qna_samples.txt', 'r') as f:
    samples = json.load(f)['data']

try:
    with db.cursor() as cursor:
        for sample in samples:
            for qna in sample['qna']:
                if qna['qtype'] == 0:  # choice
                    sql = '''
                        INSERT INTO qna_choice(book_id, question, options, answer) \
                        VALUES ( %s, %s, %s, %s); \
                    '''
                    options = '|^|'.join([option for option in qna['options']])
                    cursor.execute(sql, (sample['book_id'], qna['question'], options, int(qna['answer'])))
                else:  # essay
                    sql = '''
                        INSERT INTO qna_essay(book_id, question, answer) \
                        VALUES ( %s, %s, %s); \
                    '''
                    cursor.execute(sql, (sample['book_id'], qna['question'], qna['answer']))

        db.commit()
finally:
    db.close()
