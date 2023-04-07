from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import *
from .serializers import *
from .helpers import *
from .paginators import CustomPaginator
from rest_framework import status
from django.urls import reverse,resolve
from django.core.exceptions import *
from http import HTTPStatus
from .mixins import BasicAuthMixin
from rest_framework.permissions import AllowAny
from django.conf import settings
import json
import base64
from PIL import Image
import io
from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AuthorListAPIView(BasicAuthMixin,APIView):
    """ Used for Author based actions."""
    @swagger_auto_schema(
        operation_description="Returns a list of local authors on the node.",
        responses={
            200: openapi.Response('List of local authors', examples={
                    'application/json': {
                        "type": "authors",
                        "items": [
                            {
                                "id": "1",
                                "displayName": "Author One",
                                "email": "author1@example.com",
                                "host": "https://example.com/api/",
                                "confirmed": True
                            },
                            {
                                "id": "2",
                                "displayName": "Author Two",
                                "email": "author2@example.com",
                                "host": "https://example.com/api/",
                                "confirmed": True
                            }
                        ]
                    }
                } 
            )
        }
    )
    def get(self, request):
        """Returns a list of local authors on the node.
        """
        page_number = request.GET.get('page')
        page_size = request.GET.get('size')
        authors = Author.objects.filter(host=settings.HOST + "/api/",confirmed=True).order_by('displayName')
        if page_number or page_size:
            paginator = CustomPaginator()
            result_page = paginator.paginate_queryset(authors, request)
            serializer = AuthorSerializer(result_page, many=True,context={'request':request,'kwargs':{}})
        else:
            serializer = AuthorSerializer(authors, many=True,context={'request':request,'kwargs':{}})
        data = {
            "type": "authors",
            "items": serializer.data
        }
        return Response(data)


