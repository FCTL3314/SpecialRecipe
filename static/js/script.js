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


$('.bookmark').click(function () {
    const recipeId = $(this).data('recipe-id');
    const bookmarkLink = $(this);
    const bookmarkImg = bookmarkLink.find('img');
    const isSaved = bookmarkLink.attr('data-is-saved') === 'true';

    $.ajax({
        type: isSaved ? 'DELETE' : 'POST',
        url: isSaved ? '/api/v1/bookmarks/remove/' : '/api/v1/bookmarks/add/',
        data: {'recipe_id': recipeId},
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        success: function () {
            const bookmarkText = bookmarkLink.find('span');
            const bookmarkCount = parseInt(bookmarkText.text());
            const newBookmarkCount = isSaved ? bookmarkCount - 1 : bookmarkCount + 1;

            bookmarkText.text(newBookmarkCount + ' Saves');
            bookmarkImg.attr('src', `/static/icon/bookmark${isSaved ? '' : '-fill'}.svg`);
            bookmarkImg.addClass('animate__animated animate__flip').one('animationend', function () {
                $(this).removeClass('animate__animated animate__flip');
            });
            bookmarkLink.attr('data-is-saved', !isSaved);
        },
        error: function (xhr, status, error) {
            if (xhr.status === 403) {
                const currentUrl = window.location.pathname;
                const loginUrl = '/accounts/login/?next=' + currentUrl;
                window.location.replace(loginUrl);
            } else {
                console.error(error);
            }
        }
    });
});

$('#show-more-categories-btn').click(function () {
    const showMoreButton = $(this);
    const page = parseInt(showMoreButton.attr('data-page'));
    const selectedCategorySlug = showMoreButton.attr('data-selected-category-slug');

    $.ajax({
        type: 'GET',
        url: '/api/v1/categories/',
        data: {
            page: page,
        },
        success: function (response) {
            for (const category of response.results) {

                const categoryName = category.name;
                const categorySlug = category.slug;

                const categoryItem = $(
                    `<a class="list-group-item list-group-item-action" href="/recipes/category/${categorySlug}/">${
                        categoryName}</a>`
                );

                if (categorySlug === selectedCategorySlug) {
                    categoryItem.addClass('text-dark bg-body-secondary disabled');
                }
                categoryItem.insertBefore(showMoreButton);
            }

            response.next === null
                ? showMoreButton.remove()
                : showMoreButton.attr('data-page', page + 1);
        },
        error: function (xhr, status, error) {
            console.error(error);
        }
    });
});

$('#show-more-comments-btn').click(function () {
    const commentsContainer = $('#comments-container');
    const showMoreButton = $(this);
    const page = parseInt(showMoreButton.attr('data-page'));
    const recipeId = parseInt(showMoreButton.attr('data-recipe-id'));

    $.ajax({
        type: 'GET',
        url: '/api/v1/comments/',
        data: {
            page: page,
            recipe_id: recipeId,
        },
        success: function (response) {
            for (const comment of response.results) {

                const authorImage = comment.author.image ? comment.author.image : '/static/img/default_user_image.png';
                const authorUsername = comment.author.username;
                const authorSlug = comment.author.slug;
                const commentCreatedDate = moment(comment.created_date).fromNow();
                const commentText = comment.text;

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
                commentItem.appendTo(commentsContainer);
            }

            response.next === null
                ? showMoreButton.closest('div').remove()
                : showMoreButton.attr('data-page', page + 1);

        },
        error: function (xhr, status, error) {
            console.error(error);
        }
    });
});


$(`#add-comment-form`).on('submit', function (event) {
    event.preventDefault();

    const commentContainer = document.getElementById('comments-container');
    const noCommentsDiv = document.getElementById('no-comments');
    const form = event.target;
    const formData = new FormData(form);
    const recipeId = $(this).attr('data-recipe-id');
    const comment = formData.get('comment');

    $.ajax({
        type: 'POST',
        url: '/api/v1/comments/',
        data: {
            'recipe_id': recipeId,
            'text': comment,
            'X-CSRFToken': getCookie('csrftoken'),
        },
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        success: function (response) {
            form.reset();

            const authorImage = response.author.image ? response.author.image : '/static/img/default_user_image.png';
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
        },
        error: function (xhr, status, error) {
            console.error(error);
        }
    });
});
