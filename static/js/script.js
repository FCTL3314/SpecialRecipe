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
        url: isSaved ? '/api/v1/saves/remove/' : '/api/v1/saves/add/',
        data: {'recipe_id': recipeId},
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        success: function () {
            const bookmarkText = bookmarkLink.find('span');
            const bookmarkCount = parseInt(bookmarkText.text());
            const newBookmarkCount = isSaved ? bookmarkCount - 1 : bookmarkCount + 1;

            bookmarkText.text(newBookmarkCount + " Saves");
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
                window.location.replace(loginUrl)
            } else {
                console.error(error)
            }
        }
    });
});

$('#show-more-btn').click(function () {
    const loadMoreButton = $(this);
    const page = parseInt(loadMoreButton.attr('data-page'));
    const categorySlug = loadMoreButton.attr('data-selected-category-slug');

    $.ajax({
        type: 'GET',
        url: `/api/v1/categories/`,
        data: {
            page: page
        },
        success: function (response) {
            console.log(categorySlug)
            for (const category of response.results) {
                const categoryItem = $(`<a class="list-group-item list-group-item-action" href="/recipes/category/${
                    category.slug}/">${category.name}</a>`);
                if (category.slug === categorySlug) {
                    categoryItem.addClass("text-dark bg-body-secondary disabled");
                }
                categoryItem.insertBefore(loadMoreButton)
            }
            if (response.next === null) {
                loadMoreButton.remove()
            } else {
                loadMoreButton.attr('data-page', page + 1)
            }
        },
        error: function (xhr, status, error) {
            console.error(error)
        }
    });
});