class SingleAuthorAPIView(BasicAuthMixin,APIView):

    @swagger_auto_schema(
        operation_description="Returns an author profile",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e')
        ],
        responses={
            200: openapi.Response('Author Profile', AuthorSerializer, examples={
                    'application/json': {
                        "type":"author",
                        # ID of the Author
                        "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                        # the home host of the author
                        "host":"http://127.0.0.1:5454/",
                        # the display name of the author
                        "displayName":"Lara Croft",
                        # url to the authors profile
                        "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                        # HATEOS url for Github API
                        "github": "http://github.com/laracroft",
                        # Image from a public domain
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                    }
                }
            ),
            404: openapi.Response('Author Not Found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
        
    )
    def get(self, request, author_id):
        """Returns an author profile"""
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist"}, status=404)


        serializer = AuthorSerializer(author, context={'request':request,'kwargs':{}})

        return Response(serializer.data)


    # In the requirements it says it should be POST. I kept it as put now, is that a typo on requirements since it says it should update the author
    @swagger_auto_schema(
        operation_description="Updates an author profile",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e')
        ],
        request_body=AuthorSerializer,
        responses={
            200: openapi.Response('Author Profile', AuthorSerializer, examples={
                    'application/json': {
                        "type":"author",
                        # ID of the Author
                        "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                        # the home host of the author
                        "host":"http://127.0.0.1:5454/",
                        # the display name of the author
                        "displayName":"Lara Croft",
                        # url to the authors profile
                        "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                        # HATEOS url for Github API
                        "github": "http://github.com/laracroft",
                        # Image from a public domain
                        "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                    }
                }
            ),
            400: openapi.Response('Bad Request', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)})),
        }
    )
    def put(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist"}, status=404)

        serializer = AuthorSerializer(author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

class AuthorFollowersAPIView(BasicAuthMixin, APIView):

    @swagger_auto_schema(
        operation_description="Returns a list of all followers of the given author",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e')
        ],
        responses={
            200: openapi.Response('List of Followers', examples={
                    'application/json': {
                        "type": "followers",      
                        "items":[
                            {
                                "type":"author",
                                "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                "host":"http://127.0.0.1:5454/",
                                "displayName":"Greg Johnson",
                                "github": "http://github.com/gjohnson",
                                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                            },
                            {
                                "type":"author",
                                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                "host":"http://127.0.0.1:5454/",
                                "displayName":"Lara Croft",
                                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                "github": "http://github.com/laracroft",
                                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                            }
                        ]
                    }
                }    
            ),
            404: openapi.Response('Author Not Found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
    )                 
    def get(self, request, author_id):
        """Returns a list of all followers of the given """
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({'error': 'Author does not exist'}, status=404)

        followers = author.followers.all()
        serializer = AuthorSerializer(followers, many=True, context={'request':request,'kwargs':{}})

        data = {
            "type": "followers",
            "items": serializer.data
        }

        return Response(data)



class FollowerAPIView(BasicAuthMixin,APIView):
    @swagger_auto_schema(
        operation_description="Returns boolean for if the {follower_author_id} is a follower of {author_id}.",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e'),
            openapi.Parameter('follower_author_id', openapi.IN_PATH, description='Follower Author ID', type=openapi.TYPE_STRING, example='1d698d25ff008f7538453c120f581471')
        ],
        responses={
            200: openapi.Response('Follower Status', examples={
                    'application/json': {
                        "type": "followers",
                        "is_following": True
                    }
                }
            ),
            404: openapi.Response('Author or Follower Author Not Found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
    )
    def get(self, request, author_id, follower_author_id):
        """Returns boolean for if the {follower_author_id} is a follower of {author_id}."""
        try:
            author = Author.objects.get(id=author_id)
            foreign_author = Author.objects.get(id=follower_author_id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        is_following = foreign_author in author.followers.all()
        data = {
            "type": "followers",
            "is_following": is_following
        }
        return Response(data)

    #How to authenticate, do we need to set up like for example JWT tokens?
    @swagger_auto_schema(
        operation_description="Add {follower_author_id} as a follower of {author_id}.",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e'),
            openapi.Parameter('follower_author_id', openapi.IN_PATH, description='Follower Author ID', type=openapi.TYPE_STRING, example='1d698d25ff008f7538453c120f581471')
        ],
        responses={
            201: openapi.Response('Follower Added'),
            404: openapi.Response('Author or Follower Author Not Found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
    )
    def put(self, request, author_id, follower_author_id):
        try:
            author = Author.objects.get(id=author_id)
            foreign_author = Author.objects.get(id=follower_author_id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # # check if authenticated user is the author
        # if request.user != author:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)

        author.followers.add(foreign_author)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Unfollows {follower_author_id} from {author_id}.",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e'),
            openapi.Parameter('follower_author_id', openapi.IN_PATH, description='Follower Author ID', type=openapi.TYPE_STRING, example='1d698d25ff008f7538453c120f581471')
        ],
        responses={
            204: openapi.Response('Follower Removed'),
            404: openapi.Response('Author or Follower Author Not Found', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}))
        }
    )
    def delete(self, request, author_id, follower_author_id):
        """Unfollows {follower_author_id} from {author_id.}"""
        try:
            author = Author.objects.get(id=author_id)
            foreign_author = Author.objects.get(id=follower_author_id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # # check if authenticated user is the author
        # if request.user != author:
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)

        if foreign_author in author.followers.all():
            author.followers.remove(foreign_author)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PublicPostsAPIView(BasicAuthMixin,APIView):
    """Gets all public posts"""
    @swagger_auto_schema(
    operation_description="Gets all public posts",
        responses={
            200: openapi.Response('List of Public Posts', examples={
                    'application/json': {
                        'type': 'public_posts',
                        'items': [
                            {
                                "type":"post",
                                # title of a post
                                "title":"A post title about a post about web dev",
                                # id of the post
                                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                                # where did you get this post from?
                                "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
                                # where is it actually from
                                "origin":"http://whereitcamefrom.com/posts/zzzzz",
                                # a brief description of the post
                                "description":"This post discusses stuff -- brief",
                                # The content type of the post
                                # assume either
                                # text/markdown -- common mark
                                # text/plain -- UTF-8
                                # application/base64
                                # image/png;base64 # this is an embedded png -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
                                # image/jpeg;base64 # this is an embedded jpeg
                                # for HTML you will want to strip tags before displaying
                                "contentType":"text/plain",
                                "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                                # the author has an ID where by authors can be disambiguated
                                "author":{
                                    "type":"author",
                                    # ID of the Author
                                    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                    # the home host of the author
                                    "host":"http://127.0.0.1:5454/",
                                    # the display name of the author
                                    "displayName":"Lara Croft",
                                    # url to the authors profile
                                    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                    # HATEOS url for Github API
                                    "github": "http://github.com/laracroft",
                                    # Image from a public domain (optional, can be missing)
                                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                },
                                # categories this post fits into (a list of strings
                                "categories":["web","tutorial"],
                                # comments about the post
                                # return a maximum number of comments
                                # total number of comments for this post
                                "count": 1023,
                                # the first page of comments
                                "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                                # commentsSrc is OPTIONAL and can be missing
                                # You should return ~ 5 comments per post.
                                # should be sorted newest(first) to oldest(last)
                                # this is to reduce API call counts
                                "commentsSrc":{
                                    "type":"comments",
                                    "page":1,
                                    "size":5,
                                    "post":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                                    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                                    "comments":[
                                        {
                                            "type":"comment",
                                            "author":{
                                                "type":"author",
                                                # ID of the Author (UUID)
                                                "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                                # url to the authors information
                                                "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                                "host":"http://127.0.0.1:5454/",
                                                "displayName":"Greg Johnson",
                                                # HATEOS url for Github API
                                                "github": "http://github.com/gjohnson",
                                                # Image from a public domain
                                                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                            },
                                            "comment":"Sick Olde English",
                                            "contentType":"text/markdown",
                                            # ISO 8601 TIMESTAMP
                                            "published":"2015-03-09T13:07:04+00:00",
                                            # ID of the Comment (UUID)
                                            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                                        }
                                    ]
                                },
                                # ISO 8601 TIMESTAMP
                                "published":"2015-03-09T13:07:04+00:00",
                                # visibility ["PUBLIC","FRIENDS"]
                                "visibility":"PUBLIC",
                                # for visibility PUBLIC means it is open to the wild web
                                # FRIENDS means if we're direct friends I can see the post
                                # FRIENDS should've already been sent the post so they don't need this
                                "unlisted":False
                                # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
                            }
                        ]
                    }
                }
            )
        }
    )
    def get(self, request):
        posts = Post.objects.filter(visibility="PUBLIC",made_by__host=settings.HOST+'/api/').order_by('-date_published')
        serializer = PostSerializer(posts, many=True, context={'request':request,'kwargs':{}})
        response = {
            'type': 'public_posts',
            'items': serializer.data
        }
        return Response(response,status=200)

class PublicAuthorPostsAPIView(BasicAuthMixin,APIView):
    """Gets all author's public posts"""
    @swagger_auto_schema(
        operation_description="Returns a list of all posts created by the given author",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e')
        ],
        responses={
            200: openapi.Response('List of Author Posts', examples={
                    'application/json': {
                        'type': 'public_posts',
                        'items': [
                            {
                                "type":"post",
                                # title of a post
                                "title":"A post title about a post about web dev",
                                # id of the post
                                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                                # where did you get this post from?
                                "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
                                # where is it actually from
                                "origin":"http://whereitcamefrom.com/posts/zzzzz",
                                # a brief description of the post
                                "description":"This post discusses stuff -- brief",
                                # The content type of the post
                                # assume either
                                # text/markdown -- common mark
                                # text/plain -- UTF-8
                                # application/base64
                                # image/png;base64 # this is an embedded png -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
                                # image/jpeg;base64 # this is an embedded jpeg
                                # for HTML you will want to strip tags before displaying
                                "contentType":"text/plain",
                                "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                                # the author has an ID where by authors can be disambiguated
                                "author":{
                                    "type":"author",
                                    # ID of the Author
                                    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                    # the home host of the author
                                    "host":"http://127.0.0.1:5454/",
                                    # the display name of the author
                                    "displayName":"Lara Croft",
                                    # url to the authors profile
                                    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                    # HATEOS url for Github API
                                    "github": "http://github.com/laracroft",
                                    # Image from a public domain (optional, can be missing)
                                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                },
                                # categories this post fits into (a list of strings
                                "categories":["web","tutorial"],
                                # comments about the post
                                # return a maximum number of comments
                                # total number of comments for this post
                                "count": 1023,
                                # the first page of comments
                                "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                                # commentsSrc is OPTIONAL and can be missing
                                # You should return ~ 5 comments per post.
                                # should be sorted newest(first) to oldest(last)
                                # this is to reduce API call counts
                                "commentsSrc":{
                                    "type":"comments",
                                    "page":1,
                                    "size":5,
                                    "post":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                                    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                                    "comments":[
                                        {
                                            "type":"comment",
                                            "author":{
                                                "type":"author",
                                                # ID of the Author (UUID)
                                                "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                                # url to the authors information
                                                "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                                "host":"http://127.0.0.1:5454/",
                                                "displayName":"Greg Johnson",
                                                # HATEOS url for Github API
                                                "github": "http://github.com/gjohnson",
                                                # Image from a public domain
                                                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                            },
                                            "comment":"Sick Olde English",
                                            "contentType":"text/markdown",
                                            # ISO 8601 TIMESTAMP
                                            "published":"2015-03-09T13:07:04+00:00",
                                            # ID of the Comment (UUID)
                                            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                                        }
                                    ]
                                },
                                # ISO 8601 TIMESTAMP
                                "published":"2015-03-09T13:07:04+00:00",
                                # visibility ["PUBLIC","FRIENDS"]
                                "visibility":"PUBLIC",
                                # for visibility PUBLIC means it is open to the wild web
                                # FRIENDS means if we're direct friends I can see the post
                                # FRIENDS should've already been sent the post so they don't need this
                                "unlisted":False
                                # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
                            }
                        ]
                    }
                }),
            404: openapi.Response('Author Not Found')
        }
    )
    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        posts = Post.objects.filter(visibility="PUBLIC",made_by=author).order_by('-date_published')
        serializer = PostSerializer(posts, many=True, context={'request':request,'kwargs':{}})
        response = {
            'type': 'public_posts',
            'items': serializer.data
        }
        return Response(response,status=200)

class AuthorPostsView(BasicAuthMixin,APIView):

    @swagger_auto_schema(
        operation_description="Gets all posts made by {author_id}.",
        manual_parameters=[
            openapi.Parameter('author_id', openapi.IN_PATH, description='Author ID', type=openapi.TYPE_STRING, example='9de17f29c12e8f97bcbbd34cc908f1baba40658e')
        ],
        responses={
            200: openapi.Response('List of Author Posts', examples={
                    'application/json': {
                        'type': 'public_posts',
                        'items': [
                            {
                                "type":"post",
                                # title of a post
                                "title":"A post title about a post about web dev",
                                # id of the post
                                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                                # where did you get this post from?
                                "source":"http://lastplaceigotthisfrom.com/posts/yyyyy",
                                # where is it actually from
                                "origin":"http://whereitcamefrom.com/posts/zzzzz",
                                # a brief description of the post
                                "description":"This post discusses stuff -- brief",
                                # The content type of the post
                                # assume either
                                # text/markdown -- common mark
                                # text/plain -- UTF-8
                                # application/base64
                                # image/png;base64 # this is an embedded png -- images are POSTS. So you might have a user make 2 posts if a post includes an image!
                                # image/jpeg;base64 # this is an embedded jpeg
                                # for HTML you will want to strip tags before displaying
                                "contentType":"text/plain",
                                "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
                                # the author has an ID where by authors can be disambiguated
                                "author":{
                                    "type":"author",
                                    # ID of the Author
                                    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                    # the home host of the author
                                    "host":"http://127.0.0.1:5454/",
                                    # the display name of the author
                                    "displayName":"Lara Croft",
                                    # url to the authors profile
                                    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                                    # HATEOS url for Github API
                                    "github": "http://github.com/laracroft",
                                    # Image from a public domain (optional, can be missing)
                                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                },
                                # categories this post fits into (a list of strings
                                "categories":["web","tutorial"],
                                # comments about the post
                                # return a maximum number of comments
                                # total number of comments for this post
                                "count": 1023,
                                # the first page of comments
                                "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                                # commentsSrc is OPTIONAL and can be missing
                                # You should return ~ 5 comments per post.
                                # should be sorted newest(first) to oldest(last)
                                # this is to reduce API call counts
                                "commentsSrc":{
                                    "type":"comments",
                                    "page":1,
                                    "size":5,
                                    "post":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e",
                                    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
                                    "comments":[
                                        {
                                            "type":"comment",
                                            "author":{
                                                "type":"author",
                                                # ID of the Author (UUID)
                                                "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                                # url to the authors information
                                                "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                                                "host":"http://127.0.0.1:5454/",
                                                "displayName":"Greg Johnson",
                                                # HATEOS url for Github API
                                                "github": "http://github.com/gjohnson",
                                                # Image from a public domain
                                                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                            },
                                            "comment":"Sick Olde English",
                                            "contentType":"text/markdown",
                                            # ISO 8601 TIMESTAMP
                                            "published":"2015-03-09T13:07:04+00:00",
                                            # ID of the Comment (UUID)
                                            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
                                        }
                                    ]
                                },
                                # ISO 8601 TIMESTAMP
                                "published":"2015-03-09T13:07:04+00:00",
                                # visibility ["PUBLIC","FRIENDS"]
                                "visibility":"PUBLIC",
                                # for visibility PUBLIC means it is open to the wild web
                                # FRIENDS means if we're direct friends I can see the post
                                # FRIENDS should've already been sent the post so they don't need this
                                "unlisted":False
                                # unlisted means it is public if you know the post name -- use this for images, it's so images don't show up in timelines
                            }
                        ]
                    }
                }),
            404: openapi.Response('Author Not Found')
        }
    )       
    def get(self, request, author_id):
        """Gets all posts made by {author_id}."""
        try:
            author = Author.objects.get(id=author_id)

        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        posts = Post.objects.filter(made_by=author).order_by('-date_published')


        paginator = CustomPaginator()
        result_page = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(result_page, many=True, context={'request':request,'kwargs':{'author_id':author_id}})

        for i in range(len(serializer.data)):
            data = serializer.data[i]
            post = posts[i]
            comments = post.comments.all().order_by('-published')

            commentResultPage = paginator.paginate_queryset(comments, request)

            context = {'request':request,'kwargs':{'author_id':author_id,'post_id':data['id'].split("/")[-1]}}
            comment_serializer = CommentSerializer(commentResultPage, many=True, context=context)

            response = {
                "type": "comments",
                "page": paginator.page.number,
                "size": paginator.get_page_size(request),
                "post": get_full_uri(request,'api-post-detail',context['kwargs']),
                "id": get_full_uri(request,'api-post-comments',context['kwargs']),
                "comments": comment_serializer.data,
            }

            data["commentSrc"] = response
            data['count'] = len(comments)
            data["comments"] = get_full_uri(request,'api-post-comments',context['kwargs'])

        result = {
            "type": "posts",
            "items": serializer.data,
        }

        return Response(result,status=status.HTTP_200_OK)

class PostDetailView(BasicAuthMixin,APIView):
    
    @swagger_auto_schema(
        operation_description="Gets details of a singular post, {post_id}",
        responses={
            200: openapi.Response('Success', PostSerializer),
            404: openapi.Response('Post Not Found')
        }
    )
    def get(self, request, author_id, post_id):
        """Gets details of a singular post, {post_id}"""
        try:
            post = Post.objects.get(uuid=str(post_id))

        except Post.DoesNotExist:
            return Response({'error': 'Post does not exist'},status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id}})
        data = serializer.data

        comments = post.comments.all().order_by('-published')
        paginator = CustomPaginator()
        commentResultPage = paginator.paginate_queryset(comments, request)
        context = {'request':request,'kwargs':{'author_id':author_id,'post_id':data['id'].split("/")[-1]}}
        comment_serializer = CommentSerializer(commentResultPage, many=True, context=context)

        response = {
            "type": "comments",
            "page": paginator.page.number,
            "size": paginator.get_page_size(request),
            "post": get_full_uri(request,'api-post-detail',context['kwargs']),
            "id": get_full_uri(request,'api-post-comments',context['kwargs']),
            "comments": comment_serializer.data,
        }

        data["commentSrc"] = response
        data['count'] = len(comments)

        return Response(data)

    # Not sure how creating a post would look like (would the requester also send me the same json.) (NO NEED, we dont use it)
    @swagger_auto_schema(
        operation_description="Creates a post objects for the author {post_id}",
        request_body=PostSerializer,
        responses={
            200: openapi.Response('Success', PostSerializer),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Author Not Found')
        }
    )
    def post(self, request, author_id, post_id):
        """Creates a post objects for the author {post_id}"""
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id, made_by=author)
            return Response({"error": "Post with that id already exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:

            serializer = PostSerializer(post, data=request.data, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id}})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Deletes a post object {post_id}",
        responses={
            204: openapi.Response('Success'),
            404: openapi.Response('Post Not Found')
        }
    )
    def delete(self, request, author_id, post_id):
        """Deletes a post object {post_id}."""
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id, made_by=author)
        except Post.DoesNotExist:
            return Response({'error': 'Post does not exist'},status=status.HTTP_404_NOT_FOUND)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Updates a post object {post_id}",
        request_body=PostSerializer,
        responses={
            200: openapi.Response('Success', PostSerializer),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Post Not Found')
        }
    )
    def put(self, request, author_id, post_id):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id, made_by=author)
        except Post.DoesNotExist:
            post = Post(uuid=post_id, made_by=author)

        serializer = PostSerializer(post,data=request.data, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id}})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentView(BasicAuthMixin,APIView):

    @swagger_auto_schema(
        operation_description="Gets a comment from an authors post {comment_id}.",
        responses={
            200: openapi.Response('Success', CommentSerializer),
            404: openapi.Response('Comment Not Found')
        }
    )
    def get(self,request,author_id,post_id,comment_id):
        """Gets a comment from an authors post {comment_id}."""
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = post.comments.get(uuid=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(comment, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id,'comment_id':comment_id}})

        return Response(serializer.data)

