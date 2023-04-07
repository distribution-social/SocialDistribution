from rest_framework.test import APITestCase,APIRequestFactory
from rest_framework import status
from .serializers import *
from .views import *
from django.urls import reverse
from ..models import *
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

def create_api_creds():
  return Node.objects.create(username='test',password='test')

def create_authors(length):
  user_list = []
  for i in range(length):
    user_list.append({'username': f'test{i+1}','email': f'test{i+1}@test.ca','password': 'test'})

  return setup_authors(user_list)

def setup_authors(authors):
  for user in authors:
    User.objects.create(
      username=user.get('username'),
      email=user.get('email'),
      password=user.get('password')
    )
    Author.objects.create(
      host=settings.HOST+'/api/',
      displayName=user.get('username'),
      github=f"https://github.com/{user.get('username')}",
      profileImage=None, email=user.get('email'),
      username=user.get('username'),
      confirmed=True
    )
  return Author.objects.all()

# Create your tests here.
class Authors(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)
    self.token = create_api_creds()


  def testAuthorList(self):
    kwargs = {

    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-author-list',kwargs=kwargs),**header)
    self.assertEquals(len(response.data.get('items')),len(self.author_list))

  def testAuthorSingle(self):
    author = self.author_list.first()
    kwargs = {
      'author_id': author.id,
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-single_author',kwargs=kwargs),**header)
    self.assertEquals(response.data.get('displayName'),author.displayName)

  def testAuthorFollowers(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    author_follow.following.add(author)
    kwargs = {
      'author_id': author.id,
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-author-followers',kwargs=kwargs),**header)
    self.assertEquals(len(response.data.get('items')),len(author.followers.all()))
    self.assertEquals(response.data.get('items')[0].get('displayName'),author_follow.displayName)

  def testAuthorFollow(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    author_follow.following.add(author)
    kwargs = {
      'author_id': author.id,
      'follower_author_id': author_follow.id
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-followers',kwargs=kwargs),**header)
    self.assertEquals(response.data.get('is_following'),True)

  def testAuthorDeleteFollow(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    author_follow.following.add(author)
    kwargs = {
      'author_id': author.id,
      'follower_author_id': author_follow.id
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.delete(reverse('api-followers',kwargs=kwargs),**header)
    self.assertEquals(response.status_code,status.HTTP_204_NO_CONTENT)

    response = self.client.delete(reverse('api-followers',kwargs=kwargs),**header)
    self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)

  def testAuthorNotFollow(self):
    author = self.author_list.first()
    author_follow = self.author_list.last()
    kwargs = {
      'author_id': author.id,
      'follower_author_id': author_follow.id
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-followers',kwargs=kwargs),**header)
    self.assertEquals(response.data.get('is_following'),False)


class Posts(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)
    self.token = create_api_creds()


  def testGetAuthorPosts(self):
    author = self.author_list.first()
    author.my_posts.create(title="Test")
    author.my_posts.create(title="Test 2")
    author.my_posts.create(title="Test 3")
    kwargs = {
      'author_id': author.id
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-author-post',kwargs=kwargs),**header)

    self.assertEquals(len(response.data.get('items')),len(author.my_posts.all()))

  def testGetAuthorPostDetail(self):
    author = self.author_list.first()
    post = author.my_posts.create(title="Test",visibility="PUBLIC")
    kwargs = {
      'author_id': author.id,
      'post_id': post.uuid
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-post-detail',kwargs=kwargs),**header)

    self.assertEquals(response.data.get('title'),post.title)


  def testGetAuthorPostDelete(self):
    author = self.author_list.first()
    post = author.my_posts.create(title="Test",visibility="PUBLIC")
    kwargs = {
      'author_id': author.id,
      'post_id': post.uuid
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.delete(reverse('api-post-detail',kwargs=kwargs),**header)
    self.assertEquals(response.status_code,status.HTTP_204_NO_CONTENT)

    response = self.client.delete(reverse('api-post-detail',kwargs=kwargs),**header)
    self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)

class Comments(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)
    self.token = create_api_creds()

    self.post_author = self.author_list.first()
    self.post = self.post_author.my_posts.create(title="Test",visibility="PUBLIC")

  def testGetPostComment(self):
    author = self.author_list.last()
    comment = self.post.comments.create(author=author,comment="New comment")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid,
      'comment_id': comment.uuid
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-post-comment',kwargs=kwargs),**header)
    self.assertEquals(response.data.get('comment'),"New comment")

  def testGetPostComments(self):
    author = self.author_list.last()
    self.post.comments.create(author=author,comment="New comment")
    self.post.comments.create(author=author,comment="New comment2")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-post-comments',kwargs=kwargs),**header)
    self.assertEquals(len(response.data.get('comments')),len(self.post.comments.all()))


class Likes(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user',
      )
    self.author_list = create_authors(5)
    self.token = create_api_creds()

    self.post_author = self.author_list.first()
    self.comment_author = self.author_list.last()
    self.post = self.post_author.my_posts.create(title="Test",visibility="PUBLIC")
    self.comment = self.post.comments.create(author=self.comment_author,comment='comment')

  def testGetPostLikes(self):
    self.post.likes.create(author=self.comment_author,summary="liked post")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-post-likes',kwargs=kwargs),**header)
    self.assertEquals(response.data.get('items')[0].get('summary'),"liked post")

    self.post.likes.create(author=self.comment_author,summary="liked post")
    response = self.client.get(reverse('api-post-likes',kwargs=kwargs),**header)
    self.assertEquals(len(response.data.get('items')),2)

  def testGetCommentLikes(self):
    self.post.likes.create(author=self.comment_author,summary="liked comment")
    self.comment.likes.create(author=self.post_author,summary="liked comment")
    kwargs = {
      'author_id': self.post_author.id,
      'post_id': self.post.uuid,
      'comment_id': self.comment.uuid
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-post-comment-likes',kwargs=kwargs),**header)
    self.assertEquals(response.data.get('items')[0].get('summary'),"liked comment")

    self.comment.likes.create(author=self.comment_author,summary="liked comment")
    response = self.client.get(reverse('api-post-comment-likes',kwargs=kwargs),**header)
    self.assertEquals(len(response.data.get('items')),2)

  def testGetAuthorLiked(self):
    self.post.likes.create(author=self.comment_author,summary="liked comment")
    self.comment.likes.create(author=self.post_author,summary="liked comment")
    self.comment.likes.create(author=self.post_author,summary="liked comment 2")
    kwargs = {
      'author_id': self.post_author.id,
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.get(reverse('api-author-liked',kwargs=kwargs),**header)
    self.assertEquals(len(response.data),2)

class Inbox(APITestCase):

  def setUp(self):
    self.user =  User.objects.create(
        username='user',
        email='user@user.ca',
        password='user'
      )
    self.author_list = create_authors(5)
    self.token = create_api_creds()
    self.actor = self.author_list.first()
    self.receiver = self.author_list.last()

  def test_follow(self):
    payload = {
        "type": "Follow",
        "summary":"Greg wants to follow you",
        "actor":{
            "type":"author",
            "id":f"{self.actor.host}authors/{self.actor.id}",
            "url":f"{self.actor.host}authors/{self.actor.id}",
            "host":f"{self.actor.host}",
            "displayName":f"{self.actor.displayName}",
            "github": f"{self.actor.github}",
            "profileImage": f"{self.actor.profileImage}"
        },
        "object": {
            "type":"author",
            "id":f"{self.receiver.host}authors/{self.receiver.id}",
            "url":f"{self.receiver.host}authors/{self.receiver.id}",
            "host":f"{self.receiver.host}",
            "displayName":f"{self.receiver.displayName}",
            "github": f"{self.receiver.github}",
            "profileImage": f"{self.receiver.profileImage}"
        }
    }
    kwargs = {
      'author_id': self.receiver.id,
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.post(reverse('api-author-inbox',kwargs=kwargs),payload,format='json',**header)
    self.assertEquals(response.status_code,status.HTTP_201_CREATED)
    self.assertEquals(len(self.receiver.my_inbox.all()),1)

  def test_post(self):
    payload = {
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
            "id":f"{self.actor.host}authors/{self.actor.id}",
            "url":f"{self.actor.host}authors/{self.actor.id}",
            "host":f"{self.actor.host}",
            "displayName":f"{self.actor.displayName}",
            "github": f"{self.actor.github}",
            "profileImage": f"{self.actor.profileImage}"
        },
        # categories this post fits into (a list of strings
        "categories":["web","tutorial"],
        # comments about the post
        # return a maximum number of comments
        # total number of comments for this post
        "count": 1023,
        # the first page of comments
        "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
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
    kwargs = {
      'author_id': self.receiver.id,
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.post(reverse('api-author-inbox',kwargs=kwargs),payload,format='json',**header)
    self.assertEquals(response.status_code,status.HTTP_201_CREATED)
    self.assertEquals(len(self.receiver.my_inbox.all()),1)
    self.assertEquals(self.receiver.my_inbox.all().first().object.type,'post')
    self.assertEquals(self.receiver.my_inbox.all().first().object.content_object.title,'A post title about a post about web dev')

  def test_comment(self):
    payload = {
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
            "id":f"{self.actor.host}authors/{self.actor.id}",
            "url":f"{self.actor.host}authors/{self.actor.id}",
            "host":f"{self.actor.host}",
            "displayName":f"{self.actor.displayName}",
            "github": f"{self.actor.github}",
            "profileImage": f"{self.actor.profileImage}"
        },
        # categories this post fits into (a list of strings
        "categories":["web","tutorial"],
        # comments about the post
        # return a maximum number of comments
        # total number of comments for this post
        "count": 1023,
        # the first page of comments
        "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments",
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
    kwargs = {
      'author_id': self.receiver.id,
    }
    header = {
      'HTTP_AUTHORIZATION': f'Basic {self.token}'
    }
    response = self.client.post(reverse('api-author-inbox',kwargs=kwargs),payload,format='json',**header)
    self.assertEquals(response.status_code,status.HTTP_201_CREATED)
    self.assertEquals(len(self.receiver.my_inbox.all()),1)
    self.assertEquals(self.receiver.my_inbox.all().first().object.type,'post')
    self.assertEquals(self.receiver.my_inbox.all().first().object.content_object.title,'A post title about a post about web dev')