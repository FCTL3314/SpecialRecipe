import {
    getCookie,
    createLoadingSpinner,
    createLoadingSpinnerWrp,
    createListGroupItem,
    createCategoryItem,
    createCommentItem,
    static_url,
} from './utils.js';


const bookmarkButtons = document.querySelectorAll('.bookmark');

if (bookmarkButtons) {
    bookmarkButtons.forEach(bookmarkBtn => {
        bookmarkBtn.addEventListener('click', () => {
            bookmarkActions(bookmarkBtn);
        });
    });
}

const showMoreCategoriesButton = document.querySelector('#show-more-categories-btn');

if (showMoreCategoriesButton) {
    showMoreCategoriesButton.addEventListener('click', showMoreCategories);
}


const showMoreCommentsButton = document.querySelector('#show-more-comments-btn');

if (showMoreCommentsButton) {
    showMoreCommentsButton.addEventListener('click', showMoreComments);
}


const addCommentForm = document.querySelector('#add-comment-form');

if (addCommentForm) {
    addCommentForm.addEventListener('submit', event => {
        addComment(event);
    });
}


function bookmarkActions(bookmarkBtn) {
    const [bookmarkImg, bookmarkText] = bookmarkBtn.querySelectorAll('img, span');

    const recipeId = bookmarkBtn.dataset.recipeId;
    const isSaved = bookmarkBtn.dataset.isSaved === 'true';
    const bookmarkCount = parseInt(bookmarkText.textContent);

    const url = isSaved ? `/api/v1/bookmarks/${recipeId}/` : '/api/v1/bookmarks/';
    const csrfToken = getCookie('csrftoken');
    const requestOptions = {
        'method': isSaved ? 'DELETE' : 'POST',
        'headers': {
            'Content-Type': 'application/json', 'X-CSRFToken': csrfToken,
        },
    }

    if (!isSaved) {
        requestOptions.body = JSON.stringify({'recipe_id': recipeId});
    }

    const loadingSpinner = createLoadingSpinner(true);
    bookmarkBtn.disabled = true;
    bookmarkBtn.append(loadingSpinner);

    fetch(url, requestOptions)
        .then(response => {
            if (response.ok) {
                return response
            } else if (response.status === 403) {
                const error = new Error(response.statusText);
                error.status = 403;
                throw error;
            } else {
                const error = new Error(response.statusText);
                error.status = response.status;
                throw error;
            }
        })
        .then(() => {
            loadingSpinner.remove();
            bookmarkBtn.disabled = false;

            bookmarkText.textContent = `${isSaved ? bookmarkCount - 1 : bookmarkCount + 1} Saves`;
            bookmarkImg.src = `${static_url}icon/bookmark${isSaved ? '' : '-fill'}.svg`;
            bookmarkImg.classList.add('animate__animated', 'animate__flip');
            bookmarkImg.addEventListener('animationend', function () {
                this.classList.remove('animate__animated', 'animate__flip');
            });
            bookmarkBtn.dataset.isSaved = (!isSaved).toString();
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
}


function showMoreCategories() {
    const page = parseInt(showMoreCategoriesButton.dataset.page);
    const selectedCategorySlug = showMoreCategoriesButton.dataset.selectedCategorySlug;

    const loadingSpinner = createLoadingSpinner(true, 'primary');
    const listGroupItem = createListGroupItem(false, true);
    showMoreCategoriesButton.classList.add('d-none');
    listGroupItem.append(loadingSpinner);
    showMoreCategoriesButton.insertAdjacentElement('afterend', listGroupItem);

    const url = `/api/v1/categories/?page=${page}`;
    const requestOptions = {
        'method': 'GET',
        'headers': {
            'Content-Type': 'application/json',
        },
    }

    fetch(url, requestOptions)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                const error = new Error(response.statusText);
                error.status = response.status;
                throw error;
            }
        })
        .then(jsonResponse => {
            listGroupItem.remove();
            showMoreCategoriesButton.classList.remove('d-none');

            for (const category of jsonResponse.results) {
                const categoryItem = createCategoryItem(category, true);

                if (category.slug === selectedCategorySlug) {
                    categoryItem.classList.add('text-dark', 'bg-body-secondary', 'disabled');
                }

                showMoreCategoriesButton.insertAdjacentElement('beforebegin', categoryItem);
            }

            if (jsonResponse.next === null) {
                showMoreCategoriesButton.remove();
            } else {
                showMoreCategoriesButton.dataset.page = (page + 1).toString();
            }
        })
        .catch(error => {
            console.error(error.message);
        });
}


function showMoreComments() {
    const commentsWrp = document.getElementById('comments-wrp');

    const page = parseInt(showMoreCommentsButton.dataset.page);
    const recipeId = parseInt(showMoreCommentsButton.dataset.recipeId);

    const loadingSpinnerWrp = createLoadingSpinnerWrp(true);
    const loadingSpinner = createLoadingSpinner(false, 'primary');
    showMoreCommentsButton.classList.add('d-none');
    loadingSpinnerWrp.append(loadingSpinner);
    commentsWrp.insertAdjacentElement('afterend', loadingSpinnerWrp);

    const url = `/api/v1/comments/?page=${page}&recipe_id=${recipeId}`;
    const requestOptions = {
        'method': 'GET',
        'headers': {
            'Content-Type': 'application/json',
        },
    }

    fetch(url, requestOptions)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                const error = new Error(response.statusText);
                error.status = response.status;
                throw error;
            }
        })
        .then(jsonResponse => {
            for (const comment of jsonResponse.results) {
                loadingSpinnerWrp.remove();
                showMoreCommentsButton.classList.remove('d-none');

                const commentItem = createCommentItem(comment);
                commentsWrp.append(commentItem);
            }

            if (jsonResponse.next === null) {
                showMoreCommentsButton.closest('div').remove();
            } else {
                showMoreCommentsButton.dataset.page = (page + 1).toString();
            }
        })
        .catch(error => {
            console.error(error.message);
        });
}


function addComment(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const text = formData.get('text');
    const recipeId = addCommentForm.dataset.recipeId;

    const commentsWrp = document.getElementById('comments-wrp');
    const noCommentsDiv = document.getElementById('no-comments');

    const url = '/api/v1/comments/';
    const csrfToken = getCookie('csrftoken')
    const requestOptions = {
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json', 'X-CSRFToken': csrfToken,
        },
        'body': JSON.stringify({'recipe_id': recipeId, 'text': text}),
    }

    fetch(url, requestOptions)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                const error = new Error(response.statusText);
                error.status = response.status;
                throw error;
            }
        })
        .then(jsonResponse => {
            form.reset();

            const commentItem = createCommentItem(jsonResponse)

            if (noCommentsDiv) {
                noCommentsDiv.remove();
            }

            commentsWrp.prepend(commentItem);
        })
        .catch(error => {
            console.error(error.message);
        });
}
