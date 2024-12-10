/**
 * Toggles the like status for a given post and updates the UI accordingly.
 */
function toggleLike(pid, currentStatus) {
    var button = event.target;  // Get the clicked button
    var liked = currentStatus;  // Get current like status from data attribute
    liked = !liked;  // Toggle the status

    // Send a POST request to the backend to toggle the like status
    fetch(`/like_post/${pid}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        // Update the button's text and data-liked attribute
        var likeCountText = liked ? `♡ Like (${data.like_count})` : `❤️ Liked (${data.like_count})`;
        button.textContent = likeCountText;

        // Update the color based on the new like status
        button.setAttribute('data-liked', liked.toString());
        if (liked) {
            button.style.color = '#e74c3c';  // Red color for liked posts
        } else {
            button.style.color = '#666';  // Default color for unliked posts
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred while updating the like status.");
    });
}
