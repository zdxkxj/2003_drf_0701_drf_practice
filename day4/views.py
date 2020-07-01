from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework import generics
from rest_framework import viewsets

from api.models import Book
from utils.response import APIResponse
from .serializers import BookModelSerializer


class BookAPIView(APIView):

    def get(self, request, *args, **kwargs):
        book_list = Book.objects.filter(is_delete=False)
        data_ser = BookModelSerializer(book_list, many=True).data

        return APIResponse(results=data_ser)



class BookGenericAPIView(ListModelMixin,
                         RetrieveModelMixin,
                         CreateModelMixin,
                         UpdateModelMixin,
                         DestroyModelMixin,
                         GenericAPIView):

    queryset = Book.objects.filter(is_delete=False)
    serializer_class = BookModelSerializer

    lookup_field = "id"


    def get(self, request, *args, **kwargs):
        if "id" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # 获取book模型的所有的数据
        # book_list = Book.objects.filter(is_delete=False)
        book_list = self.get_queryset()
        # 获取要使用序列化器
        # data_ser = BookModelSerializer(book_obj).data
        data_ser = self.get_serializer(book_list, many=True)
        data = data_ser.data

        return APIResponse(results=data)

    def get(self, request, *args, **kwargs):
        # user_id = kwargs.get("id")
        # book_obj = Book.objects.get(pk=user_id, is_delete=False)
        book_obj = self.get_object()
        # data_ser = BookModelSerializer(book_obj).data
        data_ser = self.get_serializer(book_obj)
        data = data_ser.data

        return APIResponse(results=data)
    """

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)
        return APIResponse(results=response.data)

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        return APIResponse(results=response.data)


    def patch(self, request, *args, **kwargs):
        response = self.partial_update(request, *args, **kwargs)
        return APIResponse(results=response.data)


    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return APIResponse(http_status=status.HTTP_204_NO_CONTENT)


class BookListAPIVIew(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Book.objects.filter(is_delete=False)
    serializer_class = BookModelSerializer
    lookup_field = "id"


class BookGenericViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.filter(is_delete=False)
    serializer_class = BookModelSerializer
    lookup_field = "id"


    def user_login(self, request, *args, **kwargs):

        return self.retrieve(request, *args, **kwargs)

    def get_user_count(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)




