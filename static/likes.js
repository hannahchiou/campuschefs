function toggleLike(pid) {
    var button = event.target;  // Get the clicked button
    var currentStatus = button.getAttribute("data-liked"); // Get the current like status
    var liked = (currentStatus === 'true');  // Determine current like status
    liked = !liked;  // Toggle the status

    // Update the button text based on the new like status
    var likeCount = parseInt(button.textContent.match(/\d+/)[0]);  // Extract current like count
    likeCount = liked ? likeCount + 1 : likeCount - 1;  // Increment or decrement the like count

    // Update the like button text
    button.textContent = liked ? `❤️ Liked (${likeCount})` : `♡ Like (${likeCount})`;
    button.setAttribute("data-liked", liked.toString());  // Update the data-liked attribute

    // Send the like/unlike request to the server
    fetch(`/like_post/${pid}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token() }}'  // Include CSRF token if needed
        },
        body: JSON.stringify({ liked: liked })
    }).then(response => {
        if (response.ok) {
            console.log('Like status updated');
        } else {
            console.log('Failed to update like status');
        }
    });
}