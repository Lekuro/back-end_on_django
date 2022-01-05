import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 5')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=55, author_name='Author 2')
        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)

    def test_get_list(self):
        url = reverse('book-list')
        # print('url', url)
        responce = self.client.get(url)
        # print('responce', responce)
        # print('responce.data', responce.data)
        # when added annotated_likes must change:
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
        ).order_by('id')
        #serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        serializer_data = BookSerializer(books, many=True).data
        print('serializer_data', serializer_data)
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.assertEqual(serializer_data, responce.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_filter(self):
        url = reverse('book-list')
        # print('url', url)
        responce = self.client.get(url, data={'price': 55})
        # print('responce', responce)
        # print('responce.data', responce.data)
        # when added annotated_likes must change:
        books = Book.objects.filter(id__in=(self.book_2.id, self.book_3.id)).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
        ).order_by('id')
        #serializer_data = BookSerializer([self.book_2, self.book_3], many=True).data
        serializer_data = BookSerializer(books, many=True).data
        print('serializer_data', serializer_data)
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.assertEqual(serializer_data, responce.data)

    def test_get_search(self):
        url = reverse('book-list')
        print('url', url)
        responce = self.client.get(url, data={'search': 'Author 1'})
        print('responce', responce)
        print('responce.data', responce.data)
        # when added annotated_likes must change:
        books = Book.objects.filter(id__in=(self.book_1.id, self.book_3.id)).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate'),
        ).order_by('id')
        #serializer_data = BookSerializer([self.book_1, self.book_3], many=True).data
        serializer_data = BookSerializer(books, many=True).data
        print('serializer_data', serializer_data)
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.assertEqual(serializer_data, responce.data)

    # video 05 CRUD
    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Programming in Python 3",
            "price": 150,
            "author_name": "Mark Summerfield"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        responce = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, responce.status_code)
        self.assertEqual(4, Book.objects.all().count())
        # video_06
        print(Book.objects.last().owner)
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        responce = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        # self.book_1 = Book.objects.get(id=self.book_1.id)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        responce = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, responce.status_code)
        print(responce.data)
        error_msg = {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                           code='permission_denied')}
        self.assertEqual(error_msg, responce.data)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        responce = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 5')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        responce = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)
        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        responce = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        responce = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.book_1.refresh_from_db()
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            "rate": 6,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        responce = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, responce.status_code, responce.data)  # print>responce.data
        error_msg = {'rate': [ErrorDetail(string='"6" is not a valid choice.', code='invalid_choice')]}
        self.assertEqual(error_msg, responce.data)

