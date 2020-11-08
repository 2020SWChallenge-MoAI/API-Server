import os
import json

from flask import Blueprint, request, abort, g
from flask.helpers import send_from_directory

from .decorators import bid_validity_chk_required, signin_required

from database import db
from database.book import Book
from database.user_book import User_Book
from database.book_sentence import BookSentence
from database.book_image import BookImage
from database.qna import QnA
from sqlalchemy import desc, func

from config import config
from functions import *
from init_once import keyword_extractor, mainsentence_komoran_tokenizer_summarizer, mainsentence_subword_tokenizer_summarizer

book = Blueprint(name="book", import_name=__name__)

@book.route("", methods=["GET"])
@signin_required
def getAllBookMetaData():
    qresult = Book.query.all()

    result = []
    for row in qresult:
        result.append({
            "bid": row.bid,
            "title": row.title,
            "author": row.author,
            "publisher": row.publisher,
            "category": row.category,
            "page_num": row.page_num,
            "image_num": row.image_num
        })

    return {
        "books": result
    }, 200


@book.route("/<int:bid>", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookMetaData(bid):
    qresult = Book.query.filter_by(bid=bid).all()
    
    row = qresult[0]

    return {
        "bid": row.bid,
        "title": row.title,
        "author": row.author,
        "publisher": row.publisher,
        "category": row.category,
        "page_num": row.page_num,
        "image_num": row.image_num
    }, 200


@book.route("/<int:bid>/cover", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookCover(bid):
    path = os.path.join(config.BOOK_DIR, str(bid), "cover.png")
    try:
        return send_from_directory(directory=os.path.dirname(path), filename=os.path.basename(path))
    except:
        abort(404)


@book.route("/<int:bid>/read", methods=["POST"])
@signin_required
@bid_validity_chk_required
def registerBookRead(bid):
    uid = g.uid

    try:
        db.session.add(User_Book(uid, bid))
        db.session.commit()
        return {}, 200
    except:
        abort(500)


@book.route("/<int:bid>/<int:page>", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookPage(bid, page):
    uid = g.uid
    
    path = os.path.join(config.BOOK_DIR, str(bid), f"{bid}-{page}.png")
    if os.path.exists(path):
        return send_from_directory(directory=os.path.dirname(path), filename=os.path.basename(path))
    else:
        abort(404)


@book.route("/<int:bid>/text", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookText(bid):
    path = os.path.join(config.BOOK_DIR, str(bid), "text.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            text_by_lines = f.readlines()
        
        text = "".join(text_by_lines[1:]) # 제목 줄 제거

        return {"text": text}, 200
    else:
        abort(404)


@book.route("/<int:bid>/keyword", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookKeyword(bid):
    params = request.args.to_dict()
    
    if "num" not in params.keys():
        keyword_num = config.DEFAULT_KEYWORD_NUM
    else:
        try:
            keyword_num = int(params["num"])
        except:
            keyword_num = config.DEFAULT_KEYWORD_NUM

    if "anc" not in params.keys():
        ancestors = []
    else:
        try:
            ancestors = json.loads(params["anc"])
        except:
            ancestors = []
    
    keywords = keyword_extractor.recommend(document_id=bid, queries=ancestors, num=keyword_num, use_ner=False)

    return {
        "keywords": keywords
    }, 200


@book.route("/<int:bid>/main-sentence", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookMainSentence(bid):
    params = request.args.to_dict()
    
    if "num" not in params.keys():
        main_sentence_num = config.DEFAULT_MAIN_SENTENCE_NUM
    else:
        try:
            main_sentence_num = int(params["num"])
        except:
            main_sentence_num = config.DEFAULT_MAIN_SENTENCE_NUM

    main_sentences = []
    if bid in config.SELECTED_BOOK_BIDS:
        qresult = BookSentence.query.filter_by(bid=bid).order_by(BookSentence.sid).all()
        sentences = {x.__dict__["sid"]:{"sentence": x.__dict__["sentence"], "rank": x.__dict__["rank"]} for x in qresult}
        sids_sortby_rank = [x[0] for x in sorted([[x.__dict__["sid"], x.__dict__["rank"]] for x in qresult], key=lambda x:x[1])]
        
        appeared_sids = []
        for sid in sids_sortby_rank:
            if len(main_sentences) == main_sentence_num:  # 필요한 개수 다 채우면 종료
                break
            
            if sid in appeared_sids:  # 이미 등장한 sid는 skip
                continue

            main_sentence = ""
            
            if (sid - 1) in sentences.keys():
                if sentences[sid]["sentence"] != sentences[sid - 1]["sentence"]:
                    main_sentence += sentences[sid - 1]["sentence"] + "\n"
                else:
                    if (sid - 2) in sentences.keys():
                        main_sentence += sentences[sid - 2]["sentence"] + "\n"
            
            main_sentence += sentences[sid]["sentence"]

            if (sid + 1) in sentences.keys():
                if sentences[sid]["sentence"] != sentences[sid + 1]["sentence"]:
                    main_sentence += "\n" + sentences[sid + 1]["sentence"]
                else:
                    if (sid + 2) in sentences.keys():
                        main_sentence += sentences[sid - 2]["sentence"] + "\n"

            main_sentences.append(main_sentence)

            appeared_sids.append(sid - 1)
            appeared_sids.append(sid)
            appeared_sids.append(sid + 1)
    else:
        with open(os.path.join(config.BOOK_TEXT_DIR, f"{bid}.txt"), "r", encoding="utf-8") as f:
            full_sent_texts = f.readlines()
        
        full_sent_texts = [x.strip() for x in full_sent_texts if x]
        del full_sent_texts[0]  # 첫 문장(제목) 제거

        komoran_summarize_result = mainsentence_komoran_tokenizer_summarizer.summarize(full_sent_texts, topk=main_sentence_num + 3)
        subword_summarize_result = mainsentence_subword_tokenizer_summarizer.summarize(full_sent_texts, topk=main_sentence_num + 3)

        # komoran + subword, remove duplicates
        summarize_result = sorted(komoran_summarize_result + subword_summarize_result, key=lambda x:x[1])  # sort by rank
        
        appeared_sids = []
        for sid, _, _  in summarize_result:
            if len(main_sentences) == main_sentence_num:  # 필요한 개수 다 채우면 종료
                break
            
            if sid in appeared_sids:  # 이미 등장한 sid는 skip
                continue
            
            sentence = ""
            if sid > 0:
                sentence += full_sent_texts[sid - 1] + "\n"
                    
            sentence += full_sent_texts[sid]

            if sid < len(full_sent_texts) - 1:
                sentence += "\n" + full_sent_texts[sid + 1]

            main_sentences.append(sentence)

            appeared_sids.append(sid - 1)
            appeared_sids.append(sid)
            appeared_sids.append(sid + 1)
        
    return {"main_sentences": main_sentences}, 200


@book.route("/<int:bid>/main-image", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookMainImage(bid):
    params = request.args.to_dict()

    if "rank" in params.keys():
        try:
            rank = int(params["rank"])
        except:
            abort(404)
    else:
        abort(404)
    
    if "thumbnail" in params.keys():
        try:
            thumbnail = bool(params["thumbnail"])
        except:
            thumbnail = False
    else:
        thumbnail = False

    if bid not in config.SELECTED_BOOK_BIDS:
        abort(404)

    qresult = BookImage.query.filter_by(bid=bid, rank=rank).all()
    
    if len(qresult) == 0:
        abort(404)
    
    try:
        if thumbnail:
            path = os.path.join(config.BOOK_DIR, str(bid), "imgs", f"thumb.{qresult[0].uri}")
            return send_from_directory(directory=os.path.dirname(path), filename=os.path.basename(path))
        else:
            path = os.path.join(config.BOOK_DIR, str(bid), "imgs", f"{qresult[0].uri}")
            return send_from_directory(directory=os.path.dirname(path), filename=os.path.basename(path))
    except:
        abort(404)


@book.route("/<int:bid>/qna/verify/question", methods=["POST"])
@signin_required
@bid_validity_chk_required
def verifyQnAQuestion(bid):
    params = request.get_json()
    
    if bid not in config.SELECTED_BOOK_BIDS:
        abort(404)

    if "question" in params.keys():
        question = params["question"]
    else:
        abort(404)
    
    if isValidQuestion(bid, question):
        return {}, 200
    else:
        abort(400)


@book.route("/<int:bid>/qna/verify/answer", methods=["POST"])
@signin_required
@bid_validity_chk_required
def verifyQnAAnswer(bid):
    params = request.get_json()
    
    if bid not in config.SELECTED_BOOK_BIDS:
        abort(404)

    if "question" in params.keys():
        question = params["question"]
    else:
        abort(404)
    
    if "answer" in params.keys():
        answer = params["answer"]
    else:
        abort(404)

    if "type" in params.keys():
        try:
            type = int(params["type"])
        except:
            abort(404)

        if type not in [0, 1]:
            abort(404)

        if type == 0:
            choices = answer.split("#@@#")

            if len(choices) <= 1:  # choice가 없다면 error
                abort(404)

            try:
                answer = int(choices[0])  # answer가 숫자가 아니면 error
            except:
                abort(404)
            
            choices = choices[1:]

            if answer not in range(1, len(choices) + 1):  # answer가 choice 중 하나가 아니면 error
                abort(404)
    else:
        abort(404)

    if isValidAnswer(bid, question, type, answer):
        return {}, 200
    else:
        abort(400)


@book.route("/<int:bid>/qna/submit", methods=["POST"])
@signin_required
@bid_validity_chk_required
def submitQuestion(bid):
    uid = g.uid
    params = request.get_json()
    
    if bid not in config.SELECTED_BOOK_BIDS:
        abort(404)

    if "question" in params.keys():
        question = params["question"]
    else:
        abort(404)
    
    if "answer" in params.keys():
        answer = params["answer"]
    else:
        abort(404)

    if "type" in params.keys():
        try:
            type = int(params["type"])
        except:
            abort(404)

        if type not in [0, 1]:
            abort(404)

        if type == 0:
            choices = answer.split("#@@#")

            if len(choices) <= 1:  # choice가 없다면 error
                abort(404)

            try:
                answer = int(choices[0])  # answer가 숫자가 아니면 error
            except:
                abort(404)
            
            choices = choices[1:]

            if answer not in range(1, len(choices) + 1):  # answer가 choice 중 하나가 아니면 error
                abort(404)
    else:
        abort(404)
    
    if isValidQuestion(bid, question) and isValidAnswer(bid, question, type, answer):
        try:
            db.session.add(QnA(uid, bid, question, type, answer))
            db.session.commit()
            return {}, 200
        except:
            abort(400)
    else:
        abort(400)


@book.route("/<int:bid>/qna/rand", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getRandomQuestionAnswer(bid):    
    if bid not in config.SELECTED_BOOK_BIDS:
        abort(404)

    row = QnA.query.filter_by(bid=bid).order_by(func.rand()).first()

    if row is None:
        abort(400)
    
    return {
        "qid": row.qid,
        "uid": row.uid,
        "bid": row.bid,
        "question": row.question,
        "type": row.type,
        "answer": row.answer,
        "created_at": row.created_at.isoformat()
    }, 200
    
    
