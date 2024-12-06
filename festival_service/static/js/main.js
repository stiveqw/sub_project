document.addEventListener('DOMContentLoaded', function() {
    const festivalsPerPage = 3;
    let currentPage = 1;
    let allFestivals = festivalsData;

    function displayFestivals() {
        const startIndex = (currentPage - 1) * festivalsPerPage;
        const endIndex = startIndex + festivalsPerPage;
        const festivalsToShow = allFestivals.slice(startIndex, endIndex);

        const festivalGrid = document.getElementById('festival-list');
        festivalGrid.innerHTML = '';

        festivalsToShow.forEach(festival => {
            const festivalElement = document.createElement('div');
            festivalElement.className = 'festival-grid-item';
            const isReserved = reservedFestivalKeys.includes(festival.festival_key);
            festivalElement.innerHTML = `
                <img src="/static/images/default.jpg" alt="${festival.title}">
                <h3>${festival.title}</h3>
                <p>날짜: ${new Date(festival.date).toLocaleDateString()}</p>
                <p>좌석현황: ${festival.reserved_seats}/${festival.total_seats}</p>  
                ${isReserved 
                    ? `<button class="apply-button reserved" disabled>이미 예약한 축제입니다</button>`
                    : `<a href="/apply/${festival.festival_key}" class="apply-button">지금 신청하기</a>`
                }
            `;
            festivalGrid.appendChild(festivalElement);
        });
    }

    function setupPagination() {
        const totalPages = Math.ceil(allFestivals.length / festivalsPerPage);
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';

        if (currentPage > 1) {
            pagination.innerHTML += `<a href="#" class="pagination-link" onclick="changePage(${currentPage - 1})">&lt;</a>`;
        }

        for (let i = 1; i <= totalPages; i++) {
            pagination.innerHTML += `<a href="#" class="pagination-link ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</a>`;
        }

        if (currentPage < totalPages) {
            pagination.innerHTML += `<a href="#" class="pagination-link" onclick="changePage(${currentPage + 1})">&gt;</a>`;
        }
    }

    function changePage(page) {
        currentPage = page;
        displayFestivals();
        setupPagination();
    }

    // 전역 스코프에 changePage 함수 추가
    window.changePage = changePage;

    displayFestivals();
    setupPagination();
});

