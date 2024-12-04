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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('로그인 성공!');
                window.location.href = 'http://localhost:5003';  // main_service로 리다이렉트
            } else {
                alert(data.message);
                loginForm.reset();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
        });
    });
});

