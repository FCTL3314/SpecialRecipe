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
* Password change / reset
* Email verification
* Postponed Tasks / Celery
  * Delayed sending of emails
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
* django-cleanup - 7.0.0
* Pillow - 9.4.0
* humanize - 4.6.0
* celery - 5.2.7

# 💽 Local: Development

1. Clone or download the repository.
2. Create a virtual environment and install requirements from requirements/local.txt file.
3. Create an .env file or rename .env.dist in .env and populate it with development variables from .env.dist file:
   * DEBUG
   * SECRET_KEY
   * DOMAIN_NAME
   * ALLOWED_HOSTS
   * REDIS_HOST
   * REDIS_PORT
   * EMAIL_HOST_USER
   * RECIPES_PAGINATE_BY
4. Make migrations:
   * `python manage.py makemigrations`
   * `python manage.py migrate`
5. Run redis:
   * [**Windows**](https://github.com/microsoftarchive/redis/releases)
   * [**Linux**](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-22-04)
6. Run celery:
   * **Windows:** `celery -A core worker -l INFO -P solo`
   * **Linux:** `celery -A core worker -l INFO`
7. Run development server:
   * `python manage.py runserver`

# 🐳 Docker: Production

> *All actions are performed in the project directory.*

1. Clone or download the repository and go to its directory.
2. Install docker and docker-compose:
   * `apt install -y docker`
   * `apt install -y docker-compose`
3. Create an .env file or rename .env.dist in .env and populate it with all variables from .env.dist file.
4. Open **init-letsencrypt.sh** script and change `domains=(your-domain.com www.your-domain.com)` to your domains.
5. Open data/nginx/**nginx.conf** file and change `server_name your-domain.com www.your-domain.com;` to your domains.
6. Grant executable rights to the all scripts:
   * `chmod +x ./init-letsencrypt.sh`
   * `chmod +x ./entrypoint.sh`
7. Execute **init-letsencrypt.sh**: `./init-letsencrypt.sh`
   > If you get `No such file or directory` exception, run the `sed -i -e 's/\r$//' init-letsencrypt.sh` command, 
   > and then run the script again `./init-letsencrypt`.
8. Add the following lines to the data/nginx/**nginx.conf** file:
   ```
   server {
       listen 443 ssl;
       server_name your-domain.com www.your-domain.com;
       server_tokens off;

       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       include /etc/letsencrypt/options-ssl-nginx.conf;
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

       location / {
           proxy_pass http://core;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header Host $host;
               proxy_redirect off;
       }

       location /static/ {
           alias /usr/src/SpecialRecipe/static/;
       }

       location /media/ {
           alias /usr/src/SpecialRecipe/media/;
       }
   }
   ```
   > Don't forget to change `server_name your-domain.com www.your-domain.com;` to your domains.
9. Start the services: `docker-compose up --build -d`
10. Execute **init-letsencrypt.sh** again: `./init-letsencrypt.sh`

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
