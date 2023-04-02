const static_url = '/static/'


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const bookmarkLinks = document.querySelectorAll('.bookmark')

if (bookmarkLinks) {
    bookmarkLinks.forEach(bookmarkLink => {
        bookmarkLink.addEventListener('click', function () {
            const recipeId = this.dataset.recipeId;
            const bookmarkImg = bookmarkLink.querySelector('img');
            const isSaved = bookmarkLink.dataset.isSaved === 'true';
            const bookmarkText = bookmarkLink.querySelector('span');
            const bookmarkCount = parseInt(bookmarkText.textContent);
            const newBookmarkCount = isSaved ? bookmarkCount - 1 : bookmarkCount + 1;

            const url = isSaved ? `/api/v1/bookmarks/${recipeId}/` : '/api/v1/bookmarks/';
            const csrfToken = getCookie('csrftoken');

            const requestOptions = {
                'method': isSaved ? 'DELETE' : 'POST',
                'headers': {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
            }

            if (!isSaved) {
                requestOptions.body = JSON.stringify({'recipe_id': recipeId});
            }

            fetch(url, requestOptions)
                .then(response => {
                    if (response.status === 204) {
                        return response
                    } else if (response.ok) {
                        return response.json();
                    } else if (response.status === 403) {
                        const error = new Error(response.statusText);
                        error.status = 403;
                        throw error;
                    } else {
                        const error = new Error(response.statusText);
                        error.status = response.status
                        throw error;
                    }
                })
                .then(() => {
                    bookmarkText.textContent = `${newBookmarkCount} Saves`;
                    bookmarkImg.src = `${static_url}icon/bookmark${isSaved ? '' : '-fill'}.svg`;
                    bookmarkImg.classList.add('animate__animated', 'animate__flip');
                    bookmarkImg.addEventListener('animationend', function () {
                        this.classList.remove('animate__animated', 'animate__flip');
                    });
                    bookmarkLink.dataset.isSaved = (!isSaved).toString();
                })
                .catch(error => {
                    if (error.status === 403) {
                        const currentUrl = window.location.pathname;
                        const loginUrl = '/accounts/login/?next=' + currentUrl;
                        window.location.replace(loginUrl);
                    } else {
                        console.error(error.message);
                    }
                });
        });
    });
}


const showMoreCategoriesButton = document.querySelector('#show-more-categories-btn')

if (showMoreCategoriesButton) {
    showMoreCategoriesButton.addEventListener('click', function () {
        const page = parseInt(showMoreCategoriesButton.dataset.page);
        const selectedCategorySlug = showMoreCategoriesButton.dataset.selectedCategorySlug;

        const url = `/api/v1/categories/?page=${page}`;
        const method = 'GET';
        const headers = {'Content-Type': 'application/json'};

        fetch(url, {method, headers})
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    const error = new Error(response.statusText);
                    error.status = response.status
                    throw error;
                }
            })
            .then(response => {
                for (const category of response.results) {

                    const categoryName = category.name;
                    const categorySlug = category.slug;

                    const categoryItem = $(
                        `<a class="list-group-item list-group-item-action" href="/recipes/category/${categorySlug}/">
                           ${categoryName}
                         </a>`
                    );

                    if (categorySlug === selectedCategorySlug) {
                        categoryItem.addClass('text-dark bg-body-secondary disabled');
                    }
                    categoryItem.insertBefore(showMoreCategoriesButton);
                }
                response.next === null
                    ? showMoreCategoriesButton.remove()
                    : showMoreCategoriesButton.dataset.page = (page + 1).toString();
            })
            .catch(error => {
                console.error(error.message);
            });
    });
}


const showMoreCommentsButton = document.querySelector('#show-more-comments-btn')

if (showMoreCommentsButton) {
    showMoreCommentsButton.addEventListener('click', function () {
        const commentsContainer = document.getElementById('comments-container');
        const page = parseInt(showMoreCommentsButton.dataset.page);
        const recipeId = parseInt(showMoreCommentsButton.dataset.recipeId)

        const url = `/api/v1/comments/?page=${page}&recipe_id=${recipeId}`;
        const method = 'GET';
        const headers = {'Content-Type': 'application/json'};

        fetch(url, {method, headers})
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    const error = new Error(response.statusText);
                    error.status = response.status
                    throw error;
                }
            })
            .then(response => {
                for (const comment of response.results) {

                    const authorImage = comment.author.image
                        ? comment.author.image
                        : `${static_url}img/default_user_image.png`;
                    const authorUsername = comment.author.username;
                    const authorSlug = comment.author.slug;
                    const commentCreatedDate = moment(comment.created_date).fromNow();
                    const commentText = comment.text;

                    const commentItem = $(
                        `<div class="d-flex align-items-start mb-4">
                           <a href="/accounts/user/${authorSlug}/">
                             <img class="me-3 rounded-circle" src="${authorImage}" alt="user-image" width="40" 
                                  height="40">
                           </a>
                           <div>
                             <a class="fs-5 me-1 link link-dark text-decoration-none"
                                href="/accounts/user/${authorSlug}/">${authorUsername}</a>
                             <span class="text-body-secondary">${commentCreatedDate}</span>
                             <p class="text-break">${commentText}</p>
                           </div>
                         </div>`
                    );
                    commentItem.appendTo(commentsContainer);
                }

                response.next === null
                    ? showMoreCommentsButton.closest('div').remove()
                    : showMoreCommentsButton.dataset.page = (page + 1).toString();

            })
            .catch(error => {
                console.error(error.message);
            });
    });
}


const addCommentForm = document.querySelector('#add-comment-form')

if (addCommentForm) {
    addCommentForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const commentContainer = document.getElementById('comments-container');
        const noCommentsDiv = document.getElementById('no-comments');
        const form = event.target;
        const formData = new FormData(form);
        const recipeId = addCommentForm.dataset.recipeId;
        const comment = formData.get('comment');

        const url = '/api/v1/comments/';
        const method = 'POST';
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        };
        const body = JSON.stringify({'recipe_id': recipeId, 'text': comment})

        fetch(url, {method, headers, body})
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    const error = new Error(response.statusText);
                    error.status = response.status
                    throw error;
                }
            })
            .then(response => {
                form.reset();

                const authorImage = response.author.image
                    ? response.author.image
                    : `${static_url}/img/default_user_image.png`;
                const authorUsername = response.author.username;
                const authorSlug = response.author.slug;
                const commentCreatedDate = moment(response.created_date).fromNow();
                const commentText = response.text;

                const commentItem = $(
                    `<div class="d-flex align-items-start mb-4">
                      <a href="/accounts/user/${authorSlug}/">
                        <img class="me-3 rounded-circle" src="${authorImage}" alt="user-image" width="40" height="40">
                      </a>
                      <div>
                        <a class="fs-5 me-1 link link-dark text-decoration-none" 
                           href="/accounts/user/${authorSlug}/">${authorUsername}</a>
                        <span class="text-body-secondary">${commentCreatedDate}</span>
                        <p class="text-break">${commentText}</p>
                      </div>
                  </div>`
                );

                if (noCommentsDiv) {
                    noCommentsDiv.remove();
                }

                commentItem.prependTo(commentContainer);
            })
            .catch(error => {
                console.error(error.message);
            });
    });
}
