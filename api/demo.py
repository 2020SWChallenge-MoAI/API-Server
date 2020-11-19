from flask import Blueprint, request, abort, g
import itertools
import random
import os
import base64
import re

import kss
from config import config

from database.book_sentence import BookSentence

from functions import *
from init_once import mainsentence_komoran_tokenizer_summarizer, mainsentence_subword_tokenizer_summarizer, keyword_extractor, electra, komoran
from keyext import simple_preprocess
from model.qna.utils import f1_score

demo = Blueprint(name="demo", import_name=__name__)

@demo.route("/load-text", methods=["GET"])
def load_text():
    params = request.args.to_dict()

    available_bids = [int(x) for x in os.listdir(config.DEMO_DIR)]

    try:
        bid = int(params["bid"])
    except:
        abort(400)
    
    if not (bid == -1 or bid in available_bids):
        abort(400)

    if bid == -1:
        bid = random.choice(available_bids)
    
    with open(os.path.join(config.DEMO_DIR, str(bid), "meta.txt"), "r") as f:
        meta = f.readlines()
    
    title = meta[1].strip()
    author = meta[2].strip()
    publisher = meta[3].strip()

    with open(os.path.join(config.DEMO_DIR, str(bid), "text.txt"), "r") as f:
        content = f.read()

    with open(os.path.join(config.DEMO_DIR, str(bid), "cover.png"), "rb") as f:
        cover = base64.b64encode(f.read()).decode("utf-8")
    
    return {
        "bid": bid,
        "title": title,
        "author": author,
        "publisher": publisher,
        "content": content,
        "cover": cover
    }, 200

@demo.route("/keyword", methods=["POST"])
def keyword():
    params = request.get_json()

    bid = int(params["bid"])
    num = int(params["num"])
    content = params["content"]
    initKeyword = "none" if (params["initKeyword"] == "custom") else params["initKeyword"]
    initKeywordCustomInput = params["initKeywordCustomInput"] if (params["initKeyword"] == "custom") else ""

    def getKeywords():
        keyword_history = [x.strip() for x in initKeywordCustomInput.split(",")]
        keyword_ner_filtering = {
            "character": ["PS", "CV_POS"],
            "location": ["LC"],
            "event": ["EV"],
            "none": []
        }[initKeyword]

        if bid in keyword_extractor.documents:
            keywords_tfidf = keyword_extractor.recommend(bid, num=num, queries=keyword_history, use_ner=False)
            keywords_together = keyword_extractor.recommend(bid, num=num, queries=keyword_history, use_ner=True, tags=keyword_ner_filtering)
        else:
            keywords_tfidf = keyword_extractor.recommend_from_sentences([simple_preprocess(sent) for sent in content.split('\n')], num=num, queries=keyword_history, use_ner=False)
            keywords_together = keyword_extractor.recommend_from_sentences([simple_preprocess(sent) for sent in content.split('\n')], num=num, queries=keyword_history, use_ner=True, tags=keyword_ner_filtering)
        
        return keywords_tfidf, keywords_together
    
    def getNer():
        ner_model = keyword_extractor.ner_context

        if str(bid) in ner_model.contexts:
            ners = ner_model.contexts[str(bid)]["all"]
        else:
            document = re.sub('\n', '. ', content)
            document = re.sub('\s',' ', document)
            document = re.split('(?<=[\!\?\.][ ])', document)
            document = "\n".join(document)
            ners = ner_model.prediction(document)

        word_tags = {}
        for ner in ners:
            tag = ner[0]
            word = ner[1]

            if word in word_tags.keys():
                if tag in word_tags[word]:
                    word_tags[word][tag] += 1
                else:
                    word_tags[word][tag] = 1
            else:
                word_tags[word] = {}
                word_tags[word][tag] = 1

        result = []
        total_tag_count = {}
        for word in word_tags.keys():
            tags = [{"tag": tag, "count": word_tags[word][tag]} for tag in word_tags[word].keys()]
            tags = sorted(tags, key=lambda x: x["count"], reverse=True)

            result.append({
                "word": word,
                "tags": tags
            })

            total_tag_count[word] = sum([x["count"] for x in tags])
        
        result = sorted(result, key=lambda x: total_tag_count[x["word"]], reverse=True)

        return result

    try:
        tfidf, together = getKeywords()
        ner = getNer()
        return {
            "tfidf": tfidf,
            "ner": ner,
            "together": together
        }, 200
    except Exception as e:
        raise e
        abort(400)