class CommentsView(BasicAuthMixin,APIView):
    """Gets a list of comments for {post_id}."""
    @swagger_auto_schema(
        operation_description="Gets a list of comments for {post_id}.",
        responses={
            200: openapi.Response('Success', CommentSerializer),
            404: openapi.Response('Post Not Found')
        }
    )
    def get(self,request,author_id,post_id):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id)
            comments = post.comments.all().order_by('-published')
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)

        paginator = CustomPaginator()
        commentResultPage = paginator.paginate_queryset(comments, request)

        context = {'author_id':author_id,'post_id':post_id}
        serializer = CommentSerializer(commentResultPage, many=True, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id}})

        response = {
            "type": "comments",
            "page": paginator.page.number,
            "size": paginator.get_page_size(request),
            "post": get_full_uri(request,'api-post-detail',context),
            "id": get_full_uri(request,'api-post-comments',context),
            "comments": serializer.data,
        }

        return Response(response,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Adds a comment to {post_id}",
        request_body=CommentSerializer,
        responses={
            200: openapi.Response('Success', CommentSerializer),
            400: openapi.Response('Bad Request'),
            404: openapi.Response('Post Not Found')
        }
    )
    def post(self, request, author_id, post_id):
        """Adds a comment to {post_id}"""
        try:
            user = Author.objects.get(id=parse_values(request.data.get('author').get('id')).get('author_id'))
        except:
            return Response({"error": "Comment Author does not exist"}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data, context={'request':request,'post':post,'user':user,'kwargs':{'author_id':author_id,'post_id':post_id}})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikesPostView(BasicAuthMixin, APIView):
    """Gets all the likes for a post {post_id}"""
    @swagger_auto_schema(
        operation_description="Gets all the likes for a post {post_id}",
        responses={
            200: openapi.Response('Success', LikeSerializer),
            404: openapi.Response('Post Not Found')
        }
    )
    def get(self,request,author_id,post_id):
        try:
            post = Post.objects.get(uuid=post_id)
            likes = post.likes.all()
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LikeSerializer(likes, many=True, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id}})
        response = {
            'type': 'likes',
            'items': serializer.data
        }
        return Response(response,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Gets all the likes for a post {post_id}",
        responses={
            201: openapi.Response('Success'),
            400: openapi.Response('Bad Request'),
        }
    ) 
    def post(self, request, author_id, post_id):
        """Adds a like to the {post_id}"""
        user = Author.objects.get(id=parse_values(request.data.get('author').get('id')).get('author_id'))

        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist:
            return Response({"error": f"Post {post_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if user == post.made_by:
            return Response({"error": "Can't like your own post"}, status=400)
        found = post.likes.filter(author=user)
        if found:
            return Response({"error": "Already liked post"}, status=400)
        serializer = LikeSerializer(data=request.data, context={'request':request,'user':user,'post':post,'kwargs':{'author_id':author_id,'post_id':post_id}})
        if serializer.is_valid():
            serializer.save()
            response = serializer.data
            return Response(response,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikesCommentView(BasicAuthMixin,APIView):
    """Gets the comment for a post {post_id}"""
    @swagger_auto_schema(
        operation_description="Gets all the likes for a comment {comment_id}",
        responses={
            200: openapi.Response('Success', LikeSerializer),
            404: openapi.Response('Comment Not Found')
        }
    )
    def get(self,request,author_id,post_id,comment_id):
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist:
            return Response({"error": f"Post {post_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = post.comments.get(uuid=comment_id)
            likes = comment.likes.all()
        except Comment.DoesNotExist:
            return Response({"error": f"Comment {comment_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LikeSerializer(likes, many=True, context={'request':request,'kwargs':{'author_id':author_id,'post_id':post_id,'comment_id':comment_id}})
        response = {
            'type': 'likes',
            'items': serializer.data
        }
        return Response(response,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Adds a like to the comment {comment_id}",
        responses={
            201: openapi.Response('Success'),
            400: openapi.Response('Bad Request'),
        }
    )
    def post(self, request, author_id, post_id, comment_id):
        "Adds a like to the comment {comment_id}"
        user = Author.objects.get(id=get_values_from_uri(request.data.get('author').get('id'),add_api=True).get('author_id'))

        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist:
            return Response({"error": f"Post {post_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
        try:
            comment = post.comments.get(uuid=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": f"Comment {comment_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if user == comment.author:
            return Response({"error": "Can't like your own comment"}, status=status.HTTP_400_BAD_REQUEST)
        found = comment.likes.filter(author=user)
        if found:
            return Response({"error": "Already liked comment"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LikeSerializer(data=request.data, context={'request':request,'user':user,'comment':comment,'kwargs':{'author_id':author_id,'post_id':post_id,'comment_id':comment_id}})
        if serializer.is_valid():
            serializer.save()
            response = serializer.data
            return Response(response,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikedView(BasicAuthMixin,APIView):
    def get(self,request,author_id):
        """Gets all things the author {author_id} likes"""
        try:
            author = Author.objects.get(id=author_id)
            liked = author.liked.all()
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeSerializer(liked, many=True, context={'request':request,'kwargs':{'author_id':author_id}})

        response = {
            "type": "liked",
            "items": serializer.data,
        }

        return Response(response,status=status.HTTP_200_OK)

class PostImageView(BasicAuthMixin, APIView):
     def get(self,request,author_id,post_id):
        """Gets a image for image post."""
        try:
            post = Post.objects.get(uuid=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)
        if post.content_type == "image/png;base64":
            with open("PostImage.png", "wb") as fh:
                fh.write(base64.decodebytes(post.content.encode()))
            return FileResponse(open("PostImage.png", 'rb'), status=status.HTTP_200_OK, content_type="image/png")
        elif post.content_type == "image/jpeg;base64":
            content = post.content
            return Response(content, status=status.HTTP_200_OK)

        return Response({"error": "Image does not exist."}, status=status.HTTP_404_NOT_FOUND)

class InboxView(BasicAuthMixin,APIView):

    @swagger_auto_schema(
        operation_description="Gets the inbox of the author {author_id}",
        responses={
            200: openapi.Response('Success', ActivitySerializer),
            400: openapi.Response('Bad Request'),
        }
    )
    def get(self,request,author_id):
        """Retrieves the inbox of the author {author_id}"""
        try:
            author = Author.objects.get(id=author_id)
            items = author.my_inbox.all().order_by("-date")
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        item_list = []
        author_serializer = AuthorSerializer(author, context={'request':request,'kwargs':{'author_id':author_id}})
        for item in items:
            serializer = ActivitySerializer(item.object, context={'request':request,'kwargs':{'author_id':author_id}})
            item_list.append(serializer.data.get('content_object'))
        reponse = {
            'type': 'inbox',
            'author': author_serializer.data.get('id'),
            'items': item_list
        }
        return Response(reponse,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Adds the given object to the author\'s {author_id} inbox. Objects can be of type \'post\', \'follow\', \'comment\' or \'like\'",
        request_body=ActivitySerializer,
        responses={
            201: openapi.Response('Success'),
            400: openapi.Response('Bad Request'),
        }
    )
    def post(self,request,author_id):

        """Adds the given object to the author\'s {author_id} inbox.
        Objects can be of type \'post\', \'follow\', \'comment\' or \'like\'"""

        # import pdb; pdb.set_trace()
        data = json.loads(request.body.decode('utf-8'))

        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if str(data.get('type')).lower() == 'follow':
            try:
                actor_id = parse_values(request.data.get('actor').get('id')).get('author_id')
                actor = Author.objects.get(id=actor_id)
            except Author.DoesNotExist:
                foreign_uuid = actor_id
                actor = Author(id=uuid.UUID(
                    foreign_uuid),username=uuid.UUID(
                    foreign_uuid), confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('actor'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs actor:url field.",status=status.HTTP_400_BAD_REQUEST)

            try:
                if actor not in author.followers.all():
                    # Should be no op if it's handled somewhere
                    print(f"Got a follow requests from {actor} to {author}")
                    actor.sent_requests.add(author)
                    # author.follow_requests.add(actor)
                    add_to_inbox(actor,author,Activity.FOLLOW,actor)
                else:
                    return Response(f"Already following {author.displayName}",status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif str(data.get('type')).lower() == 'post':
            try:
                actor_id = parse_values(request.data.get('author').get('id')).get('author_id')
                actor = Author.objects.get(id=actor_id)
            except Author.DoesNotExist:
                foreign_uuid = actor_id
                actor = Author(id=uuid.UUID(
                    foreign_uuid),username=uuid.UUID(
                    foreign_uuid), confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('author'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs actor:url field.",status=status.HTTP_400_BAD_REQUEST)


            try:
                post_id = data.get('origin')
                post = Post.objects.get(origin=post_id)
            except Post.DoesNotExist:
                post = Post(made_by=actor)
                post_serializer = PostSaveSerializer(post,data=data,context={'request':request,'kwargs':{'author_id':author_id}})
                if post_serializer.is_valid():
                    post_serializer.save()
                else:
                    return Response(post_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs origin field.",status=status.HTTP_400_BAD_REQUEST)
            try:
                add_to_inbox(actor,author,Activity.POST,post)
            except Exception as e:
                return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif str(data.get('type')).lower() == 'accept':
            # Actor (author) sends the object a follow request
            # Actor (author) is the current user (us)
            # Object accepts the actor and send the accepts response
            # We add the object to our following
            # We add ourselves to the object's followers

            try:
                actor_id = parse_values(request.data.get('object').get('id')).get('author_id')
                object = Author.objects.get(id=actor_id)
            except Author.DoesNotExist:
                foreign_uuid = actor_id
                object = Author(id=uuid.UUID(
                    foreign_uuid),username=uuid.UUID(
                    foreign_uuid), confirmed=True)
                authorSerializer = AuthorSerializer(object,data.get('object'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs actor:url field.",status=status.HTTP_400_BAD_REQUEST)

            try:
                if object not in author.following.all():
                    # Add our current author as one of the object's followers
                    object.followers.add(author)

                    # Add the object as one of our current author's following
                    author.following.add(object)

                    # Remove from sent_requests
                    author.sent_requests.remove(object)

                    # Remove from follow_requests
                    object.follow_requests.remove(author)

                    # add_to_inbox(actor, author, 'accept', actor)
                    print(f"{object.displayName} accepted {author.displayName}'s follow request")
                else:

                    # add_to_inbox(actor, author, 'accept', actor)

                    return Response(f"Already following {object.displayName}", status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        elif str(data.get('type')).lower() == 'comment':

            try:
                actor_id = parse_values(request.data.get('author').get('id')).get('author_id')
                actor = Author.objects.get(id=actor_id)
            except Author.DoesNotExist:
                foreign_uuid = actor_id
                actor = Author(id=uuid.UUID(
                    foreign_uuid),username=uuid.UUID(
                    foreign_uuid), confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('author'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs actor:url field.",status=status.HTTP_400_BAD_REQUEST)


            try:
                post_id = data.get('object').split('/')[-1]
                post = Post.objects.get(uuid=post_id)
            except Post.DoesNotExist:
                return Response({'error':f'Post {post_id} does not exist.'},status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs id field.",status=status.HTTP_400_BAD_REQUEST)


            comment_text = data.get('comment')
            comment = Comment(author=actor,post=post, comment=comment_text)
            comment_serializer = CommentSerializer(comment,data=data,context={'request':request,'kwargs':{'author_id':author_id}})
            if comment_serializer.is_valid():
                comment_serializer.save()
            else:
                # import pdb; pdb.set_trace()
                return Response(comment_serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            try:
                add_to_inbox(actor,author,Activity.COMMENT,comment)
            except Exception as e:
                return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        elif str(data.get('type')).lower() == 'like':
            try:
                kwargs = parse_values(data.get('object'))
                actor_kwargs = parse_values(data.get('author').get('id'))
            except AttributeError:
                return Response("Bad request: need object and author:url fields.",status=status.HTTP_400_BAD_REQUEST)


            try:
                actor_id = actor_kwargs.get('author_id')
                actor = Author.objects.get(id=actor_id)
            except Author.DoesNotExist:
                foreign_uuid = actor_id
                actor = Author(id=uuid.UUID(
                    foreign_uuid),username=uuid.UUID(
                    foreign_uuid), confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('author'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs actor:url field.",status=status.HTTP_400_BAD_REQUEST)


            try:
                post_id = kwargs.get('post_id')
                post = Post.objects.get(uuid=post_id)
            except Post.DoesNotExist:
                return Response({'error':f'Post {post_id} does not exist.'},status=status.HTTP_404_NOT_FOUND)
            if kwargs.get('comment_id'):
                try:
                    comment_id = kwargs.get('comment_id')
                    comment = Comment.objects.get(uuid=comment_id)
                except Comment.DoesNotExist:
                    return Response({'error':f'Comment {comment_id} does not exist.'},status=status.HTTP_404_NOT_FOUND)
                except AttributeError:
                    return Response('Bad rquest: need comment_id field.',status=status.HTTP_400_BAD_REQUEST)


                if comment.author.id == actor.id:
                    return Response('Can\'t like your own comment',status=status.HTTP_400_BAD_REQUEST)
                found = comment.likes.filter(author=actor)
                if not found:
                    comment.likes.create(type=Like.COMMENT,author=actor,summary=f'{actor.displayName} liked your comment.')
                    add_to_inbox(actor,comment.author,Activity.LIKE,comment)
                else:
                    return Response('Already liked comment.',status=status.HTTP_400_BAD_REQUEST)
            else:

                if post.made_by.id == actor.id:
                    return Response('Can\'t like your own post')
                found = post.likes.filter(author=actor)
                if not found:
                    post.likes.create(type=Like.POST,author=actor,summary=f'{actor.displayName} liked your comment.')
                    try:
                        add_to_inbox(actor,author,Activity.LIKE,post)
                    except Exception as e:
                        return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response('Already liked post.',status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Type not supported: [\'follow\',\'post\',\'like\',\'comment\']",status=status.HTTP_400_BAD_REQUEST)

        return Response("Added to inbox.",status=status.HTTP_201_CREATED)

    @swagger_auto_schema(  
        operation_description="Clears the author's inbox",
        responses={
            204: openapi.Response("No content"),
            404: openapi.Response("Author does not exist")
        }
    )
    def delete(self,request,author_id):
        """Clears the author\'s {author_id} inbox"""
        try:
            author = Author.objects.get(id=author_id)
            author.my_inbox.all().delete()
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)