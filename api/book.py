import os
import re
import json
from functools import wraps

from flask import Blueprint, request, abort, g
from flask.helpers import send_from_directory
from api.auth import signin_required

from database import db
from database.user_book import User_Book
from database.book import Book
from config import config
from functions import *
from init_once import keyword_extractor, mainsentence_komoran_tokenizer_summarizer, mainsentence_subword_tokenizer_summarizer


book = Blueprint(name="book", import_name=__name__)

def bid_validity_chk_required(f):
    @wraps(f)
    def decorated_function(bid, *args, **kwargs):
        if not isValidBid(bid):
            abort(404)
        else:
            return f(bid, *args, **kwargs)
    
    return decorated_function


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
            "page_num": row.page_num
        })

    return {
        "books": result
    }, 200


@book.route("/<int:bid>/cover", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookCover(bid):
    path = os.path.join(config.ASSET_DIR, str(bid), "cover.png")
    try:
        return send_from_directory(directory=os.path.dirname(path), filename=os.path.basename(path))
    except:
        abort(404)


@book.route("/<int:bid>/<int:page>", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookPage(bid, page):
    uid = g.uid
    
    path = os.path.join(config.ASSET_DIR, str(bid), f"{bid}-{page}.png")
    if os.path.exists(path):
        try:
            db.session.add(User_Book(uid, bid))
            db.session.commit()
        except:
            abort(500)
        
        return send_from_directory(directory=os.path.dirname(path), filename=os.path.basename(path))
    else:
        abort(404)


@book.route("/<int:bid>/text", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookText(bid):
    path = os.path.join(config.ASSET_DIR, str(bid), "text.txt")
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
    
    keywords = keyword_extractor.recommend(document_id=bid, keyword_history=ancestors, num=keyword_num)

    return {
        "bid": bid,
        "keyword_num": keyword_num,
        "keyword_ancestors": ancestors,
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

    # TODO : main sentence 추출기 DB 버전으로 업데이트
    with open(os.path.join(config.BOOK_DIR, str(bid) + ".txt"), "r", encoding="utf-8") as f:
        full_sent_texts = f.readlines()
    
    full_sent_texts = [x.strip() for x in full_sent_texts if x]
    del full_sent_texts[0]  # 첫 문장(제목) 제거

    komoran_summarize_result = mainsentence_komoran_tokenizer_summarizer.summarize(full_sent_texts, topk=main_sentence_num + 3)
    subword_summarize_result = mainsentence_subword_tokenizer_summarizer.summarize(full_sent_texts, topk=main_sentence_num + 3)

    # komoran + subword, remove duplicates
    summarize_result = sorted(komoran_summarize_result + subword_summarize_result, key=lambda x:x[1])  # sort by rank
    
    appeared_sent_idx = []
    main_sentences = []
    for sent_idx, sent_rank, _  in summarize_result:
        if len(appeared_sent_idx) == main_sentence_num:  # 필요한 개수 다 채우면 종료
            break
        
        if sent_idx in appeared_sent_idx:  # 이미 등장한 idx는 skip
            continue

        main_sentences.append({
            "idx": int(sent_idx),
            "rank": sent_rank,
            "sentence": append_prev_next_sent(full_sent_texts, sent_idx)
        })

        appeared_sent_idx.append(sent_idx - 1)
        appeared_sent_idx.append(sent_idx)
        appeared_sent_idx.append(sent_idx + 1)

    return {
        "bid": bid,
        "main_sentence_num": main_sentence_num,
        "main_sentences": main_sentences
    }, 200


@book.route("/<int:bid>/main-image", methods=["GET"])
@signin_required
@bid_validity_chk_required
def getBookMainImage(bid):
    params = request.args.to_dict()
    
    if "num" not in params.keys():
        main_image_num = config.DEFAULT_MAIN_IMAGE_NUM
    else:
        try:
            main_image_num = int(params["num"])
        except:
            main_image_num = config.DEFAULT_MAIN_IMAGE_NUM

    # TODO : main image 추출기 완성하기
    main_images = None

    return {
        "bid": bid,
        "main_image_num": main_image_num,
        "main_images": main_images
    }, 200