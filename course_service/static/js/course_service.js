document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    const itemsPerPage = 3;

    function fetchCourses(page) {
        fetch(`/api/courses?page=${page}&per_page=${itemsPerPage}`)
            .then(response => response.json())
            .then(data => {
                displayCourses(data.courses);
                setupPagination(data.total_pages);
            })
            .catch(error => console.error('Error:', error));
    }

    function displayCourses(courses) {
        const tableBody = document.getElementById('courseTableBody');
        tableBody.innerHTML = '';
        courses.forEach(course => {
            const row = `
                <tr>
                    <td>${course.id}</td>
                    <td>${course.course_name}</td>
                    <td>${course.professor}</td>
                    <td>${course.max_students}</td>
                    <td>${course.department}</td>
                    <td>${course.year}</td>
                    <td>${new Date(course.created_at).toLocaleString()}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    }

    function setupPagination(totalPages) {
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';

        if (currentPage > 1) {
            pagination.innerHTML += `<button onclick="changePage(${currentPage - 1})">&lt;</button>`;
        }

        for (let i = 1; i <= totalPages; i++) {
            pagination.innerHTML += `<button onclick="changePage(${i})" ${i === currentPage ? 'class="active"' : ''}>${i}</button>`;
        }

        if (currentPage < totalPages) {
            pagination.innerHTML += `<button onclick="changePage(${currentPage + 1})">&gt;</button>`;
        }
    }

    window.changePage = function(page) {
        currentPage = page;
        fetchCourses(currentPage);
    }

    fetchCourses(currentPage);
});

