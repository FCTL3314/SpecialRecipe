# <center> Special Recipe

# 📃 About

**Special Recipe** is a website where you can search for recipes, bookmark them, and access them as needed. Each recipe
can be viewed in detail along with its comments, and users can optionally leave a comment. The search functionality
allows for both category and keyword searches, while users also have the option to browse all available recipes.
Additionally, the website enables users to create or edit an account, reset lost passwords, and verify email addresses.

> ***The project was created for educational purposes.***

# 🔥 Features

* **Django Rest API**
* **Postponed Tasks / Celery**
* **Recipe bookmarks**
* **Recipe comments**
* **Recipe markdown editing**
* **Registration / Authorization**
* **User profile**
* **Profile editing**
* **Password change / reset**
* **Email verification**
* **Tests**

# ❕ Peculiarities

* For correct display, **at least 3 recipes must be created** regardless of the category.
* For correct display of images, their **aspect ratio must be 16:10**. Example: **1440×900, 1536×960, 1680:1050,
  1920x1200...**

# 📜 Requirements

* **Python - 3.11**
* **Django - 3.2.16**
* **django-debug-toolbar - 3.8.1**
* **django-environ - 0.9.0**
* **django-summernote - 0.8.20.0**
* **django-redis - 5.2.0**
* **django-cleanup - 7.0.0**
* **django-widget-tweaks - 1.4.12**
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
    * CATEGORIES_PAGINATE_BY
    * COMMENTS_PAGINATE_BY
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
2. Create an **.env** file or rename **.env.dist** in **.env** and populate it with all variables from **.env.dist**
   file.
3. Open data/nginx/**nginx.conf** file and change `server_name example.com www.example.com;` to your domains.
4. Grant executable rights to the **entrypoint.sh** script: `chmod +x ./entrypoint.sh`
5. Start the services: `docker-compose up --build -d`

### Obtaining an ssl certificate:

1. Access nginx container: `docker exec -it <nginx-container-id> bin/sh`
2. Get ssl certificate: `certbot --nginx`
3. Done ! Now you can exit from nginx container: `exit`

# 🌄 Demonstration

* **Recipes page**

![firefox_yTZ8EJt8q8](https://user-images.githubusercontent.com/97694131/228911580-e0814d70-2006-420e-955d-25ee7ea6ee0a.jpg)
![firefox_4isgaYhoh9](https://user-images.githubusercontent.com/97694131/229195293-cb6d7a62-00a6-4b3c-a5b1-4df77e45527f.png)
<hr>

* **Recipe description pages**

![firefox_BIptF7qvNF](https://user-images.githubusercontent.com/97694131/220067183-6f268b3f-4df7-40a8-9a0d-1e22fd434b10.png)
![firefox_IBkV7J7xM8](https://user-images.githubusercontent.com/97694131/228911705-615c7bfd-c28a-461a-9b9f-afc550ffb01d.png)
<hr>

![firefox_MwRO5h1mmH](https://user-images.githubusercontent.com/97694131/220067240-2a42cc0a-e34e-4a6c-bf21-e44381d398d6.png)
![firefox_RIhl4T5iWE](https://user-images.githubusercontent.com/97694131/228911721-158156d1-83d6-4d3a-9569-b9bbda2c095e.png)
<hr>

* **Bookmarks page**

![firefox_t9L3dG0iBa](https://user-images.githubusercontent.com/97694131/222557584-4e93b400-62d9-4954-8154-fd2b1eff4a92.png)
<hr>

* **Profile pages**

![firefox_Rjwr6yUSXn](https://user-images.githubusercontent.com/97694131/228260132-94c3b088-46b7-4188-8f1b-a2279133ea9b.png)
![firefox_GVubZrCC1K](https://user-images.githubusercontent.com/97694131/228260184-ba6e80e7-1351-4273-9383-6293d5b673f1.png)
![firefox_aLKDOhKHSg](https://user-images.githubusercontent.com/97694131/228260189-13084b42-4231-4a65-8e80-e00b01a76e3f.png)
<hr>

* **Authentication pages**

![firefox_z9ORAIUYAf](https://user-images.githubusercontent.com/97694131/220067677-08dd1c7c-29a9-45db-9bb5-24f453c1e017.png)
![firefox_OHwLoPAKEr](https://user-images.githubusercontent.com/97694131/220067688-9b4f426a-edc5-4aba-baab-b6756febe96e.png)

* **Animation of adding / removing from bookmarks**

![recipe-animation](https://user-images.githubusercontent.com/97694131/228067650-30dff9d6-9671-4081-bd70-18606594cc17.gif)
