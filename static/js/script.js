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
    const bookmarkLink = $(`a[data-recipe-id="${recipeId}"]`);
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
            bookmarkLink.find('img').attr('src', `/static/icon/bookmark${isSaved ? '' : '-fill'}.svg`);
            bookmarkLink.attr('data-is-saved', !isSaved);
            bookmarkLink.find('img')
                .addClass('animate__animated animate__flip')
                .one('animationend', function () {
                    $(this).removeClass('animate__animated animate__flip');
                });

        },
        error: function (xhr, status, error) {
            if (xhr.status === 403) {
                window.location.replace('/accounts/login/')
            } else {
                console.error(error)
            }
        }
    });
});