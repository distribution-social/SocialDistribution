import uuid
from django.utils import timezone
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
import base64
import os
from django.conf import settings

# Create your models here.

class Author(models.Model):
    # Unique ID of the user
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    # Server host of the user
    host = models.URLField(max_length=255)

    url = models.URLField(max_length=255,null=True,blank=True)

    # Max Length: 35 (First Name) + 35 (Last Name)
    displayName = models.CharField(max_length=255)

    github = models.URLField(max_length=255, null=True)

    profileImage = models.URLField(max_length=2048,blank=True, null=True)

    # Max Length: 64 (Username) + 255 (Domain)
    email = models.EmailField(max_length=320)

    username = models.CharField(max_length=255, unique=True)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    following = models.ManyToManyField(
        'self', related_name='followers', symmetrical=False, blank=True)

    sent_requests = models.ManyToManyField('self', related_name='follow_requests', symmetrical=False, blank=True)

    confirmed = models.BooleanField()

    # Used for rapid lookup, will improve database performance
    class Meta:
        indexes = [
            models.Index(fields=['host'], name='host_idx'),
            models.Index(fields=['displayName'], name='displayName_idx'),
            models.Index(fields=['github'], name='github_idx'),
            models.Index(fields=['profileImage'], name='profileImage_idx'),
            models.Index(fields=['email'], name='email_idx'),
            models.Index(fields=['username'], name='username_idx')
        ]

    def save(self, *args, **kwargs):
        if self.url == '' or not self.url:
            self.url = settings.HOST+'/api/authors/'+str(self.id)
        if self.host == '' or not self.host:
            self.host = settings.HOST + '/api/'
        super(Author, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.displayName}"
        # return f"Name: ({self.displayName}) ID: ({self.id}) Host: ({self.host}) URL: ({self.url})"

class Activity(models.Model):
    POST = 'post'
    COMMENT = 'comment'
    FOLLOW = 'follow'
    LIKE = 'like'
    TYPE_CHOICES = [
        (POST,POST),
        (COMMENT,COMMENT),
        (FOLLOW,FOLLOW),
        (LIKE,LIKE)
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(blank = False, null = False)
    content_object = GenericForeignKey()

class Inbox(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    date = models.DateTimeField(default=timezone.now)
    from_author = models.ForeignKey(Author, blank = False, null = False, related_name = "my_outbox", on_delete=models.CASCADE)
    to = models.ForeignKey(Author, blank = False, null = False, related_name = "my_inbox", on_delete=models.CASCADE)
    object = models.OneToOneField(Activity, blank = False, null = True, related_name="inbox_item", on_delete=models.CASCADE)

    # may override delete for deletion of activity when inbox is cleared

    def __str__(self) -> str:
        return f'{self.from_author} -> {self.to}'

class Like(models.Model):
    POST = 'post'
    COMMENT = 'comment'
    TYPE_CHOICES = [
        (POST,POST),
        (COMMENT,COMMENT),
    ]
    summary = models.CharField(max_length=50)
    author = models.ForeignKey(Author, blank = False, null = False, related_name = "liked", on_delete=models.CASCADE)

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey()
    activity = GenericRelation(Activity)

    def __str__(self) -> str:
        if self.type == self.POST:
            return f'{self.author.displayName} -> {self.content_object.made_by.displayName}\'s post: {self.content_object.title}'
        elif self.type == self.COMMENT:
            return f'{self.author.displayName} -> {self.content_object.author.displayName}\'s comment'
        return super().__str__()


class Post(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    made_by = models.ForeignKey(Author, related_name = "my_posts", on_delete=models.CASCADE)

    #if a private post was sent to a friend(only comes into play, when private, otherwise blank).
    receivers = models.ManyToManyField(Author, blank = True, related_name = "private_posts")

    title = models.CharField(max_length=100, unique=False)
    description = models.CharField(max_length=150, blank=True, null=True)

    source = models.URLField(max_length=200)
    origin = models.URLField(max_length=200)

    date_published = models.DateTimeField(default=timezone.now)
    PLAIN = "text/plain"
    MARKDOWN = "text/markdown"
    PNG = "image/png;base64"
    JPG = "image/jpeg;base64"
    CONTENT_TYPE_CHOICES = [
        (MARKDOWN, "Markdown"),
        (PLAIN, "Plain Text"),
        (PNG, "PNG"),
        (JPG, "JPG/JEPG"),
    ]

    content_type = models.CharField(max_length=18, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField(blank=True, null=True)
    comments_url = models.URLField()
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'public'),
        ('PRIVATE', 'private'),
        ('FRIENDS', 'friends'),
    ]
    visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES)
    unlisted = models.BooleanField(default=False)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)

    likes = GenericRelation(Like)
    activity = GenericRelation(Activity)


    def save(self, *args, **kwargs):
        if self.origin == '' or not self.origin:
            self.origin = settings.SCHEME+settings.DOMAIN+'/api/authors/'+str(self.made_by.id)+'/posts/'+str(self.uuid)
        if self.source == '' or not self.source:
            self.source = settings.SCHEME+settings.DOMAIN+'/api/authors/'+str(self.made_by.id)+'/posts/'+str(self.uuid)
        if self.comments_url == '' or not self.comments_url:
            self.comments_url = settings.SCHEME+settings.DOMAIN+'/api/authors/'+str(self.made_by.id)+'/posts/'+str(self.uuid)+'/comments'
        super(Post, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.made_by.username} - {self.title} - {self.uuid}'

class Comment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    published = models.DateTimeField(default=timezone.now)
    PLAIN = "text/plain"
    MARKDOWN = "text/markdown"
    CONTENT_TYPE_CHOICES = [
        (MARKDOWN,MARKDOWN),
        (PLAIN,PLAIN)
    ]
    author = models.ForeignKey(Author, blank = False, null = False, related_name = "comments", on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)

    contentType = models.CharField(max_length=18, choices=CONTENT_TYPE_CHOICES, null=True)
    post = models.ForeignKey(Post, blank = False, null = False, related_name='comments', on_delete=models.CASCADE)
    likes = GenericRelation(Like)
    activity = GenericRelation(Activity)

class Node(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        text = self.username + ":" + self.password
        encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return encoded_text

#The teams we connect to (including ourselves).
class ForeignAPINodes(models.Model):
    nickname = models.CharField(max_length=255, null=True, blank=True)
    base_url = models.URLField(max_length=200, unique=True)

    #allowing it to be blank because team yoshi doesnt have auth
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return f'{self.base_url} - {self.nickname}'

    def getToken(self):
        if not self.username:
            return ""
        text = self.username + ":" + self.password
        encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return encoded_text



