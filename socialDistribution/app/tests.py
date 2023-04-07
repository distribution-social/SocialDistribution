from django.test import TestCase

from .models import *

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
import uuid
import datetime


class AuthorTest(TestCase):

    host = host = settings.HOST+'/api/',

    displayName = 'John Doe'

    github = 'https://github.com/johndoe'

    profileImage = 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg'

    email = 'johndoe@gmail.com'

    username = 'johndoe'

    confirmed = True

    def create_author(self):
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()
        return author

    def test_create_author(self):
        author = self.create_author()
        self.assertTrue(isinstance(author, Author))
        # self.assertEqual(str(user), f"{self.name} ({self.email})")

    def test_create_author_empty(self):

        # Empty Argument
        author = Author()
        self.assertRaises(ValidationError, author.full_clean)

        # Empty host
        author = Author(host=None, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty display name
        author = Author(displayName=None, host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty github
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=None, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty email
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=None, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty username
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=None, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

    def test_create_author_invalid_argument(self):

        # Invalid host URL
        author = Author(host=123, displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid github URL
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=456, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid profileImage URL
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=self.github, profileImage=789, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid email
        author = Author(displayName=self.displayName, host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email='google.com', username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

    def test_add_author_to_db(self):
        author = Author(displayName="Jane Doe", host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Jane Doe")

        self.assertEqual(retrieved_author.displayName, "Jane Doe")

    def test_delete_author_from_db(self):
        author = Author(displayName="Deleted Author", host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Deleted Author")

        self.assertEqual(retrieved_author.displayName, "Deleted Author")

        retrieved_author.delete()

        # Reference: https: // stackoverflow.com/questions/69781507/django-unit-test-an-object-has-been-deleted-how-to-use-assertraise-doesnot
        with self.assertRaises(Author.DoesNotExist):
            Author.objects.get(displayName="Deleted Author")

    def test_update_author_in_db(self):
        author = Author(displayName="Jamie Doe", host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Jamie Doe")

        self.assertEqual(retrieved_author.displayName, "Jamie Doe")

        retrieved_author.displayName = "Anna Doe"

        retrieved_author.save()

        retrieved_author = Author.objects.get(displayName="Anna Doe")

        self.assertEqual(retrieved_author.displayName, "Anna Doe")


class PostTest(TestCase):

    def test_create_post(self):

        post_uuid = uuid.uuid4()

        author1 = Author(displayName="John Doe", host=settings.HOST+'/api/',
                         github="https://github.com/johndoe", profileImage='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg', email="johndoe@gmail.com", username="johndoe", confirmed=True)

        author1.save()

        author_id = author1.id

        author2 = Author(displayName="Jane Doe", host=settings.HOST+'/api/',
                         github="https://github.com/janedoe", profileImage='https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg', email="janedoe@gmail.com", username="janedoe", confirmed=True)

        author2.save()

        author3 = Author(displayName="Henry Doe", host=settings.HOST+'/api/',
                         github="https://github.com/henrydoe", profileImage='https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg', email="henrydoe@gmail.com", username="henrydoe", confirmed=True)

        author3.save()

        post = Post(uuid=post_uuid, made_by=author1, title="Test Title", description="Test Description",
                    source=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}", origin=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}", date_published="2023-04-07T04:48:34.325751Z", content_type="text/plain", content="Test Content", comments_url=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}/comments", visibility="PUBLIC", unlisted=False)

        self.assertTrue(isinstance(post, Post))

    def test_add_post_to_db(self):

        post_uuid = uuid.uuid4()

        author1 = Author(displayName="John Doe", host=settings.HOST+'/api/',
                         github="https://github.com/johndoe", profileImage='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg', email="johndoe@gmail.com", username="johndoe", confirmed=True)

        author1.save()

        author_id = author1.id

        author2 = Author(displayName="Jane Doe", host=settings.HOST+'/api/',
                         github="https://github.com/janedoe", profileImage='https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg', email="janedoe@gmail.com", username="janedoe", confirmed=True)

        author2.save()

        author3 = Author(displayName="Henry Doe", host=settings.HOST+'/api/',
                         github="https://github.com/henrydoe", profileImage='https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg', email="henrydoe@gmail.com", username="henrydoe", confirmed=True)

        author3.save()

        post = Post(uuid=post_uuid, made_by=author1, title="Test Title", description="Test Description",
                    source=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}", origin=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}", date_published="2023-04-07T04:48:34.325751Z", content_type="text/plain", content="Test Content", comments_url=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}/comments", visibility="PUBLIC", unlisted=False)

        post.save()

        post.receivers.add(author2)

        post.receivers.add(author3)

        post.activity.create(type=Activity.COMMENT)

        post.likes.create(type=Activity.COMMENT,
                          summary="My comment", author=author3)

        retrieved_post = Post.objects.get(uuid=post_uuid)

        self.assertEqual(retrieved_post.uuid, post.uuid)

        self.assertEqual(retrieved_post.made_by, post.made_by)

        self.assertEqual(retrieved_post.title, post.title)

        self.assertEqual(retrieved_post.description, post.description)

        self.assertEqual(retrieved_post.origin, post.origin)

        self.assertEqual(retrieved_post.source, post.source)


        self.assertEqual(retrieved_post.content_type, post.content_type)

        self.assertEqual(retrieved_post.content, post.content)

        self.assertEqual(retrieved_post.comments_url, post.comments_url)

        self.assertEqual(retrieved_post.visibility, post.visibility)

        self.assertEqual(retrieved_post.unlisted, post.unlisted)

    def test_delete_post_from_db(self):

        post_uuid = uuid.uuid4()

        author1 = Author(displayName="John Doe", host=settings.HOST+'/api/',
                         github="https://github.com/johndoe", profileImage='https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg', email="johndoe@gmail.com", username="johndoe", confirmed=True)

        author1.save()

        author_id = author1.id

        author2 = Author(displayName="Jane Doe", host=settings.HOST+'/api/',
                         github="https://github.com/janedoe", profileImage='https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg', email="janedoe@gmail.com", username="janedoe", confirmed=True)

        author2.save()

        author3 = Author(displayName="Henry Doe", host=settings.HOST+'/api/',
                         github="https://github.com/henrydoe", profileImage='https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg', email="henrydoe@gmail.com", username="henrydoe", confirmed=True)

        author3.save()

        post = Post(uuid=post_uuid, made_by=author1, title="Test Title", description="Test Description",
                    source=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}", origin=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}", date_published="2023-04-07T04:48:34.325751Z", content_type="text/plain", content="Test Content", comments_url=f"https://www.distribution.social/api/authors/{author_id}/posts/{post_uuid}/comments", visibility="PUBLIC", unlisted=False)

        post.save()

        post.receivers.add(author2)

        post.receivers.add(author3)

        post.activity.create(type=Activity.COMMENT)

        post.likes.create(type=Activity.COMMENT,
                          summary="My comment", author=author3)

        retrieved_post = Post.objects.get(uuid=post_uuid)

        self.assertEqual(retrieved_post.uuid, post_uuid)

        retrieved_post.delete()

        # Reference: https: // stackoverflow.com/questions/69781507/django-unit-test-an-object-has-been-deleted-how-to-use-assertraise-doesnot
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(uuid=post_uuid)





