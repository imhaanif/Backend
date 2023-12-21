
from django.contrib.auth import models
from django.db.models import fields
from rest_framework import serializers
from core.models import Image, Match, User, Notification
from core.models import Item
from accounts.models import User


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'




class ItemSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    class Meta:
        model = Item
        fields = '__all__'



class MatchSerializer(serializers.ModelSerializer):
    lost_item = ItemSerializer()
    found_item = ItemSerializer()
    class Meta:
        model = Match
        exclude = ['face_matching_data',]


class NotificationSerializer(serializers.ModelSerializer):


    class Meta:
        model = Notification
        fields = '__all__'


# class IdeaSerializer(serializers.ModelSerializer):
#     time = serializers.SerializerMethodField(read_only=True)
#     creator = serializers.SerializerMethodField(read_only=True)
#     tag = TagsSerializer(read_only=True, many=True)
#     files = FilesSerializer(read_only=True, many=True)
#     category = CategorySerializer(read_only=True)
#     goal = GoalsSerializer(read_only=True)
#     detail = IdeaDetailSerializer(read_only=True)
#     bot_planing = BPSerializer(read_only=True)

#     class Meta:
#         model = Idea
#         fields = '__all__'
#     def get_time(self, obj):
#         return obj.timestamp.timestamp()
#     def get_creator(self, obj):
#         print(obj)
#         name = f"{obj.owner.fname} {obj.owner.lname}"
#         return name


  
# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = '__all__'
#     def get_time(self, obj):
#         return obj.timestamp.timestamp()
   


