document.addEventListener('DOMContentLoaded', function() {
    const seatGrid = document.getElementById('seatGrid');
    const applyButton = document.getElementById('applyButton');
    let selectedSeat = null;

    // Get the token from the URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    // Store the token in localStorage
    if (token) {
        localStorage.setItem('access_token', token);
    }

    function loadFestivalInfo() {
        fetch(`/api/festival/${festivalId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('festivalTitle').textContent = data.title;
            document.getElementById('festivalDescription').textContent = data.description;
            document.getElementById('festivalDate').textContent = new Date(data.date).toLocaleString();
            document.getElementById('festivalCapacity').textContent = data.capacity;
            createSeatGrid(data.total_seats, data.reserved_seats);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('축제 정보를 불러오는 데 실패했습니다. 다시 시도해 주세요.');
        });
    }

    function createSeatGrid(totalSeats, reservedSeats) {
        seatGrid.innerHTML = '';
        for (let i = 1; i <= totalSeats; i++) {
            const seat = document.createElement('div');
            seat.className = 'seat';
            seat.textContent = i;
            if (reservedSeats.includes(i)) {
                seat.classList.add('occupied');
            } else {
                seat.addEventListener('click', () => selectSeat(seat, i));
            }
            seatGrid.appendChild(seat);
        }
    }

    function selectSeat(seatElement, seatNumber) {
        if (selectedSeat) {
            selectedSeat.classList.remove('selected');
        }
        seatElement.classList.add('selected');
        selectedSeat = seatElement;
        applyButton.disabled = false;
        document.getElementById('seatInfo').textContent = `선택된 좌석: ${seatNumber}`;
    }

    applyButton.addEventListener('click', function() {
        if (!selectedSeat) return;

        const seatNumber = parseInt(selectedSeat.textContent);
        fetch('/api/apply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                festival_id: festivalId,
                seat_number: seatNumber
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('신청이 성공적으로 완료되었습니다!');
                selectedSeat.classList.add('occupied');
                selectedSeat.classList.remove('selected');
                selectedSeat = null;
                applyButton.disabled = true;
                document.getElementById('seatInfo').textContent = '';
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('신청 중 오류가 발생했습니다. 다시 시도해 주세요.');
        });
    });

    loadFestivalInfo();
});

