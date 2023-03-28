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
                console.log(window.location.pathname)
                const currentUrl = window.location.pathname;
                const loginUrl = '/accounts/login/?next=' + currentUrl;
                window.location.replace(loginUrl)
            } else {
                console.error(error)
            }
        }
    });
});