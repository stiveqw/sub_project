function removeWhitespace(input) {
    input.value = input.value.replace(/\s/g, '');
}

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const studentIdInput = document.querySelector('input[name="student_id"]');
    const departmentInput = document.querySelector('input[name="department"]');
    const nameInput = document.querySelector('input[name="name"]');
    const emailInput = document.querySelector('input[name="email"]');
    const phoneInput = document.querySelector('input[name="phone_number"]');
    const passwordInput = document.querySelector('input[name="password"]');

    // 학번 입력 제한
    studentIdInput.addEventListener('input', function(e) {
        if (e.target.value.length > 15) {
            e.target.value = e.target.value.slice(0, 15);
        }
        removeWhitespace(e.target);
    });

    // 학과와 이름 입력 제한 (문자만)
    [departmentInput, nameInput].forEach(input => {
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^가-힣a-zA-Z]/g, '');
            removeWhitespace(e.target);
        });
    });

    // 이메일 입력 제한 (공백 제거)
    emailInput.addEventListener('input', function(e) {
        removeWhitespace(e.target);
    });

    // 전화번호 형식 지정
    phoneInput.addEventListener('input', function(e) {
        let number = e.target.value.replace(/[^0-9]/g, '');
        if (number.length > 11) {
            number = number.slice(0, 11);
        }
        if (number.length > 3 && number.length <= 7) {
            number = number.slice(0, 3) + '-' + number.slice(3);
        } else if (number.length > 7) {
            number = number.slice(0, 3) + '-' + number.slice(3, 7) + '-' + number.slice(7);
        }
        e.target.value = number;
        removeWhitespace(e.target);
    });

    // 비밀번호 입력 제한
    passwordInput.addEventListener('input', function(e) {
        if (e.target.value.length > 20) {
            e.target.value = e.target.value.slice(0, 20);
        }
        removeWhitespace(e.target);
    });

    // 이메일 형식 검사
    function validateEmail(email) {
        const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        return re.test(String(email).toLowerCase());
    }

    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // 이메일 유효성 검사
        if (!validateEmail(emailInput.value)) {
            alert('유효한 이메일 주소를 입력해주세요.');
            return;
        }

        const formData = new FormData(registerForm);
        
        fetch('/register', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = '/login';
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
});

