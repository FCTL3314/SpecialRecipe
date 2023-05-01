# 📖 Contents

<ul>
  <li><a href="#-about">About</a></li>
  <li><a href="#-features">Features</a></li>
  <li><a href="#-peculiarities">Peculiarities</a></li>
  <li><a href="#-requirements">Requirements</a></li>
  <li><a href="#-local-development">Local: Development</a></li>
  <li><a href="#-docker-production">Docker: Production</a></li>
  <li><a href="#-demonstration">Demonstration</a></li>
</ul>

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

# 💽 Local: Development

1. Clone or download the repository.
2. Create a virtual environment and install requirements from requirements/local.txt file.
3. Create an **.env** file or rename **.env.dist** in **.env** and populate it **only with development variables**:
    * DEBUG
    * SECRET_KEY
    * DOMAIN_NAME
    * ALLOWED_HOSTS
    * INTERNAL_IPS
    * PROTOCOL
    * REDIS_HOST
    * REDIS_PORT
    * EMAIL_HOST_USER
    * EMAIL_SEND_INTERVAL_SECONDS
    * EMAIL_EXPIRATION_HOURS
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
   * In the REDIS_HOST, you need to specify not the local ip, but the name of the redis container, like this: REDIS_HOST=redis.
3. Open data/nginx/**nginx.conf** file and change `server_name example.com www.example.com;` to your domains.
4. Grant executable rights to the **entrypoint.sh** script: `chmod +x ./entrypoint.sh`
5. Start the services: `docker-compose up --build -d`

### Obtaining an ssl certificate:

1. Access nginx container: `docker exec -it <nginx-container-id> bin/sh`
2. Get ssl certificate: `certbot --nginx`
3. Done ! Now you can exit from nginx container: `exit`

# 🌄 Demonstration

* **Recipes page**

![firefox_NeEAcpxcd3](https://user-images.githubusercontent.com/97694131/233777355-7822ee4d-78fc-451a-a878-d7ebe41ad0e5.jpg)
![firefox_ojqwCSTJJx](https://user-images.githubusercontent.com/97694131/233777357-79e54ab7-0203-400c-82b7-0a7c5343bfea.png)
<hr>


* **Recipe detail pages**

![firefox_0DKWb1eWkW](https://user-images.githubusercontent.com/97694131/233776917-2a9c4dcb-8b3f-412a-98da-3919fd1f9cb3.png)
![firefox_9SFI9HVncg](https://user-images.githubusercontent.com/97694131/233776918-15f30af6-7209-45b6-847d-7ac630c0af3d.png)
<hr>

![firefox_ea9Mhd9I3Y](https://user-images.githubusercontent.com/97694131/233776120-b23f27be-48a1-4fd3-844b-67511b48bf85.png)
![firefox_ICgV4HS1TZ](https://user-images.githubusercontent.com/97694131/233776124-a02bee48-cc5c-45c7-a0a9-39725291fb34.png)
<hr>


* **Bookmarks page**

![firefox_IrbXSTevJy](https://user-images.githubusercontent.com/97694131/233777363-01734e77-3154-4ac6-aa19-cc8925213cfb.png)
<hr>

* **Profile pages**

![firefox_Rjwr6yUSXn](https://user-images.githubusercontent.com/97694131/228260132-94c3b088-46b7-4188-8f1b-a2279133ea9b.png)
![firefox_GVubZrCC1K](https://user-images.githubusercontent.com/97694131/228260184-ba6e80e7-1351-4273-9383-6293d5b673f1.png)
![firefox_aLKDOhKHSg](https://user-images.githubusercontent.com/97694131/228260189-13084b42-4231-4a65-8e80-e00b01a76e3f.png)
<hr>

* **Authentication pages**

![firefox_B4E9sQRVKS](https://user-images.githubusercontent.com/97694131/232253448-ebed7762-8c42-4222-94dc-53b07174ee0e.png)
![firefox_OHwLoPAKEr](https://user-images.githubusercontent.com/97694131/220067688-9b4f426a-edc5-4aba-baab-b6756febe96e.png)

* **Adding / removing from bookmarks**

![recipe-bookmark](https://user-images.githubusercontent.com/97694131/231538126-7de16b2c-2025-469b-be27-608033dda41e.gif)
