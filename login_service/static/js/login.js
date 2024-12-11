document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(loginForm);
        
        fetch('/login', {
            method: 'POST',
            body: formData,
            credentials: 'include'  // 쿠키를 포함하기 위해 추가
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Login failed');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('로그인 성공!');
                window.location.href = data.redirect_url;
            } else {
                alert(data.message || '로그인에 실패했습니다.');
                loginForm.reset();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || '로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
        });
    });
});

