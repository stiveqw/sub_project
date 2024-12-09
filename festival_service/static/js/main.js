let allFestivals, allCancelFestivals;

document.addEventListener('DOMContentLoaded', function() {
    allFestivals = typeof festivalsData !== 'undefined' ? festivalsData : [];
    allCancelFestivals = typeof userReservedFestivals !== 'undefined' ? userReservedFestivals : [];

    const festivalsPerPage = 3;
    let currentPage = 1;
    let currentCancelPage = 1;
    

    console.log("Total festivals in JavaScript:", allFestivals.length);
    console.log("Total cancel festivals in JavaScript:", allCancelFestivals.length);

    function showLoading(id) {
        const loadingElement = document.getElementById(id);
        const listElement = document.getElementById(id.replace('-loading-indicator', '-list'));
        if (loadingElement) loadingElement.style.display = 'flex';
        if (listElement) listElement.style.display = 'none';
    }

    function hideLoading(id) {
        const loadingElement = document.getElementById(id);
        const listElement = document.getElementById(id.replace('-loading-indicator', '-list'));
        if (loadingElement) loadingElement.style.display = 'none';
        if (listElement) listElement.style.display = 'grid';
    }

    function displayFestivals() {
        showLoading('festival-loading-indicator');
        const startIndex = (currentPage - 1) * festivalsPerPage;
        const endIndex = startIndex + festivalsPerPage;
        const festivalsToShow = allFestivals.slice(startIndex, endIndex);

        console.log("Displaying festivals:", startIndex, "to", endIndex);

        const festivalGrid = document.getElementById('festival-list');
        if (!festivalGrid) {
            console.error("Festival list element not found");
            return;
        }
        festivalGrid.innerHTML = '';

        festivalsToShow.forEach(festival => {
            const festivalElement = document.createElement('div');
            festivalElement.className = 'festival-grid-item';
            const isReserved = festival.is_reserved;
            const isFull = festival.is_full;
            festivalElement.innerHTML = `
                <img src="/static/images/default.jpg" alt="${festival.title}">
                <h3>${festival.title}</h3>
                <p>날짜: ${new Date(festival.date).toLocaleDateString()}</p>
                <p>좌석현황: ${festival.capacity}/${festival.total_seats}</p>  
                ${isReserved 
                    ? `<button class="apply-button reserved" disabled>이미 예약한 축제입니다</button>`
                    : isFull
                        ? `<button class="apply-button full" disabled>신청 마감</button>`
                        : `<a href="/apply/${festival.festival_key}" class="apply-button">지금 신청하기</a>`
                }
            `;
            festivalGrid.appendChild(festivalElement);
        });

        setupPagination('festival-pagination', allFestivals.length, currentPage, changePage);
        hideLoading('festival-loading-indicator');
    }

    function displayCancelFestivals() {
        showLoading('cancel-loading-indicator');
        const startIndex = (currentCancelPage - 1) * festivalsPerPage;
        const endIndex = startIndex + festivalsPerPage;
        const festivalsToShow = allCancelFestivals.slice(startIndex, endIndex);

        console.log("Displaying cancel festivals:", startIndex, "to", endIndex);

        const festivalGrid = document.getElementById('cancel-festival-list');
        if (!festivalGrid) {
            console.error("Cancel festival list element not found");
            return;
        }
        festivalGrid.innerHTML = '';

        festivalsToShow.forEach(festival => {
            const festivalElement = document.createElement('div');
            festivalElement.className = 'festival-grid-item';
            festivalElement.innerHTML = `
                <img src="/static/images/default.jpg" alt="${festival.title}">
                <h3>${festival.title}</h3>
                <p>좌석 번호: ${festival.seat_number}</p>
                <p>예약 시간: ${new Date(festival.reservation_time).toLocaleString()}</p>
                <p>상태: 예약됨</p>
                <button class="cancel-button" data-reservation-id="${festival.id}">예약 취소</button>
            `;
            festivalGrid.appendChild(festivalElement);
        });

        setupPagination('cancel-pagination', allCancelFestivals.length, currentCancelPage, changeCancelPage);
        hideLoading('cancel-loading-indicator');
    }

    function setupPagination(paginationId, totalItems, currentPageNum, changePageFunc) {
        const totalPages = Math.ceil(totalItems / festivalsPerPage);
        console.log(`Total ${paginationId} pages:`, totalPages);

        const pagination = document.getElementById(paginationId);
        if (!pagination) {
            console.error(`Pagination element with id ${paginationId} not found`);
            return;
        }
        pagination.innerHTML = '';

        if (currentPageNum > 1) {
            pagination.innerHTML += `<a href="#" class="pagination-link" data-page="${currentPageNum - 1}">&lt;</a>`;
        }

        const maxVisiblePages = 6;
        let startPage = Math.max(1, currentPageNum - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        if (startPage > 1) {
            pagination.innerHTML += `<a href="#" class="pagination-link" data-page="1">1</a>`;
            if (startPage > 2) {
                pagination.innerHTML += `<span class="pagination-ellipsis">...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            pagination.innerHTML += `<a href="#" class="pagination-link ${i === currentPageNum ? 'active' : ''}" data-page="${i}">${i}</a>`;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                pagination.innerHTML += `<span class="pagination-ellipsis">...</span>`;
            }
            pagination.innerHTML += `<a href="#" class="pagination-link" data-page="${totalPages}">${totalPages}</a>`;
        }

        if (currentPageNum < totalPages) {
            pagination.innerHTML += `<a href="#" class="pagination-link" data-page="${currentPageNum + 1}">&gt;</a>`;
        }

        // 페이지네이션 링크에 이벤트 리스너 추가
        pagination.addEventListener('click', function(e) {
            e.preventDefault();
            if (e.target.classList.contains('pagination-link')) {
                const page = parseInt(e.target.getAttribute('data-page'));
                changePageFunc(page);
            }
        });
    }

    function changePage(page) {
        currentPage = page;
        console.log("Changing to page:", page);
        showLoading('festival-loading-indicator');
        setTimeout(() => {
            displayFestivals();
        }, 300);
    }

    function changeCancelPage(page) {
        currentCancelPage = page;
        console.log("Changing cancel page to:", page);
        showLoading('cancel-loading-indicator');
        setTimeout(() => {
            displayCancelFestivals();
        }, 300);
    }

    function refreshFestivals() {
        showLoading('festival-loading-indicator');
        showLoading('cancel-loading-indicator');
        
        fetch('/api/festivals', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                allFestivals = data.festivals;
                allCancelFestivals = data.festivals.filter(f => f.is_reserved); // Update: Changed allCancelFestivals assignment
                displayFestivals();
                displayCancelFestivals();
            } else {
                throw new Error(data.message || '축제 목록을 새로고침하는데 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error refreshing festivals:', error);
            alert('축제 목록을 새로고침하는데 실패했습니다: ' + error.message);
        })
        .finally(() => {
            hideLoading('festival-loading-indicator');
            hideLoading('cancel-loading-indicator');
        });
    }

    displayFestivals();
    displayCancelFestivals();

    // 예약 취소 기능 추가
    const cancelFestivalList = document.getElementById('cancel-festival-list');
    if (cancelFestivalList) {
        cancelFestivalList.addEventListener('click', function(e) {
            if (e.target.classList.contains('cancel-button')) {
                const reservationId = e.target.getAttribute('data-reservation-id');
                if (confirm('정말로 이 축제 예약을 취소하시겠습니까?')) {
                    cancelReservation(reservationId);
                }
            }
        });
    }

    function cancelReservation(reservationId) {
        fetch(`/api/cancel_reservation/${reservationId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('예약이 성공적으로 취소되었습니다.');
                refreshFestivals();
            } else {
                throw new Error(data.message || '예약 취소에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.message === 'Reservation is already cancelled') {
                alert('이 예약은 이미 취소되었습니다. 페이지를 새로고침합니다.');
                refreshFestivals();
            } else {
                alert('예약 취소 중 오류가 발생했습니다: ' + error.message);
            }
        });
    }
});

