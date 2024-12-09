document.addEventListener('DOMContentLoaded', function() {
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function checkAuth() {
        const csrfToken = getCookie('csrf_access_token');
        
        fetch(window.location.href, {
            method: 'GET',
            headers: {
                'X-CSRF-TOKEN': csrfToken
            },
            credentials: 'include'
        })
        .then(response => {
            if (response.status === 401) {
                return response.json();
            } else if (response.status === 400) {
                throw new Error('CSRF token is invalid or missing');
            }
            return null;
        })
        .then(data => {
            if (data && data.error) {
                alert(data.error);
                window.location.href = data.redirect;
            }
        })
        .catch(error => {
            console.error('Auth check error:', error);
            if (error.message === 'CSRF token is invalid or missing') {
                alert('보안 토큰이 유효하지 않습니다. 페이지를 새로고침하거나 다시 로그인해주세요.');
                refreshCSRFToken();
            }
        });
    }

    function refreshCSRFToken() {
        fetch('/refresh-csrf', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.csrf_token) {
                document.cookie = `csrf_access_token=${data.csrf_token}; path=/; SameSite=Strict; Secure`;
            }
        })
        .catch(error => {
            console.error('CSRF token refresh error:', error);
            alert('보안 토큰을 갱신하는 데 실패했습니다. 다시 로그인해주세요.');
            window.location.href = '/login';
        });
    }

    // 15분마다 CSRF 토큰 갱신
    setInterval(refreshCSRFToken, 15 * 60 * 1000);

    checkAuth();
});

