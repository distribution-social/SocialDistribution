from rest_framework import serializers
from ..models import *

class AuthorSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_host(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri('/')

    def get_type(self, obj):
        return "author"

    def get_url(self,obj):
        return ""

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if data['id'] is not None and data['host']:
            data['id'] = data['host'] + "authors/" + data['id']
        
        if data['url'] is not None:
            data['url'] = data['id']
        return data

    class Meta:
        model = Author
        fields = ('type', 'id', 'host', 'displayName', 'url', 'github', 'profileImage')


#Need to add comments and comments information here, will be added when comments are done.
class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid')
    author = AuthorSerializer(read_only=True,source='made_by')
    published = serializers.DateTimeField(source='date_published')
    contentType = serializers.CharField(source='content_type')
    comments = serializers.URLField(source='comments_url')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")
        if request:
            uri = request.build_absolute_uri(request.path).replace('/api', '')

            if data['id']:
                data['id'] = uri + data['id']
            
        return data


    class Meta:
        model = Post
        fields = ['title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author', 'comments', 'published', 'visibility', 'unlisted']




