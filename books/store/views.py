from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import render

from store.models import Book
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer


# http://127.0.0.1:8000/book/?format=json
class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]  # IsAuthenticated IsAuthenticatedOrReadOnly
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


def auth(request):
    return render(request, 'oauth.html')
