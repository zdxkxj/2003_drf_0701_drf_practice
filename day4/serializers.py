from rest_framework import serializers

from api.models import Book


class BookListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        for index, obj in enumerate(instance):
            self.child.update(obj, validated_data[index])
        return instance


class BookModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book

        fields = ("book_name", "price", "publish", "authors", "pic")


        extra_kwargs = {
            "book_name": {
                "required": True,
                "min_length": 3,
                "error_messages": {
                    "required": "图书名是必填的",
                    "min_length": "长度不够，太短啦~"
                }
            },

            "publish": {
                "write_only": True
            },
            "authors": {
                "write_only": True
            },

            "pic": {
                "read_only": True
            }
        }

    def validate_book_name(self, value):

        if "1" in value:
            raise serializers.ValidationError("图书名含有敏感字")

        request = self.context.get("request")
        print(request)
        return value


    def validate(self, attrs):
        price = attrs.get("price", 0)

        if price > 90:
            raise serializers.ValidationError("超过设定的最高价钱~")

        return attrs
