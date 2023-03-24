from django.test import TestCase

from .models import Author

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings

class AuthorTest(TestCase):

    host = host=settings.HOST+'/api/',

    displayName = 'John Doe'

    github = 'https://github.com/johndoe'

    profileImage = 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg'

    email = 'johndoe@gmail.com'

    username = 'johndoe'

    confirmed = True

    def create_author(self):
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
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
        author = Author(host=None,displayName=self.displayName,
               github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty display name
        author = Author(displayName=None,host=settings.HOST+'/api/',
               github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty github
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
                        github=None, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty email
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=None, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Empty username
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=None, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

    def test_create_author_invalid_argument(self):

        # Invalid host URL
        author = Author(host=123,displayName=self.displayName,
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid github URL
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
                        github=456, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid profileImage URL
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
                        github=self.github, profileImage=789, email=self.email, username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)

        # Invalid email
        author = Author(displayName=self.displayName,host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email='google.com', username=self.username, confirmed=self.confirmed)
        self.assertRaises(ValidationError, author.full_clean)


    def test_add_author_to_db(self):
        author = Author(displayName="Jane Doe",host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Jane Doe")

        self.assertEqual(retrieved_author.displayName, "Jane Doe")

    def test_delete_author_from_db(self):
        author = Author(displayName="Deleted Author",host=settings.HOST+'/api/',
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
        author = Author(displayName="Jamie Doe",host=settings.HOST+'/api/',
                        github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)

        author.full_clean()
        author.save()

        retrieved_author = Author.objects.get(displayName="Jamie Doe")

        self.assertEqual(retrieved_author.displayName, "Jamie Doe")

        retrieved_author.displayName = "Anna Doe"

        retrieved_author.save()

        retrieved_author = Author.objects.get(displayName="Anna Doe")

        self.assertEqual(retrieved_author.displayName, "Anna Doe")




