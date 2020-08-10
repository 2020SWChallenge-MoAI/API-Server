from rest_framework import serializers
from api.models import Book
from api.models import MindMap
from api.models import EssayQnA, ChoiceQnA


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author')


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class MindMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = MindMap
        fields = '__all__'


class EssayQnASerializer(serializers.ModelSerializer):
    class Meta:
        model = EssayQnA
        fields = '__all__'


class ChoiceQnASerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceQnA
        fields = '__all__'
