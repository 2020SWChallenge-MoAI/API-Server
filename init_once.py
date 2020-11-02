from functions import *

# Keyword
keyword_extractor = getKeywordExtractor()

# Main Sentence
from konlpy.tag import Komoran
from textrank import KeysentenceSummarizer
komoran = Komoran()
mainsentence_komoran_tokenizer_summarizer = KeysentenceSummarizer(tokenize=komoran_tokenizer, min_sim=0.3, verbose=False)
mainsentence_subword_tokenizer_summarizer = KeysentenceSummarizer(tokenize=subword_tokenizer, min_sim=0.3)

# QnA
from model.qna import KoELECTRA
electra = KoELECTRA("monologg/koelectra-base-v2-finetuned-korquad")

# TODO : 파일 로딩 완료되었다는 log 메시지 띄우기