@demo.route("/main-sentence", methods=["POST"])
def main_sentence():
    params = request.get_json()
    
    num = int(params["main_sentence_num"])
    text = params["text"]
    bid = int(params["bid"])

    main_sentences = []

    if bid != -1:
        sentence_list = [x.strip() for x in text.split("\n")]
    else:
        sentence_list = [kss.split_sentences(x.strip()) for x in text.split("\n")]
        sentence_list = list(itertools.chain(*sentence_list))

    komoran_summarize_result = mainsentence_komoran_tokenizer_summarizer.summarize(sentence_list, topk=(num + 10))
    subword_summarize_result = mainsentence_subword_tokenizer_summarizer.summarize(sentence_list, topk=(num + 10))

    # komoran + subword, remove duplicates
    summarize_result = sorted(komoran_summarize_result + subword_summarize_result, key=lambda x:x[1])  # sort by rank
    
    appeared_sids = []
    for sid, rank, _  in summarize_result:
        if len(main_sentences) == num:  # 필요한 개수 다 채우면 종료
            break
        
        if sid in appeared_sids:  # 이미 등장한 sid는 skip
            continue
        
        sent = {}

        sent["cur"] = sentence_list[sid]
        sent["rank"] = rank

        if sid > 0:
            sent["prev"] = sentence_list[sid - 1]

        if sid < len(sentence_list) - 1:
            sent["next"] = sentence_list[sid + 1]

        main_sentences.append(sent)

        appeared_sids.append(sid - 1)
        appeared_sids.append(sid)
        appeared_sids.append(sid + 1)
    
    return {
        "main-sentences": main_sentences
    }, 200

@demo.route("/verify-question", methods=["POST"])
def verify_question():
    params = request.get_json()

    text = params["content"]
    question = params["question"]

    score = electra({
        'question': question,
        'context': text})["score"]

    if score >= config.QNA_QUESTION_VALID_SCORE_THRESHOLD:
        return {
            "score": round(score, 3)
        }, 200
    else:
        return {
            "score": round(score, 3)
        }, 400

@demo.route("/verify-answer", methods=["POST"])
def verify_answer():
    params = request.get_json()

    text = params["content"]
    question = params["question"]
    type = int(params["type"])
    answer = params["answer"]

    electra_answers = electra({
        'question': question,
        'context': text},
        topk=5)
    
    electra_answers = ["".join(komoran.nouns(w['answer'])) for w in electra_answers]

    if type == 0:
        choices = answer.split("#@@#")
        answer = int(choices[0])
        choices = choices[1:]

        scores = []
        for choice in choices:
            scores.append(max([f1_score(electra, choice) for electra in electra_answers]))
        
        if answer == [(i + 1) for i, s in enumerate(scores) if s == max(scores)][0]:
            return {
                "score": (f"{round(scores[answer - 1], 3)} ([{', '.join([str(round(x, 3)) for x in scores])}])"),
                "electra_answer": ", ".join(electra_answers)
            }, 200
        else:
            return {
                "score": (f"{round(scores[answer - 1], 3)} ([{', '.join([str(round(x, 3)) for x in scores])}])"),
                "electra_answer": ", ".join(electra_answers)
            }, 400
    else:  # type == 1
        score = max([f1_score(electra, answer) for electra in electra_answers])

        if score >= config.QNA_ANSWER_VALID_SCORE_THRESHOLD:
            return {
                "score": round(score, 3),
                "electra_answer": ", ".join(electra_answers)
            }, 200
        else:
            return {
                "score": round(score, 3),
                "electra_answer": ", ".join(electra_answers)
            }, 400