document.addEventListener('DOMContentLoaded', function() {
    // 여기에 필요한 다른 JavaScript 코드를 추가할 수 있습니다.
    console.log('Main service JavaScript loaded');

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function setCookie(name, value, options = {}) {
        options = {
            path: '/',
            ...options
        };
        if (options.expires instanceof Date) {
            options.expires = options.expires.toUTCString();
        }
        let updatedCookie = encodeURIComponent(name) + "=" + encodeURIComponent(value);
        for (let optionKey in options) {
            updatedCookie += "; " + optionKey;
            let optionValue = options[optionKey];
            if (optionValue !== true) {
                updatedCookie += "=" + optionValue;
            }
        }
        document.cookie = updatedCookie;
    }

    async function refreshCSRFToken() {
        try {
            const response = await fetch('/refresh-csrf', {
                method: 'GET',
                credentials: 'include'
            });
            const data = await response.json();
            if (data.csrf_token) {
                setCookie('csrf_access_token', data.csrf_token, { secure: true, sameSite: 'Strict' });
                return data.csrf_token;
            }
        } catch (error) {
            console.error('CSRF token refresh error:', error);
            alert('보안 토큰을 갱신하는 데 실패했습니다. 다시 로그인해주세요.');
            window.location.href = '/login';
        }
    }

    async function handleCSRFError() {
        const newToken = await refreshCSRFToken();
        if (newToken) {
            return newToken;
        } else {
            throw new Error('Failed to refresh CSRF token');
        }
    }

    async function fetchWithCSRF(url, options = {}) {
        const csrfToken = getCookie('csrf_access_token');
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'X-CSRF-TOKEN': csrfToken,
                'Content-Type': 'application/json'
            }
        };
        const mergedOptions = { ...defaultOptions, ...options };
        if (mergedOptions.body && typeof mergedOptions.body !== 'string') {
            mergedOptions.body = JSON.stringify(mergedOptions.body);
        }
        try {
            const response = await fetch(url, mergedOptions);
            if (!response.ok) {
                if (response.status === 400 && response.headers.get('X-CSRF-TOKEN-INVALID')) {
                    const newToken = await handleCSRFError();
                    mergedOptions.headers['X-CSRF-TOKEN'] = newToken;
                    return fetchWithCSRF(url, mergedOptions);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            if (error.message.includes('401')) {
                window.location.href = '/login';
            }
            throw error;
        }
    }

    // 로그아웃 버튼 이벤트 리스너
    const logoutButton = document.getElementById('logoutBtn');
    if (logoutButton) {
        logoutButton.addEventListener('click', async function(e) {
            e.preventDefault();
            try {
                const response = await fetchWithJWT(this.href, { method: 'POST' });
                if (response.success) {
                    window.location.href = response.redirect_url;
                } else {
                    console.error('Logout failed:', response.message);
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
});

   
    

