def isValidBid(bid):
    import os
    import re
    from config import config
    from database.book import Book

    qresult = Book.query.filter_by(bid=bid).all()

    if len(qresult) == 0:
        return False
    else:
        return True


def getDBURI():
    from config import config, secret

    return f"{config.DB_TYPE}+{config.DB_DRIVER}://{config.DB_USER}:{secret.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"


def getKeywordExtractor():
    from keyext import preprocess, KeywordExtractor
    from config import config
    import os
    import re

    # TODO : pkl 파일은 외부에서 만들어 넣어주는 형식이라 생각하자. => build 함수 지워도 됨 (config.BOOK_TEXT_DIR을 사용함)
    def buildKeywordExtractionDataFile(extractor):
        build_data = []
        for i, bid in enumerate(sorted([int(x.split(".")[0]) for x in os.listdir(config.BOOK_TEXT_DIR) if (re.compile("^\d+[.]txt$").match(x) != None)])):
            with open(os.path.join(config.MODEL_DIR, str(bid) + ".txt"), "r") as f:
                text = f.read()
            
            build_data.append([bid, preprocess(text)])
        
        extractor.build(build_data)
        extractor.save(os.path.join(config.MODEL_DIR, "keyext", config.KEYWORD_DATA_FILE_NAME))

    keyword_extractor = KeywordExtractor()

    if config.KEYWORD_DATA_FILE_NAME not in os.listdir(os.path.join(config.MODEL_DIR, "keyext")):
        buildKeywordExtractionDataFile(keyword_extractor)
    
    keyword_extractor.load(os.path.join(config.MODEL_DIR, "keyext", config.KEYWORD_DATA_FILE_NAME))

    return keyword_extractor


def subword_tokenizer(sent, n=3):
    def subword(token, n):
        if len(token) <= n:
            return [token]

        return [token[i:i+n] for i in range(len(token) - n + 1)]

    return [sub for token in sent.split() for sub in subword(token, n)]

def komoran_tokenizer(sent):
    from init_once import komoran

    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
    return words

def convertFileToBase64(path):
    import base64

    with open(path, "rb") as f:
        result = base64.b64encode(f.read()).decode("utf-8")
    
    return result

def convertBase64ToFile(base64_str, path):
    import base64

    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_str))


def saveWorkThumbnail(uid, bid, type, updated_at, thumbnail):
    import os
    from config import config

    path = os.path.join(config.WORK_DIR, str(uid), getWorkName(bid, updated_at, type))

    if not os.path.exists(os.path.dirname(path)):
        os.mkdir(os.path.dirname(path))
    
    convertBase64ToFile(thumbnail, path)
    
def deleteWorkThumbnail(uid, bid, type, updated_at):
    import os
    from config import config
    
    path = os.path.join(config.WORK_DIR, str(uid), getWorkName(bid, updated_at, type))

    if os.path.exists(path):
        os.remove(path)
    
def getWorkName(bid, updated_at, type):
    return f"{bid}.{updated_at.strftime('%Y-%m-%d-%H-%M-%S')}.{type}.png"


def isValidQuestion(bid, question):
    import os
    from config import config
    from init_once import electra

    path = os.path.join(config.BOOK_DIR, str(bid), "text.txt")
    with open(path, "r", encoding="utf-8") as f:
        text_by_lines = f.readlines()
    
    text = "".join(text_by_lines[1:])

    score = electra.get_answer(question=question, context=text)[0]["score"]

    # DEBUG CODE
    print(f"{score} - {question}")

    if score >= config.QNA_QUESTION_VALID_SCORE_THRESHOLD:
        return True
    else:
        return False

def isValidAnswer(bid, question, type, answer):
    import os
    from config import config
    from init_once import electra
    from model.qna.utils import f1_score

    path = os.path.join(config.BOOK_DIR, str(bid), "text.txt")
    with open(path, "r", encoding="utf-8") as f:
        text_by_lines = f.readlines()
    
    text = "".join(text_by_lines[1:])

    electra_answer = electra.get_answer(question=question, context=text, topk=1)[0]["answer"]

    if type == 0:
        choices = answer.split("#@@#")
        answer = int(choices[0])
        choices = choices[1:]

        scores = []
        for choice in choices:
            scores.append(f1_score(electra_answer, choice))
        
        if answer == [(i + 1) for i, s in enumerate(scores) if s == max(scores)][0]:
            return True
        else:
            return False
    else:  # type == 1
        score = f1_score(electra_answer, answer)

        if score >= config.QNA_ANSWER_VALID_SCORE_THRESHOLD:
            return True
        else:
            return False