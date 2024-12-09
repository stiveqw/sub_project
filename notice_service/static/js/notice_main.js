document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    const noticesPerPage = 3;
    let allNotices = [];

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
            console.error('Error refreshing CSRF token:', error);
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

    async function loadNotices() {
        try {
            const data = await fetchWithCSRF('/api/notices');
            allNotices = data;
            displayNotices();
            updatePaginationButtons();
        } catch (error) {
            console.error('Error fetching notices:', error);
        }
    }

    function displayNotices() {
        const startIndex = (currentPage - 1) * noticesPerPage;
        const endIndex = startIndex + noticesPerPage;
        const noticesToShow = allNotices.slice(startIndex, endIndex);

        const noticeGrid = document.getElementById('notice-list');
        noticeGrid.innerHTML = '';

        noticesToShow.forEach(notice => {
            const noticeElement = document.createElement('div');
            noticeElement.className = 'notice-item notice-grid-item';
            noticeElement.innerHTML = `
                <img src="/static/images/default.jpg" alt="${notice.title}">
                <h3><a href="/news/${notice.id}">${notice.title}</a></h3>
                <p class="notice-content">${notice.content.substring(0, 100)}...</p>
                <p class="notice-date">${new Date(notice.date).toLocaleDateString()}</p>
            `;
            noticeGrid.appendChild(noticeElement);
        });

        document.getElementById('currentPage').textContent = currentPage;
    }

    function updatePaginationButtons() {
        const prevButton = document.getElementById('prevPage');
        const nextButton = document.getElementById('nextPage');
        const totalPages = Math.ceil(allNotices.length / noticesPerPage);

        prevButton.classList.toggle('disabled', currentPage === 1);
        nextButton.classList.toggle('disabled', currentPage === totalPages);
    }

    document.getElementById('prevPage').addEventListener('click', (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            displayNotices();
            updatePaginationButtons();
        }
    });

    document.getElementById('nextPage').addEventListener('click', (e) => {
        e.preventDefault();
        const totalPages = Math.ceil(allNotices.length / noticesPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            displayNotices();
            updatePaginationButtons();
        }
    });

    loadNotices();

    // 15분마다 CSRF 토큰 갱신
    setInterval(refreshCSRFToken, 15 * 60 * 1000);
});

