document.addEventListener('DOMContentLoaded', function() {
    console.log('Main service JavaScript loaded');

    const festivalItems = document.getElementById('festivalItems');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const pageIndicator = document.getElementById('pageIndicator');

    const festivalImages = [
        'autumn-festival.jfif',
        'canoe-festival.jfif',
        'culture-festival.jfif',
        'festival-schedule.jfif',
        'music-festival.jfif',
        'sports-festival.jfif',
        'spring-festival.jfif',
        'summer-festival.jfif',
        'winter-festival.jfif'
    ];

    let festivals = [];
    let currentPage = 1;
    const itemsPerPage = 3;

    function fetchFestivals() {
        fetch('/festival/festivals')
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    festivals = data.festivals;
                    displayFestivals();
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (festivalItems) {
                    festivalItems.innerHTML = `<p class="col-12">축제 정보를 불러오는 중 오류가 발생했습니다: ${error.message}</p>`;
                } else {
                    console.error('Festival items container not found');
                }
            });
    }

    function displayFestivals() {
        if (!festivalItems) {
            console.error('Festival items container not found');
            return;
        }

        const totalPages = Math.ceil(festivals.length / itemsPerPage);
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageItems = festivals.slice(startIndex, endIndex);

        festivalItems.innerHTML = '';
        if (pageItems.length === 0) {
            festivalItems.innerHTML = '<p>현재 사용 가능한 축제가 없습니다.</p>';
            return;
        }

        pageItems.forEach((festival, index) => {
            const item = document.createElement('div');
            item.className = 'festival-item';
            const imageIndex = (startIndex + index) % festivalImages.length;
            item.innerHTML = `
                <img src="/static/images/${festivalImages[imageIndex]}" alt="${festival.title}">
                <div class="festival-item-content">
                    <h3>${festival.title}</h3>
                    <p>날짜: ${new Date(festival.date).toLocaleDateString()}</p>
                    <p>좌석현황: ${festival.capacity}/${festival.total_seats}</p>
                    <a href="http://localhost:5002/festival/apply/${festival.festival_key}?image=${encodeURIComponent(festivalImages[imageIndex])}"" class="btn btn-primary">지금 신청하기</a>
                </div>
            `;
            festivalItems.appendChild(item);
        });

        updatePageIndicator(totalPages);
    }

    function updatePageIndicator(totalPages) {
        if (!pageIndicator) {
            console.error('Page indicator not found');
            return;
        }
        pageIndicator.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
            const dot = document.createElement('div');
            dot.className = `page-dot ${i === currentPage ? 'active' : ''}`;
            pageIndicator.appendChild(dot);
        }
    }

    function nextPage() {
        const totalPages = Math.ceil(festivals.length / itemsPerPage);
        currentPage = currentPage === totalPages ? 1 : currentPage + 1;
        displayFestivals();
    }

    function prevPage() {
        const totalPages = Math.ceil(festivals.length / itemsPerPage);
        currentPage = currentPage === 1 ? totalPages : currentPage - 1;
        displayFestivals();
    }

    if (festivalItems && prevButton && nextButton && pageIndicator) {
        fetchFestivals();

        prevButton.addEventListener('click', prevPage);
        nextButton.addEventListener('click', nextPage);

        prevButton.addEventListener('mousedown', (e) => e.preventDefault());
        nextButton.addEventListener('mousedown', (e) => e.preventDefault());
    } else {
        console.error('One or more required elements are missing');
        if (!festivalItems) console.error('festivalItems not found');
        if (!prevButton) console.error('prevButton not found');
        if (!nextButton) console.error('nextButton not found');
        if (!pageIndicator) console.error('pageIndicator not found');
    }
});

