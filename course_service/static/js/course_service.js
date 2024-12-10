// Course service related JavaScript goes here

let courses = [];
let appliedCourses = [];
let keptCourses = [];
let allCourses = [];
let currentPage = 1;
const itemsPerPage = 5;

async function fetchCourseData() {
    try {
        const response = await fetch('/api/get_courses');
        if (!response.ok) {
            throw new Error('Failed to fetch course data');
        }
        const data = await response.json();
        courses = data.courses || [];
        appliedCourses = data.appliedCourses || [];
        console.log('Available Courses:', courses);
        console.log('Applied Courses:', appliedCourses);
        showInitialMessage();
        updateAppliedCourses();
        await fetchKeptCourses();
    } catch (error) {
        console.error('Error fetching course data:', error);
        alert('과목 데이터를 불러오는 데 실패했습니다. 페이지를 새로고침 해주세요.');
    }
}

async function fetchKeptCourses() {
    try {
        console.log('Fetching kept courses...');
        const response = await fetch('/api/get_kept_courses');
        if (!response.ok) {
            console.error(`HTTP error! status: ${response.status}`);
            throw new Error('Failed to fetch kept courses');
        }
        const data = await response.json();
        if (data.success) {
            keptCourses = data.kept_courses || [];
            console.log('Kept Courses:', keptCourses);
            updateKeptCourses();
            updateKeepButtons();
        } else {
            console.error('Failed to fetch kept courses. Server message:', data.message);
            throw new Error(data.message || 'Failed to fetch kept courses');
        }
    } catch (error) {
        console.error('Error in fetchKeptCourses:', error);
        alert('보관된 과목 데이터를 불러오는 데 실패했습니다.');
    }
}

function updateKeptCourses() {
    const keptCoursesTableBody = document.getElementById('courseKeepTableBody');
    if (!keptCoursesTableBody) return;

    keptCoursesTableBody.innerHTML = '';
    if (keptCourses.length === 0) {
        keptCoursesTableBody.innerHTML = `
            <tr>
                <td colspan="9" style="height: 240px; text-align: center; color: rgba(128, 128, 128, 0.7);">
                    보관한 강좌가 없습니다.
                </td>
            </tr>
        `;
        return;
    }
    keptCourses.forEach(course => {
        if (course.status === 'kept') {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${course.id}</td>
                <td>${course.course_name}</td>
                <td>${course.professor}</td>
                <td>${course.max_students}</td>
                <td>${course.current_students}</td>
                <td>${course.credits}</td>
                <td>${course.department}</td>
                <td>${course.year}</td>
                <td><button class="remove-kept-button" data-course-key="${course.course_key}">Remove</button></td>
            `;
            keptCoursesTableBody.appendChild(row);
        }
    });
}

function updateKeepButtons() {
    const keepButtons = document.querySelectorAll('.keep-button');
    keepButtons.forEach(button => {
        const courseKey = button.getAttribute('data-course-key');
        const keptCourse = keptCourses.find(course => course.course_key === courseKey);
        if (keptCourse && keptCourse.status === 'kept') {
            button.disabled = true;
            button.textContent = 'Kept';
        } else {
            button.disabled = false;
            button.textContent = 'Keep';
        }
    });
}

function createCourseList(coursesToDisplay) {
    console.log('Creating course list with', coursesToDisplay.length, 'courses');
    const courseTableBody = document.getElementById('courseTableBody');
    if (!courseTableBody) {
        console.error('Course table body not found');
        return;
    }

    courseTableBody.innerHTML = '';
    if (coursesToDisplay.length === 0) {
        courseTableBody.innerHTML = `
            <tr>
                <td colspan="10" style="height: 240px; text-align: center; color: rgba(128, 128, 128, 0.7);">
                    조회된 강좌가 없습니다.
                </td>
            </tr>
        `;
        updatePagination(0);
        return;
    }

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageItems = coursesToDisplay.slice(startIndex, endIndex);

    pageItems.forEach(course => {
        const row = document.createElement('tr');
        const isApplied = appliedCourses.some(appliedCourse => appliedCourse.course_key === course.course_key);
        const isFull = course.max_students === course.current_students;
        row.innerHTML = `
            <td>${course.id}</td>
            <td>${course.course_name}</td>
            <td>${course.professor}</td>
            <td>${course.max_students}</td>
            <td>${course.current_students}</td>
            <td>${course.credits}</td>
            <td>${course.department}</td>
            <td>${course.year}</td>
            <td><button class="keep-button" data-course-key="${course.course_key}">Keep</button></td>
            <td><button class="${isFull ? 'deadline-button' : 'apply-button'}" data-course-key="${course.course_key}" ${isApplied || isFull ? 'disabled' : ''}>
                ${isApplied ? 'Applied' : isFull ? 'Deadline' : 'Apply'}
            </button></td>
        `;
        courseTableBody.appendChild(row);
    });

    console.log('Displayed', pageItems.length, 'courses on current page');
    updatePagination(coursesToDisplay.length);
    console.log('Course list creation completed');
}

function updatePagination(totalItems) {
    const paginationContainer = document.getElementById('paginationContainer');
    if (!paginationContainer) return;

    const totalPages = Math.ceil(totalItems / itemsPerPage);
    let paginationHTML = '';

    if (totalPages > 1) {
        paginationHTML += `<button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>&lt;</button>`;
        
        if (totalPages <= 10) {
            for (let i = 1; i <= totalPages; i++) {
                paginationHTML += `<button onclick="changePage(${i})" class="${currentPage === i ? 'active' : ''}">${i}</button>`;
            }
        } else {
            // Always show first page
            paginationHTML += `<button onclick="changePage(1)" class="${currentPage === 1 ? 'active' : ''}">1</button>`;

            if (currentPage > 4) {
                paginationHTML += `<span>...</span>`;
            }

            // Calculate start and end of middle section
            let start = Math.max(2, currentPage - 2);
            let end = Math.min(currentPage + 2, totalPages - 1);

            // Adjust start and end to always show 5 pages in middle section
            if (start === 2) end = Math.min(6, totalPages - 1);
            if (end === totalPages - 1) start = Math.max(totalPages - 5, 2);

            for (let i = start; i <= end; i++) {
                paginationHTML += `<button onclick="changePage(${i})" class="${currentPage === i ? 'active' : ''}">${i}</button>`;
            }

            if (currentPage < totalPages - 3) {
                paginationHTML += `<span>...</span>`;
            }

            // Always show last page
            paginationHTML += `<button onclick="changePage(${totalPages})" class="${currentPage === totalPages ? 'active' : ''}">${totalPages}</button>`;
        }
        
        paginationHTML += `<button onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>&gt;</button>`;
    }

    paginationContainer.innerHTML = paginationHTML;
}

function changePage(page) {
    currentPage = page;
    createCourseList(allCourses.length > 0 ? allCourses : courses);
}

function updateAppliedCourses() {
    const appliedCoursesTableBody = document.getElementById('appliedCoursesTableBody');
    if (!appliedCoursesTableBody) return;

    appliedCoursesTableBody.innerHTML = '';
    if (appliedCourses.length === 0) {
        appliedCoursesTableBody.innerHTML = `
            <tr>
                <td colspan="8" style="height: 240px; text-align: center; color: rgba(128, 128, 128, 0.7);">
                    신청한 강좌가 없습니다.
                </td>
            </tr>
        `;
        return;
    }
    appliedCourses.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${course.id}</td>
            <td>${course.course_name}</td>
            <td>${course.professor}</td>
            <td>${course.credits}</td>
            <td>${course.department}</td>
            <td>${course.year}</td>
            <td>Applied</td>
            <td><button class="cancel-button" data-course-key="${course.course_key}">Cancel</button></td>
        `;
        appliedCoursesTableBody.appendChild(row);
    });
}

function keepCourse(courseKey) {
    console.log(`Attempting to keep course with key: ${courseKey}`);
    fetch('/api/keep_course', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            course_key: courseKey
        }),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            console.error(`HTTP error! status: ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log(`Successfully kept course: ${courseKey}`);
            alert('과목이 성공적으로 보관되었습니다!');
            fetchKeptCourses();
        } else {
            console.error(`Failed to keep course: ${courseKey}. Server message: ${data.message}`);
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error in keepCourse:', error);
        alert('과목 보관 중 오류가 발생했습니다. 다시 시도해 주세요.');
    });
}

function removeKeptCourse(courseKey) {
    console.log(`Attempting to remove kept course with key: ${courseKey}`);
    fetch('/api/remove_kept_course', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            course_key: courseKey
        }),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            console.error(`HTTP error! status: ${response.status}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log(`Successfully removed kept course: ${courseKey}`);
            alert('과목이 성공적으로 보관 목록에서 제거되었습니다!');
            fetchKeptCourses();
        } else {
            console.error(`Failed to remove kept course: ${courseKey}. Server message: ${data.message}`);
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error in removeKeptCourse:', error);
        alert('과목 제거 중 오류가 발생했습니다. 다시 시도해 주세요.');
    });
}

