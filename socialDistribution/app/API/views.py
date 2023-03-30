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

class AuthorListAPIView(BasicAuthMixin,APIView):
    """ Used for Author based actions."""
    def get(self, request):
        """Returns a list of local authors on the node.
        """
        authors = Author.objects.filter(host=settings.HOST + "/api/",confirmed=True).order_by('displayName')
        paginator = CustomPaginator()
        result_page = paginator.paginate_queryset(authors, request)
        serializer = AuthorSerializer(result_page, many=True,context={'request':request,'kwargs':{}})

        data = {
            "type": "authors",
            "items": serializer.data
        }
        return Response(data)


class SingleAuthorAPIView(BasicAuthMixin,APIView):

    def get(self, request, author_id):
        """Returns an author profile"""
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": "Author does not exist"}, status=404)


        serializer = AuthorSerializer(author, context={'request':request,'kwargs':{}})

        return Response(serializer.data)

    # In the requirements it says it should be POST. I kept it as put now, is that a typo on requirements since it says it should update the author
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

class InboxView(BasicAuthMixin,APIView):
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

    def post(self,request,author_id):
        """Adds the given object to the author\'s {author_id} inbox.
        Objects can be of type \'post\', \'follow\', \'comment\' or \'like\'"""
        data = json.loads(request.body.decode('utf-8'))
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if data.get('type') == 'follow':
            try:
                actor_id = data.get('actor').get('url')
                actor = Author.objects.get(url=actor_id)
            except Author.DoesNotExist:
                actor = Author(username=parse_values(actor_id).get('author_id'),confirmed=True)
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
                    actor.sent_requests.add(author)
                    author.follow_requests.add(actor)
                    add_to_inbox(actor,author,Activity.FOLLOW,actor)
                else:
                    return Response(f"Already following {author.displayName}",status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif data.get('type') == 'post':
            try:
                actor_id = data.get('author').get('url')
                actor = Author.objects.get(url=actor_id)
            except Author.DoesNotExist:
                actor = Author(username=parse_values(actor_id).get('author_id'),confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('author'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs author:url field.",status=status.HTTP_400_BAD_REQUEST)


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


        elif data.get('type') == 'comment':
        
            try:
                actor_id = data.get('author').get('url')
                actor = Author.objects.get(url=actor_id)
            except Author.DoesNotExist:
                actor = Author(username=parse_values(actor_id).get('author_id'),confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('author'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: needs author:url field.",status=status.HTTP_400_BAD_REQUEST)


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


        elif data.get('type') == 'like':
            try:
                kwargs = parse_values(data.get('object'))
                actor_kwargs = parse_values(data.get('author').get('url'))
            except AttributeError:
                return Response("Bad request: need object and author:url fields.",status=status.HTTP_400_BAD_REQUEST)


            try:
                actor_id = data.get('author').get('url')
                actor = Author.objects.get(url=actor_id)
            except Author.DoesNotExist:
                actor = Author(username=parse_values(actor_id).get('author_id'),confirmed=True)
                authorSerializer = AuthorSerializer(actor,data.get('author'))
                if authorSerializer.is_valid():
                    authorSerializer.save()
                else:
                    return Response(authorSerializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except AttributeError:
                return Response("Bad request: need author:url field.",status=status.HTTP_400_BAD_REQUEST)


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

    def delete(self,request,author_id):
        """Clears the author\'s {author_id} inbox"""
        try:
            author = Author.objects.get(id=author_id)
            author.my_inbox.all().delete()
        except Author.DoesNotExist:
            return Response({"error": f"Author {author_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)