# 📃 About

**Special Recipe** is a website where you can find the recipes you need and save them if necessary.
Recipe search is presented by categories and keyword search, but users can also simply browse through 
all available recipes.
The site provides the ability to create / edit an account, change or reset the password if it has been lost, 
as well as email verification.

> ***The project was created for educational purposes.***
> 
# 🔥 Features

* **Django Rest API**
* **Keyword search**
* **Search by category**
* **Registration / Authorization**
* **User profile**
* **Profile editing**
* **Password change / reset**
* **Email verification**
* **Recipe markdown editing**
* **Postponed Tasks / Celery**
  * **Delayed sending of emails**
* **Tests**
  * **94% coverage**
* **Bookmarks / Saves**
  * **Without reloading the page**
  * **With animation**

# ❕ Peculiarities

* For correct display, **at least 3 recipes must be created** regardless of the category.
* For correct display of images, their **aspect ratio must be 16:10**. Example: **1440×900, 1536×960, 1680:1050, 1920x1200...**

# 📜 Requirements

* **Python - 3.11**
* **Django - 3.2.16**
* **django-debug-toolbar - 3.8.1**
* **django-environ - 0.9.0**
* **django-summernote - 0.8.20.0**
* **django-redis - 5.2.0**
* **django-cleanup - 7.0.0**
* **Pillow - 9.4.0**
* **humanize - 4.6.0**
* **celery - 5.2.7**

# 💽 Local: Development

1. Clone or download the repository.
2. Create a virtual environment and install requirements from requirements/local.txt file.
3. Create an **.env** file or rename **.env.dist** in **.env** and populate it **only with development variables**:
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

> * **All actions with files are performed in the project directory.**
> * **Don't forget to install docker and docker compose first.**
 
### Project Deployment:

1. Clone or download the repository and go to its directory.
2. Create an **.env** file or rename **.env.dist** in **.env** and populate it with all variables from **.env.dist** file.
3. Open data/nginx/**nginx.conf** file and change `server_name example.com www.example.com;` to your domains.
4. Grant executable rights to the **entrypoint.sh** script: `chmod +x ./entrypoint.sh`
5. Start the services: `docker-compose up --build -d`

### Obtaining an ssl certificate:

1. Access nginx container: `docker exec -it <nginx-container-id> bin/sh`
2. Get ssl certificate: `certbot --nginx`
3. Done ! Now you can exit from nginx container: `exit`

# 🌄 Demonstration
* **Recipes page**

![firefox_aWCIlczEsK](https://user-images.githubusercontent.com/97694131/220066734-baa81672-6c34-4493-a734-25923d7e2dd5.jpg)
![firefox_Kwiy02Peyv](https://user-images.githubusercontent.com/97694131/220066751-f4e56670-b28f-46b1-a2d4-2f8be6f56dff.png)
<hr>

* **Recipe description pages**

![firefox_BIptF7qvNF](https://user-images.githubusercontent.com/97694131/220067183-6f268b3f-4df7-40a8-9a0d-1e22fd434b10.png)
![firefox_ClWNl4FRLr](https://user-images.githubusercontent.com/97694131/220067195-5c6fce3f-486e-41df-b269-514256f3d2b6.png)
<hr>

![firefox_MwRO5h1mmH](https://user-images.githubusercontent.com/97694131/220067240-2a42cc0a-e34e-4a6c-bf21-e44381d398d6.png)
![firefox_O44yFDikVk](https://user-images.githubusercontent.com/97694131/220067264-7c6a5fcf-1216-44b6-906f-90e4cdfc3f6d.png)
<hr>

* **Bookmarks page**

![firefox_t9L3dG0iBa](https://user-images.githubusercontent.com/97694131/222557584-4e93b400-62d9-4954-8154-fd2b1eff4a92.png)
<hr>

* **Profile pages**

![firefox_fQs32ahCuf](https://user-images.githubusercontent.com/97694131/220067565-e827dbe7-6770-43f1-bf5f-dc2915d6ba79.png)
![firefox_VGOM765r25](https://user-images.githubusercontent.com/97694131/220067583-e506937b-9ea7-45ba-8af7-d01021e7c244.png)
<hr>

* **Authentication pages**

![firefox_z9ORAIUYAf](https://user-images.githubusercontent.com/97694131/220067677-08dd1c7c-29a9-45db-9bb5-24f453c1e017.png)
![firefox_OHwLoPAKEr](https://user-images.githubusercontent.com/97694131/220067688-9b4f426a-edc5-4aba-baab-b6756febe96e.png)

* **Animation of adding / removing from bookmarks**

![recipe-animation](https://user-images.githubusercontent.com/97694131/228067650-30dff9d6-9671-4081-bd70-18606594cc17.gif)
