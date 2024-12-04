document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    const festivalsPerPage = 6;
    let allFestivals = [];

    function loadFestivals() {
        fetch('/api/festivals')
            .then(response => response.json())
            .then(festivals => {
                allFestivals = festivals;
                displayFestivals();
                updatePaginationButtons();
            });
    }

    function displayFestivals() {
        const startIndex = (currentPage - 1) * festivalsPerPage;
        const endIndex = startIndex + festivalsPerPage;
        const festivalsToShow = allFestivals.slice(startIndex, endIndex);

        const festivalGrid = document.getElementById('festivalGrid');
        festivalGrid.innerHTML = '';

        festivalsToShow.forEach(festival => {
            const festivalElement = document.createElement('div');
            festivalElement.className = 'festival-item';
            festivalElement.innerHTML = `
                <img src="${festival.image}" alt="${festival.title}">
                <h3>${festival.title}</h3>
                <p>${festival.description}</p>
                <p>Date: ${new Date(festival.date).toLocaleDateString()}</p>
                <button onclick="location.href='/apply/${festival.id}'">Apply Now</button>
            `;
            festivalGrid.appendChild(festivalElement);
        });
    }

    function updatePaginationButtons() {
        const prevButton = document.getElementById('prevPage');
        const nextButton = document.getElementById('nextPage');

        prevButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage === Math.ceil(allFestivals.length / festivalsPerPage);
    }

    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayFestivals();
            updatePaginationButtons();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        if (currentPage < Math.ceil(allFestivals.length / festivalsPerPage)) {
            currentPage++;
            displayFestivals();
            updatePaginationButtons();
        }
    });

    loadFestivals();
});

