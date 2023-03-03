from django.test import TestCase

from .models import Author

class AuthorTest(TestCase):
    
    host = 'http://127.0.0.1:8000'

    displayName = 'John Doe'

    github = 'https://github.com/johndoe'

    profileImage = 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg'

    email = 'johndoe@gmail.com'

    username = 'johndoe'

    confirmed = True

    def create_author(self):
        author = Author(host=self.host, displayName=self.displayName,
                              github=self.github, profileImage=self.profileImage, email=self.email, username=self.username, confirmed=self.confirmed)
        
        author.full_clean()
        author.save()
        return author
    
    


