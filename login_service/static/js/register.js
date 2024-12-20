document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(registerForm);
        
        fetch('/register', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        })
        .then(response => 
            response.json().catch(() => response.text())
        )
        .then(data => {
            if (typeof data === 'object') {
                // JSON 응답 처리
                handleJsonResponse(data);
            } else {
                // HTML 응답 처리
                document.body.innerHTML = data;
                const errorElement = document.querySelector('.error-message');
                if (errorElement) {
                    alert(errorElement.textContent);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
});

function handleJsonResponse(data) {
    if (data.success) {
        alert(data.message);
        window.location.href = '/login';
    } else {
        alert(data.message);
        window.location.href = '/register';
    }
}