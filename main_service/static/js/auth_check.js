document.addEventListener('DOMContentLoaded', function() {
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function checkAuth() {
        fetch(window.location.href, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getCookie('access_token_cookie')}`
            },
            credentials: 'include'
        })
        .then(response => {
            if (response.status === 401) {
                throw new Error('Unauthorized');
            } else if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return null;
        })
        .then(data => {
            if (data && data.error) {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Auth check error:', error);
            window.location.href = '/auth_required.html';
        });
    }

    // 주기적으로 인증 확인 (1분마다)
    setInterval(checkAuth, 60 * 1000);

    // 초기 인증 확인
    checkAuth();
});

