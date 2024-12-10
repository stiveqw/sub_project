function removeWhitespace(input) {
    input.value = input.value.replace(/\s/g, '');
}

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const studentIdInput = document.querySelector('input[name="student_id"]');
    const passwordInput = document.querySelector('input[name="password"]');
    
    // 학번 입력 제한
    studentIdInput.addEventListener('input', function(e) {
        if (e.target.value.length > 15) {
            e.target.value = e.target.value.slice(0, 15);
        }
        removeWhitespace(e.target);
    });

    // 비밀번호 입력 제한
    passwordInput.addEventListener('input', function(e) {
        if (e.target.value.length > 20) {
            e.target.value = e.target.value.slice(0, 20);
        }
        removeWhitespace(e.target);
    });
    
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
                alert(data.message || '학번 또는 비밀번호가 잘못되었습니다.');
                loginForm.reset();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error.message || '로그인 중 오류가 발생했습니다. 다시 시도해주세요.');
        });
    });
});

