from rest_framework import serializers
from ..models import *
from .helpers import *
from ..helpers import *
from generic_relations.relations import GenericRelatedField
from django.urls import reverse
from django.utils import timezone

class AuthorSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    host = serializers.URLField()
    url = serializers.URLField()

    def get_type(self, obj):
        return "author"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        kwargs = self.context.get('kwargs')
        kwargs = {
            'author_id':instance.id,
        }

        if not data['url'] or data['url'] == '' :
            api = ''
            if str(data['host'] == settings.HOST):
                api = '/api'
            if str(data['host']).endswith('/'):
                data['url'] = str(data['host'])[:-1] + api + "/authors/" + data['id']
            else:
                data['url'] = data['host'] + api + "/authors/" + data['id']
        data['id'] = get_full_uri(request,'api-single_author',kwargs,remove_str='')

        if not data['profileImage']:
            data['profileImage'] = ''

        return data

    class Meta:
        model = Author
        fields = ('type', 'id', 'host', 'displayName', 'url', 'github', 'profileImage')


#Need to add comments and comments information here, will be added when comments are done.
class PostSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    id = serializers.UUIDField(source='uuid')
    author = AuthorSerializer(read_only=True,source='made_by')
    published = serializers.DateTimeField(source='date_published')
    contentType = serializers.CharField(source='content_type')
    comments = serializers.URLField(source='comments_url')

    def get_type(self,obj):
        return "post"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        kwargs = self.context.get('kwargs')
        kwargs = {
            'author_id':instance.made_by.id,
            'post_id':instance.uuid
        }


        data['id'] = get_full_uri(request,'api-post-detail',kwargs,remove_str='')

        post_comments = instance.comments.all()

        # comment_serializer = CommentSerializer(post_comments,many=True)

        # data['commentSrc'] = comment_serializer.data

        return data


    class Meta:
        model = Post
        fields = ['type','title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'comments', 'published', 'visibility', 'unlisted']

class PostSaveSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True,source='made_by')
    published = serializers.DateTimeField(source='date_published')
    contentType = serializers.CharField(source='content_type')
    comments = serializers.URLField(source='comments_url')

    class Meta:
        model = Post
        fields = ['title', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'comments', 'published', 'visibility', 'unlisted']

class CommentSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    id = serializers.UUIDField(required=False,source='uuid')
    author = AuthorSerializer(read_only=True)
    published = serializers.DateTimeField(required=False)
    comment = serializers.CharField()

    def get_type(self,obj):
        return "comment"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        kwargs = self.context.get('kwargs')
        kwargs = {
            'author_id':kwargs.get('author_id'),
            'post_id':instance.post.uuid,
            'comment_id': instance.uuid
        }
        data['id'] = get_full_uri(request,'api-post-comment',kwargs,remove_str='')

        return data

    def create(self, validated_data):
        post = self.context.get('post')
        user = self.context.get('user')
        comment = post.comments.create(**validated_data,author=user)
        return comment

    class Meta:
        model = Comment
        fields = ['type', 'author', 'id', 'comment', 'published']

class LikeSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    author = AuthorSerializer(read_only=True)
    summary = serializers.CharField()
    content_object = GenericRelatedField({
        Post: PostSerializer(),
        Comment: CommentSerializer()
    },required=False)
    object = serializers.URLField(required=False)

    def get_type(self,obj):
        return "like"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        kwargs = self.context.get('kwargs')
        new_data = data

        if isinstance(instance.content_object,Post):
            kwargs = {
                'author_id': kwargs.get('author_id'),
                'post_id': instance.content_object.uuid
            }
            new_data.update({'object': get_full_uri(request,'api-post-detail',kwargs,remove_str='')})

        elif isinstance(instance.content_object,Comment):

            kwargs.update({'post_id': instance.content_object.post.uuid})
            kwargs.update({'comment_id': instance.content_object.uuid})
            new_data.update({'object': get_full_uri(request,'api-post-comment',kwargs,remove_str='')})


        new_data.pop('content_object')
        return new_data

    def create(self, validated_data):
        try:
            validated_data.pop('object')
        except:
            pass
        post = self.context.get('post')
        comment = self.context.get('comment')
        user = self.context.get('user')
        if comment:
            content_object = comment
            receiver = comment.author
            type = Like.COMMENT
        else:
            content_object = post
            receiver = post.made_by
            type = Like.POST
        like = content_object.likes.create(**validated_data,author=user, type=type)
        add_to_inbox(user,receiver,Activity.LIKE,content_object)
        return like

    class Meta:
        model = Like
        fields = ['type', 'author', 'summary','content_object','object']


class ActivitySerializer(serializers.ModelSerializer):
    content_object = GenericRelatedField({
        Post: PostSerializer(),
        Like: LikeSerializer(),
        Comment: CommentSerializer(),
        Author: AuthorSerializer()
    })

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        kwargs = self.context.get('kwargs')
        # kwargs = {
        #     'author_id':kwargs.get('author_id')
        # }
        # data['author'] = get_full_uri(request,'api-author',kwargs)
        return data

    class Meta:
        model = Activity
        fields = [ 'content_object']