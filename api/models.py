from django.db import models


class Book(models.Model):
    title = models.CharField(unique=True, max_length=100, blank=True)
    author = models.CharField(max_length=30, blank=True)
    content = models.TextField(blank=True)

    class Meta:
        db_table = 'book'


class EssayQnA(models.Model):
    book_id = models.PositiveIntegerField()
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        db_table = 'qna_essay'


class ChoiceQnA(models.Model):
    book_id = models.PositiveIntegerField()
    question = models.TextField()
    options = models.TextField()
    answer = models.SmallIntegerField()

    class Meta:
        db_table = 'qna_choice'


class MindMap(models.Model):
    book_id = models.PositiveIntegerField()
    nodes = models.TextField()

    class Meta:
        db_table = 'mind_map'
