import re
import os
from os.path import join

import pymysql

db = pymysql.connect(
    host='localhost',
    port=3306,
    user='moai',
    passwd='moai',
    db='ttokdok',
    charset='utf8'
)


def convert_book1():
    """
    :return: Titles, Authors, Contents
    """
    bookfiles = next(os.walk('data/book/1'))[2]

    authors = []
    titles = []
    contents = []

    for filepath in bookfiles:
        filename = re.sub(r'\([^)]*\)', '', filepath)  # remove text within parentheses
        filename = filename.split('.')[0].split('-')

        author = filename[0] if filename[0] != 'OT' else filename[2]
        title = filename[1] if filename[0] != 'OT' else filename[3]

        with open(join('data/book/1', filepath), 'r', encoding='utf8') as f:
            raw = f.readlines()[1:]
            for idx in range(len(raw)):
                if idx >= 1 and (raw[idx - 1] != '\n' and raw[idx + 1] != '\n'):
                    raw = raw[idx - 1:]
                    break

        content = ''.join(raw)

        authors.append(author)
        titles.append(title)
        contents.append(content)

    return titles, authors, contents


def convert_book2():
    """
    :return: Titles, Authors(None), Contents
    """
    bookfiles = next(os.walk('data/book/2'))[2]

    titles = []
    contents = []

    for filepath in bookfiles:
        with open(join('data/book/2', filepath), 'r', encoding='utf8') as f:
            raw = f.readlines()

            title = raw[0].strip()
            content = ''.join(raw[1:]).strip()
            titles.append(title)
            contents.append(content)

    return titles, [''] * len(titles), contents


def insert_to_Book(titles, authors, contents):
    #try:
    with db.cursor() as cursor:
        for title, author, content in zip(titles, authors, contents):
            sql = '''
                INSERT INTO book(title, author, content) \
                VALUES ( %s, %s, %s); \
            '''
            cursor.execute(sql, (title, author, content))

        db.commit()
    #finally:
        #db.close()


if __name__ == '__main__':
    titles1, authors1, contents1 = convert_book1()
    titles2, authors2, contents2 = convert_book2()

    insert_to_Book(titles1, authors1, contents1)
    insert_to_Book(titles2, authors2, contents2)
