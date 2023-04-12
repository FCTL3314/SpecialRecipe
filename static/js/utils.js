const static_url = '/static/';


function getCookie(name) {
    let cookieValue;
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


function createLoadingSpinner(small = false, textColor) {
    const loadingSpinner = document.createElement('span');
    loadingSpinner.className = 'spinner-border';

    if (small) {
        loadingSpinner.classList.add('spinner-border-sm');
    }
    if (textColor) {
        loadingSpinner.classList.add(`text-${textColor}`);
    }

    loadingSpinner.setAttribute('role', 'status');

    const span = document.createElement('span');
    span.classList.add('visually-hidden');
    span.textContent = 'Loading...';
    loadingSpinner.append(span);

    return loadingSpinner;
}


function createLoadingSpinnerWrp(centered = false) {
    const loadingSpinnerWrp = document.createElement('div');
    loadingSpinnerWrp.classList.add('d-flex');

    if (centered) {
        loadingSpinnerWrp.classList.add('justify-content-center');
    }

    return loadingSpinnerWrp;
}


function createListGroupItem(action = false, centered = false) {
    const listGroupItem = document.createElement('li');
    listGroupItem.classList.add('list-group-item');

    if (action) {
        listGroupItem.classList.add('list-group-item-action');
    }
    if (centered) {
        listGroupItem.classList.add('text-center');
    }

    return listGroupItem;
}


function createCategoryItem(category, action = true) {
    const categoryItem = document.createElement('a');
    categoryItem.classList.add('list-group-item');
    if (action) {
        categoryItem.classList.add('list-group-item-action');
    }
    categoryItem.href = `/category/${category.slug}/`;
    categoryItem.text = category.name;

    return categoryItem;
}


function createCommentItem(comment) {
    const authorImageUrl = comment.author.image ? comment.author.image : `${static_url}img/default_user_image.png`;
    const authorUsername = comment.author.username;
    const authorSlug = comment.author.slug;
    const commentCreationDate = moment(comment.created_date).fromNow();
    const commentText = comment.text;

    const commentItem = document.createElement('div');
    commentItem.classList.add('d-flex', 'align-items-start', 'mb-4');

    const authorImageLink = document.createElement('a');
    authorImageLink.href = `/accounts/user/${authorSlug}/`;

    const authorImage = document.createElement('img');
    authorImage.classList.add('me-3', 'rounded-circle');
    authorImage.src = authorImageUrl;
    authorImage.alt = 'author-image';
    authorImage.width = 40;
    authorImage.height = 40;

    authorImageLink.append(authorImage);

    const textWrp = document.createElement('div');

    const authorLink = document.createElement('a');
    authorLink.classList.add('fs-5', 'me-1', 'link', 'link-dark', 'text-decoration-none')
    authorLink.href = `/accounts/user/${authorSlug}/`;
    authorLink.textContent = authorUsername

    const creationDateText = document.createElement('span')
    creationDateText.classList.add('text-body-secondary')
    creationDateText.textContent = commentCreationDate

    const text = document.createElement('p')
    text.classList.add('text-break')
    text.textContent = commentText

    textWrp.append(authorLink);
    textWrp.append(creationDateText);
    textWrp.append(text)

    commentItem.append(authorImageLink);
    commentItem.append(textWrp);

    return commentItem
}


export {
    getCookie,
    createLoadingSpinner,
    createLoadingSpinnerWrp,
    createListGroupItem,
    createCategoryItem,
    createCommentItem,
    static_url,
};
