from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter

from api.views.book import book_list, book_detail
from api.views import qna
from api.views import mind_map

urlpatterns = [
    path('books/', book_list),
    path('books/<int:book_id>', book_detail),
    path('qna/verify-question/', qna.verify_question),
    path('qna/verify-answer/', qna.verify_answer),
    path('qna/check-answer/', qna.check_answer),
    path('qna/random/<int:book_id>/<int:qtype>/', qna.random_qna),
    path('mind-map/suggestion/', mind_map.suggestion)
]