from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase
# from unittest import TestCase # don't clean TestDataBase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksSerializerTestCase(TestCase):
    def test_serializer(self):
        user1 = User.objects.create(username='test_user1')
        user2 = User.objects.create(username='test_user2')
        user3 = User.objects.create(username='test_user3')
        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1')
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True , rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True , rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        # data = BookSerializer([book_1, book_2], many=True).data # only a likes_count

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
        ).order_by('id')
        data = BookSerializer(books, many=True).data

        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'annotated_likes': 3,
                'rating': '4.67',
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                'annotated_likes': 2,
                'rating': '3.50',
            },
        ]
        #print('rating:', data)
        self.assertEqual(expected_data, data)
