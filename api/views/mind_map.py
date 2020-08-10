import json
from os.path import dirname, join
from rest_framework.response import Response
from rest_framework.decorators import api_view
from keyext import KeywordExtractor, preprocess
from api.models import Book


model_path = join(dirname(dirname(dirname('__file__'))), 'data_handler/data/model.pkl')
keyword_extractor = KeywordExtractor(model_path=model_path)


@api_view(['POST'])
def suggestion(request):
    request = json.loads(request.body)
    print(request)
    try:
        suggestions = keyword_extractor.recommend(request['book_id'], request['ancestors'][:-1])
    except KeyError:
        content = Book.objects.get(pk=request['book_id']).content
        suggestions = keyword_extractor.recommend_from_sentences(preprocess(content), request['ancestors'][:-1])
    print(f'suggestion keywords: {suggestions}')
    return Response({'suggestions': suggestions})
