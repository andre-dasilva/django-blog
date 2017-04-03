# Django Blog

This blog is written in python with the web framework [django (1.9)](https://www.djangoproject.com/)

*Project is pretty much done, but there are some possible extensions. Look at the [TODO's](TODO.md)*

## Installation

Fork the repository and then clone it:

`git clone https://github.com/<USERNAME>/django-blog.git`

Create a virtual environment:

`virtualenv venv`

Install project dependencies:

`pip install -r requirements.txt`

Move into the source directory:

`cd src/`

Create the django database:

`python manage.py makemigrations`  
`python manage.py migrate`

Add a super user to the database:

`python manage.py createsuperuser`

Start the server:

`python manage.py runserver`

Open a browser with the url:

http://localhost:8000/

## Credits

CodingEntrepreneurs for making an awesome youtube channel:

Checkout:  
https://www.youtube.com/user/CodingEntrepreneurs  
https://www.codingforentrepreneurs.com/  
https://github.com/codingforentrepreneurs
