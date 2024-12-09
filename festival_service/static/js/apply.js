// 전역 변수에서 축제 데이터 가져오기
const { festivalKey, festivalTotalSeats, reservedSeats, isAlreadyReserved } = window.festivalData;
console.log('Festival Key:', festivalKey);
console.log('Total Seats:', festivalTotalSeats);
console.log('Reserved Seats:', reservedSeats);
console.log('Is Already Reserved:', isAlreadyReserved);

function formatSeatNumber(seatIndex) {
  const row = String.fromCharCode('A'.charCodeAt(0) + Math.floor((seatIndex - 1) / 30));
  const number = ((seatIndex - 1) % 30) + 1;
  return `${row}${number}`;
}

function createSeatGrid(totalSeats) {
  const seatGrid = document.getElementById('seatGrid');
  seatGrid.innerHTML = '';
  for (let i = 1; i <= totalSeats; i++) {
      if (i % 12 === 1) {
          // 새로운 줄 시작
          const row = document.createElement('div');
          row.className = 'seat-row';
          seatGrid.appendChild(row);
      }

      const seat = document.createElement('div');
      seat.className = 'seat';
      const seatNumber = formatSeatNumber(i);
      if (reservedSeats.includes(seatNumber)) {
          seat.classList.add('occupied');
      } else {
          seat.addEventListener('click', () => selectSeat(seat, seatNumber));
      }
      seat.textContent = seatNumber;

      const currentRow = seatGrid.lastElementChild;
      if (i % 12 <= 6) {
          // 좌측 좌석
          currentRow.appendChild(seat);
      } else if (i % 12 === 7) {
          // 중앙 여백
          const spacer = document.createElement('div');
          spacer.className = 'spacer';
          currentRow.appendChild(spacer);
          currentRow.appendChild(seat);
      } else {
          // 우측 좌석
          currentRow.appendChild(seat);
      }
  }
}

function selectSeat(seatElement, seatNumber) {
  const applyButton = document.getElementById('applyButton');
  if (seatElement.classList.contains('occupied')) {
      return;
  }

  if (window.selectedSeat === seatElement) {
      // 이미 선택된 좌석을 다시 클릭한 경우
      seatElement.classList.remove('selected');
      window.selectedSeat = null;
      applyButton.disabled = true;
      document.getElementById('seatInfo').textContent = '';
  } else {
      // 새로운 좌석을 선택한 경우
      if (window.selectedSeat) {
          window.selectedSeat.classList.remove('selected');
      }
      seatElement.classList.add('selected');
      window.selectedSeat = seatElement;
      applyButton.disabled = false;
      document.getElementById('seatInfo').textContent = `선택된 좌석: ${seatNumber}`;
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const applyButton = document.getElementById('applyButton');

  if (isAlreadyReserved) {
    applyButton.textContent = '이미 예약한 축제입니다';
    applyButton.disabled = true;
    applyButton.classList.add('reserved');
  } else {
    applyButton.addEventListener('click', function() {
        if (!window.selectedSeat) return;

        const seatNumber = window.selectedSeat.textContent;
        fetch('/api/apply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                festival_key: festivalKey, 
                seat_number: seatNumber
            }),
            credentials: 'include'  
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('신청이 성공적으로 완료되었습니다!');
                setTimeout(() => {
                    window.location.href = '/';
                }, 500); // 0.5초 후에 리다이렉트
            } else {
                alert(data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('신청 중 오류가 발생했습니다. 다시 시도해 주세요.');
        });
    });
  }

  // 페이지 로드 시 좌석 그리드 생성
  createSeatGrid(festivalTotalSeats);
});

// 페이지 로드 완료 후 좌석 그리드 생성
window.onload = function() {
  createSeatGrid(festivalTotalSeats);
};