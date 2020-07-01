from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from api.models import Book
from utils.response import APIResponse
from .serializers import BookModelSerializer, BookDeModelSerializer, BookModelSerializerV2
from api import serializers


class BookAPIView(APIView):

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("id")
        if book_id:

            book_obj = Book.objects.get(pk=book_id)
            # book_ser = BookModelSerializer(book_obj).data
            book_ser = serializers.BookModelSerializerV2(book_obj).data
            return Response({
                "status": status.HTTP_200_OK,
                "message": "查询单个图书成功",
                "results": book_ser
            })

        else:
            book_list = Book.objects.all()
            book_list_ser = BookModelSerializer(book_list, many=True).data
            return Response({
                "status": status.HTTP_200_OK,
                "message": "查询所有图书成功",
                "results": book_list_ser
            })

    def post(self, request, *args, **kwargs):
        """
        完成增加单个对象
        """
        request_data = request.data

        # 将前端发送过来的数据交给反序列化器进行校验
        book_ser = BookDeModelSerializer(data=request_data)

        # 校验数据是否合法 raise_exception：一旦校验失败 立即抛出异常
        book_ser.is_valid(raise_exception=True)
        book_obj = book_ser.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "添加图书成功",
            "result": BookModelSerializer(book_obj).data
        })


class BookAPIViewV2(APIView):

    def get(self, request, *args, **kwargs):

        book_id = kwargs.get("id")
        if book_id:
            try:
                book_obj = Book.objects.get(pk=book_id, is_delete=False)
                book_ser = BookModelSerializerV2(book_obj, many=False).data
                return APIResponse(status.HTTP_200_OK, "SUCCESS", results=book_ser)
            except:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "查询失败",
                })
        else:
            book_list = Book.objects.filter(is_delete=False)
            book_list_ser = BookModelSerializerV2(book_list, many=True).data
            return APIResponse(100, "查询成功了", results=book_list_ser)

    def post(self, request, *args, **kwargs):
        """
        完成增加单个对象
        同时完成增加多个对象
        """
        """
        增加单个：传递参数的格式 字典
        增加多个：[{},{},{}]  列表中嵌套的事一个个的图书对象
        """
        request_data = request.data
        if isinstance(request_data, dict):  # 代表增加的是单个图书
            # 将前端发送过来的数据交给反序列化器进行校验
            many = False
        elif isinstance(request_data, list):  # 代表添加多个图书
            many = True
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "请求参数格式有误",
            })

        book_ser = BookModelSerializerV2(data=request_data, many=many, context={"request": request})
        # 校验数据是否合法 raise_exception：一旦校验失败 立即抛出异常
        book_ser.is_valid(raise_exception=True)
        book_obj = book_ser.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "添加图书成功",
            # 当群增多个时，无法序列化多个对象到前台  所以报错
            "result": BookModelSerializerV2(book_obj, many=many).data
        })

    def delete(self, request, *args, **kwargs):
        """
        删除单个以及删除多个
        单个删除：通过url传递id v2/books/1/
        删除多个：有多个id {ids:[1,2,3]}
        """
        book_id = kwargs.get("id")
        if book_id:
            # 删除单个  也作为删除多个
            ids = [book_id]
        else:
            # 删除多个
            ids = request.data.get("ids")

        # 判断传递过来的图书的id是否在数据库  且还未删除
        response = Book.objects.filter(pk__in=ids, is_delete=False).update(is_delete=True)
        if response:
            return Response({
                "status": status.HTTP_200_OK,
                "message": "删除成功"
            })

        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "删除失败或图书不存在"
        })

    def put(self, request, *args, **kwargs):
        """
        整体修改单个： 修改一个对象的全部字段
        :return: 修改后的对象
        """
        # 修改的参数
        request_data = request.data
        # 要修改的图书的id
        book_id = kwargs.get("id")

        try:
            book_obj = Book.objects.get(pk=book_id)
        except:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "图书不存在"
            })

        # 前端发送了修改的参数request_data 数据更新需要校验
        # 更新 的时候将参数赋值data  方便钩子函数校验
        # TODO 如果是修改 需要指定instance参数  指定你要修改的是哪一个实例
        book_ser = BookModelSerializerV2(data=request_data, instance=book_obj, partial=False)
        book_ser.is_valid(raise_exception=True)

        # 经过序列化器规则校验 局部全局钩子校验通过后则调用 update()方法完成更新
        book_ser.save()

        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "更新成功",
            "results": BookModelSerializerV2(book_obj).data
        })

    # def patch(self, request, *args, **kwargs):
    #     """
    #     完成单个对象的局部修改
    #     修改对象的某些字段
    #     """
    #     request_data = request.data
    #     book_id = kwargs.get("id")
    #
    #     try:
    #         book_obj = Book.objects.get(pk=book_id)
    #     except:
    #         return Response({
    #             "status": status.HTTP_400_BAD_REQUEST,
    #             "message": "图书不存在"
    #         })
    #     # TODO 如果是修改 需要指定instance参数
    #     # TODO 如果是修改局部需要指定 partial=True  代表可以修改局部字段
    #     book_ser = BookModelSerializerV2(data=request_data, instance=book_obj, partial=True)
    #     book_ser.is_valid(raise_exception=True)
    #
    #     book_ser.save()
    #
    #     return Response({
    #         "status": status.HTTP_400_BAD_REQUEST,
    #         "message": "更新成功",
    #         "results": BookModelSerializerV2(book_obj).data
    #     })

    def patch(self, request, *args, **kwargs):
        """
        单个修改： pk  传递要修改的内容    1  {book_name: php}
        局部修改多个与整体修改多个: 多个id   多个  request.data
        id:[1,2,3]  request.data:[{},{},{}]   如何确定要修改的id与值的对应关系
        要求前端发送过来的数据按照一定的格式
        [{pk:1,book_name: python},{pk:2,publish:2},{pk:3,price:88.88}]
        """
        request_data = request.data
        book_id = kwargs.get("id")

        # 如果id存在且传递的参数是字典   单个修改  修改单个  群改一个
        if book_id and isinstance(request_data, dict):
            book_ids = [book_id, ]
            request_data = [request_data]

        # 如果id不存在且参数是列表 修改多个
        elif not book_id and isinstance(request_data, list):
            book_ids = []
            # 将要修改的图书的id取出放进 book_ids中
            for dic in request_data:
                pk = dic.pop("pk", None)
                if pk:
                    book_ids.append(pk)
                else:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "PK不存在",
                    })
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "数据格式有误",
            })

        # print(request_data)
        # print(book_ids)

        # TODO  需要对传递过来的id与 request_data 进行筛选  id对应的图书是否存在
        # TODO 如果id对应的图书不存在  移除id  id对应的request_data也要移除  如果存在 则查询出对应的图书进行修改
        book_list = []  # 所有要修改的图书对象
        new_data = []  # 所有要修改的参数
        # TODO 禁止在循环中对列表的长度做改变
        for index, pk in enumerate(book_ids):
            try:
                book_obj = Book.objects.get(pk=pk)
                book_list.append(book_obj)
                new_data.append(request_data[index])
                # print(request_data[index])
            except:
                # 如果图书对象不存在  则将id与对应数据都移除
                # index = book_ids.index(pk)
                # request_data.pop(index)
                continue

        book_ser = BookModelSerializerV2(data=new_data, instance=book_list, partial=True, many=True)
        book_ser.is_valid(raise_exception=True)
        book_ser.save()

        return Response({
            "status": status.HTTP_200_OK,
            "message": "修改成功",
        })


"""
查询单个  查询多个  增加单个  增加多个 删除单个  删除多个  局部修改单个  整体修改单个
整体修改多个  局部修改多个
"""
