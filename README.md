# SocialDistribution


Our Web Service
=================

Located at: https://www.distribution.social/<br />
API at: https://www.distribution.social/api/<br />
AUTHORIZATION: BASIC <br />
username: server1<br />
password: 123<br /><br />

Web Service Coordination
=================

**1. CMPUT404W23T00 (Team Yoshi)<br /><br />**
GITHUB: https://github.com/CMPUT404-Big-Yoshi-Social-Network/yoshi-connect<br />
API: https://yoshi-connect.herokuapp.com/<br />
AUTHORIZATION: BASIC <br />
username: goomba-yoshi<br />
password: 123<br /><br />

**2. CMPUT404W23T01 (Team peer2pressure)<br /><br />**
GITHUB: https://github.com/Peer2Pressure/Peer2Pressure<br />
API: https://p2psd.herokuapp.com/<br />
AUTHORIZATION: BASIC<br />
username: p2padmin<br />
password: p2padmin<br />

**3. CMPUT404W23T03 (Team BiggerYoshi)<br /><br />**
GITHUB: https://github.com/CMPUT404W23-bigger-yoshi/CMPUT404-project-socialdistribution<br />
API: http://bigger-yoshi.herokuapp.com/api/<br />
AUTHORIZATION: No AUTH<br /><br />

Demo Video
=================
https://drive.google.com/drive/folders/1bRVYhAcmzWWbAQxHKvU-swIsFxlX3Ggw

Web Service API & Documentation
=================

We have a webservice API that can be used, with the correct authentication, to<br />
interact with our website. This API is used by other groups to send authors on<br />
our site.<br />

Our API Document is available on https://www.distribution.social/swagger

Test Cases
=================
We have test cases for API and Model testing.

To run tests: `python manage.py test`<br />

These tests check if our API and models are working properly.<br />

AJAX Documentation
=================
We used AJAX to show local and foreign profile.
We used AJAX when liking and commenting things.
We used AJAX for getting posts, comments, and likes.
We used AJAX because we wanted it on the fly and request data from foreign servers which takes some time to arrive.


Instruction
=================

Setting up a virtual environment:
`python -m venv venv`

Activate the virtual environment:
`source venv/bin/activate`

Install the requirements:
`pip install -r requirements.txt`

To run: `python manage.py runserver`

To run tests: `python manage.py test`

Deploying to Heroku
=================
1. Create a new app on Heroku https://dashboard.heroku.com/new-app.

2. Choose an **App Name** and **Region**.

3. Click the **Deploy** tab

4. Clone our repository https://github.com/distribution-social/SocialDistribution.git

5. Using Heroku Git
   1.  Login to Heroku `$ heroku login`
   2.  Add the Heroku remote `heroku git:remote -a app-name`

6. Using GitHub
   1. Fork our repository: https://github.com/distribution-social/SocialDistribution
   2. Search for the repository
   3. Click **Connect** beside the repository you would like to connect

License/Copyright
=================

MIT License

Copyright (c) 2023 Ronggang Cui, Nick Wielgus, Saadman Islam Khan, Daryna Chernyavska, Justin Monteza

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

The template posts.html and static posts.css are derived from html
examples thus parts of these files is Copyright © 2023 bootdey.com
Under the MIT License https://www.bootdey.com/snippets/view/bs4-s

Reference
=================

Refrences for views.py:

        Stackoverflow Answer
        Title: django open specific html tab in response
        https://stackoverflow.com/questions/32564742/django-open-specific-html-tab-in-response
        https://stackoverflow.com/a/32564970
        Author: Alasdair https://stackoverflow.com/users/113962/alasdair

        Stackoverflow Answer
        Title: How can I find the union of two Django querysets?
        https://stackoverflow.com/questions/4411049/how-can-i-find-the-union-of-two-django-querysets
        https://stackoverflow.com/a/4412293
        Author: Jordan Reiter https://stackoverflow.com/users/255918/jordan-reiter

        Stackoverflow Answer
        Title: How do I do an OR filter in a Django query?
        https://stackoverflow.com/questions/739776/how-do-i-do-an-or-filter-in-a-django-query
        https://stackoverflow.com/a/739799
        Author: Alex Koshelev https://stackoverflow.com/users/19772/alex-koshelev


