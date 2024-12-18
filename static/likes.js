function likePost(postId) {
    const button = document.getElementById(`like-button-${postId}`);
    const buttonContainer = document.getElementById(`like-button-container-${postId}`);
    const uid = buttonContainer.dataset.uid; // Get the correct UID for the post

    // Add the "liked" class to the button to indicate it has been liked
    button.classList.add('liked');

    fetch(`/like/${postId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid: uid }) // Ensure UID is sent in the body
    })
    .then(response => response.json())
    .then(data => {
        if (!data.error) {
            // Update the like count on the page after the POST request
            const likeCountElement = document.getElementById(`like-count-${postId}`);
            if (likeCountElement) {
                likeCountElement.textContent = data.like_count;
            }
        } else {
            console.error(data.message || 'An error occurred');
        }
    })
    .catch(error => console.error('Error:', error));
}
