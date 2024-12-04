document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    const noticesPerPage = 3;
    let allNotices = [];

    function loadNotices() {
        fetch('/api/notices')
            .then(response => response.json())
            .then(notices => {
                allNotices = notices;
                displayNotices();
                updatePaginationButtons();
            })
            .catch(error => {
                console.error('Error fetching notices:', error);
            });
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
});