function applyCourse(courseKey) {
    fetch('/api/apply_course', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ course_key: courseKey }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('과목 신청이 성공적으로 완료되었습니다!');
            fetchCourseData();
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('과목 신청 중 오류가 발생했습니다. 다시 시도해 주세요.');
    });
}

function cancelCourse(courseKey) {
    fetch('/api/cancel_course', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            course_key: courseKey
        }),
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('과목 취소가 성공적으로 완료되었습니다!');
            fetchCourseData();
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('과목 취소 중 오류가 발생했습니다. 다시 시도해 주세요.');
    });
}

function showInitialMessage() {
    const courseTableBody = document.getElementById('courseTableBody');
    if (courseTableBody) {
        courseTableBody.innerHTML = `
            <tr>
                <td colspan="10" style="height: 240px; text-align: center; color: rgba(128, 128, 128, 0.7);">
                    원하는 과목을 검색하세요
                </td>
            </tr>
        `;
    }
    updatePagination(0);
}

document.addEventListener('DOMContentLoaded', function() {
    fetchCourseData();

    const courseTableBody = document.getElementById('courseTableBody');
    if (courseTableBody) {
        courseTableBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('apply-button') && !e.target.disabled) {
                const courseKey = e.target.getAttribute('data-course-key');
                applyCourse(courseKey);
            }
            if (e.target.classList.contains('keep-button') && !e.target.disabled) {
                const courseKey = e.target.getAttribute('data-course-key');
                keepCourse(courseKey);
            }
        });
    }

    const appliedCoursesTableBody = document.getElementById('appliedCoursesTableBody');
    if (appliedCoursesTableBody) {
        appliedCoursesTableBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('cancel-button')) {
                const courseKey = e.target.getAttribute('data-course-key');
                cancelCourse(courseKey);
            }
        });
    }

    const courseKeepTableBody = document.getElementById('courseKeepTableBody');
    if (courseKeepTableBody) {
        courseKeepTableBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-kept-button')) {
                const courseKey = e.target.getAttribute('data-course-key');
                removeKeptCourse(courseKey);
            }
        });
    }
});

