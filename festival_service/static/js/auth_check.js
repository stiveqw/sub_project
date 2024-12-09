document.addEventListener('DOMContentLoaded', function() {
    fetch(window.location.href)
        .then(response => {
            if (response.status === 401) {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.error) {
                alert(data.error);
                window.location.href = data.redirect;
            }
        })
        .catch(error => console.error('Error:', error));
});