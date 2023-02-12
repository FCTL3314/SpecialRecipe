# 📃 About

**Special Recipe** is a website where you can find the recipes you need and save them if necessary.
Recipe search is presented by categories and keyword search, but users can also simply browse through 
all available recipes.
The site provides the ability to create / edit an account, change or reset the password if it has been lost, 
as well as email verification.

**Link to the website:** https://special-recipe.space/

> ***The project was created for educational purposes.***

# 🔥 Features

* Bookmarks / Saves
* Keyword search
* Search by category
* Registration / Authorization
* User profile
* Profile editing
* Email verification
* Password change / reset
* Recipe markdown editing

# ❕ Peculiarities

* For correct display, **at least 3 recipes must be created** regardless of the category.
* For correct display of images, their **aspect ratio must be 16:10**. Example: **1440×900, 1536×960, 1680:1050, 1920x1200...**

# 📜 Requirements

* Python - 3.11
* Django - 3.2.16
* django-debug-toolbar - 3.8.1
* django-environ - 0.9.0
* django-summernote - 0.8.20.0
* django-redis - 5.2.0
* Pillow - 9.4.0
* humanize - 4.6.0
* celery - 5.2.7

# 💽 Local installation

1. Clone or download the repository.

2. Create a virtual environment and install requirements from requirements/local.txt file.

3. Create an .env file or rename .env.dist in .env and populate it with variables from .env.dist file.

An example of filling in environment variables for local development:
```
# Project
DEBUG=True
SECRET_KEY=%q49hdw+=60wkj7(kl5+m_zv@!6wgjccl6e01u0zf+*c%8=fk@
DOMAIN_NAME=127.0.0.1:8000
ALLOWED_HOSTS=*

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Email
EMAIL_HOST_USER=email@example.com

# Recipes
RECIPES_PAGINATE_BY=9
```

4. Make migrations
```
python manage.py makemigrations
python manage.py migrate
```

# 🌄 Images
* **Recipes page**

![firefox_EbTImtf91k](https://user-images.githubusercontent.com/97694131/218304714-ae387f54-f6e1-4a38-986b-229b880d458a.png)
![firefox_ICwvrpabC1](https://user-images.githubusercontent.com/97694131/218304717-3e6eda9a-ec33-4248-8629-f37d46b2ea27.png)
<hr>

* **Recipe description pages**

![firefox_TcArWFj7V1](https://user-images.githubusercontent.com/97694131/218304936-0dd3ecc7-77c0-4b51-989b-189e22e14ee8.png)
![firefox_QqiP4ViNXc](https://user-images.githubusercontent.com/97694131/218304938-12f614eb-eefc-45c2-9f08-b390f473c2ac.png)
<hr>

![firefox_Eeeu1dCB0l](https://user-images.githubusercontent.com/97694131/218304946-fdfdf99a-7a91-4c9f-a6b4-10dbf952c597.png)
![firefox_UyFly3pelp](https://user-images.githubusercontent.com/97694131/218304952-a97b776b-4081-485c-9a22-034ebd15fb15.png)
<hr>

* **Bookmarks page**

![firefox_40rdeV1FtQ](https://user-images.githubusercontent.com/97694131/218304895-655a1529-108d-4a5d-832d-6adbaa7bdaa3.png)
<hr>

* **Profile pages**

![firefox_8Ju1qXjySr](https://user-images.githubusercontent.com/97694131/218304973-4398f787-2241-4ec9-bfb8-85ecd3b0f8f3.png)
![firefox_XdMnzOVPXR](https://user-images.githubusercontent.com/97694131/218304974-1d301bd9-2c2a-4a21-b199-4e8150084144.png)
<hr>

* **Authentication pages**

![firefox_TWTnPDoUww](https://user-images.githubusercontent.com/97694131/218304986-d633adce-fea7-42da-b7d9-2aa6dd0e149c.png)
![firefox_6qLBkDuUnE](https://user-images.githubusercontent.com/97694131/218304988-07cc498c-ad37-451e-a439-378e480dbe0c.png)
