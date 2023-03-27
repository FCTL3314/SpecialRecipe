$('.bookmark').click(function () {
    const recipeId = $(this).data('recipe-id');
    const bookmarkLink = $(`a[data-recipe-id="${recipeId}"]`);
    const isSaved = bookmarkLink.attr('data-is-saved') === 'true';

    $.ajax({
        type: isSaved ? 'DELETE' : 'POST',
        url: isSaved ? '/api/v1/saves/remove/' : '/api/v1/saves/add/',
        data: {'recipe_id': recipeId},
        headers: {'Authorization': 'Token ' + 'e7cd400e29855d7a6163eaec7739a11fd1d8dc19'},
        success: function () {
            const bookmarkText = bookmarkLink.find('span');
            const bookmarkCount = parseInt(bookmarkText.text());
            const newBookmarkCount = isSaved ? bookmarkCount - 1 : bookmarkCount + 1;

            bookmarkText.text(newBookmarkCount + " Saves");
            bookmarkLink.find('img').attr('src', `/static/icon/bookmark${isSaved ? '' : '-fill'}.svg`);
            bookmarkLink.attr('data-is-saved', !isSaved);
        },
        error: function (response) {
            console.error(response)
        }
    });
});