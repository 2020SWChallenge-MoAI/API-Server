def isValidBid(bid):
    import os
    import re
    from config import config

    if bid not in [int(x.split(".")[0]) for x in os.listdir(config.BOOK_DIR) if (re.compile("^\d+[.]txt$").match(x) != None)]:
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

    def buildKeywordExtractionDataFile(extractor):
        build_data = []
        for i, bid in enumerate(sorted([int(x.split(".")[0]) for x in os.listdir(config.BOOK_DIR) if (re.compile("^\d+[.]txt$").match(x) != None)])):
            with open(os.path.join(config.MODEL_DIR, bid + ".txt"), "r") as f:
                text = f.read()
            
            build_data.append([bid, preprocess(text)])
        
        extractor.build(build_data)
        extractor.save(os.path.join(config.MODEL_DIR, config.KEYWORD_DATA_FILE_NAME))

    keyword_extractor = KeywordExtractor()

    if config.KEYWORD_DATA_FILE_NAME not in os.listdir(config.MODEL_DIR):
        buildKeywordExtractionDataFile(keyword_extractor)
    
    keyword_extractor.load(os.path.join(config.MODEL_DIR, config.KEYWORD_DATA_FILE_NAME))

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

def append_prev_next_sent(full_sent_texts, sent_idx):
    result = ""
    
    if sent_idx > 0:
        result += full_sent_texts[sent_idx - 1] + "\n"
        
    result += full_sent_texts[sent_idx]

    if sent_idx < len(full_sent_texts) - 1:
        result += "\n" + full_sent_texts[sent_idx + 1]
    
    return result