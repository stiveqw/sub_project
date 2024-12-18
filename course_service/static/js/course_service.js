// Course service related JavaScript goes here

let courses = [];
let appliedCourses = [];
let allCourses = []; // 추가된 변수
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
        keptCourses = data.keptCourses || [];
        console.log('Available Courses:', courses);
        console.log('Applied Courses:', appliedCourses);
        showInitialMessage();  // 초기 메시지 표시
        updateAppliedCourses();
        
    } catch (error) {
        console.error('Error fetching course data:', error);
        alert('과목 데이터를 불러오는 데 실패했습니다. 페이지를 새로고침 해주세요.');
    }
}

async function fetchDropdownOptions() {
    try {
        const response = await fetch('/api/dropdown_options');
        if (!response.ok) {
            throw new Error('Failed to fetch dropdown options');
        }
        const data = await response.json();
        if (data.success) {
            populateDropdowns(data.credits, data.departments);
        } else {
            throw new Error(data.message || 'Failed to fetch dropdown options');
        }
    } catch (error) {
        console.error('Error fetching dropdown options:', error);
        alert('드롭다운 옵션을 불러오는 데 실패했습니다. 페이지를 새로고침 해주세요.');
    }
}

function populateDropdowns(credits, departments) {
    const creditsDropdown = document.getElementById('creditsDropdown');
    const departmentDropdown = document.getElementById('departmentDropdown');

    if (creditsDropdown) {
        creditsDropdown.innerHTML = '<option value="">Select Credits</option>';
        credits.forEach(credit => {
            const option = document.createElement('option');
            option.value = credit;
            option.textContent = credit;
            creditsDropdown.appendChild(option);
        });
    }

    if (departmentDropdown) {
        departmentDropdown.innerHTML = '<option value="">Select Department</option>';
        departments.forEach(department => {
            const option = document.createElement('option');
            option.value = department;
            option.textContent = department;
            departmentDropdown.appendChild(option);
        });
    }
}

function createCourseList(coursesToDisplay) {
    const courseTableBody = document.getElementById('courseTableBody');
    if (!courseTableBody) return;

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
           
            <td><button class="${isFull ? 'deadline-button' : 'apply-button'}" data-course-key="${course.course_key}" ${isApplied || isFull ? 'disabled' : ''}>
                ${isApplied ? 'Applied' : isFull ? 'Deadline' : 'Apply'}
            </button></td>
        `;
        courseTableBody.appendChild(row);
    });

    updatePagination(coursesToDisplay.length);
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
    createCourseList(allCourses.length > 0 ? allCourses : courses); // 수정된 부분
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


async function handleApply(courseKey) {
    try {
        const response = await fetch('/api/apply_course', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ course_key: courseKey }),
            credentials: 'include'
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || `HTTP error! status: ${response.status}`);
        }

        return result;
    } catch (error) {
        console.error('Error applying for course:', error);
        throw error;
    }
}

function applyCourse(courseKey) {
    handleApply(courseKey)
    .then(data => {
        if (data && data.success) {
            alert('과목 신청이 성공적으로 완료되었습니다!');
            window.location.reload(); // 페이지 새로고침
        } else {
            alert(data ? data.message : '과목 신청 중 오류가 발생했습니다.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert(`과목 신청 중 오류가 발생했습니다: ${error.message}`);
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
            window.location.reload(); // 페이지 새로고침
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('과목 취소 중 오류가 발생했습니다. 다시 시도해 주세요.');
    });
}

function filterCourses(credits, department) {
    if (credits === '' && department === '') {
        showNoCoursesMessage();
        return;
    }
    showLoadingIndicator();
    fetch(`/api/search_courses?credits=${credits}&department=${department}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.courses.length === 0) {
                    showNoCoursesMessage();
                } else {
                    allCourses = data.courses;  // 수정된 부분
                    currentPage = 1;  // 수정된 부분
                    createCourseList(allCourses);
                }
            } else {
                showErrorMessage(data.message || "과목을 불러오는데 실패했습니다.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage("서버 오류가 발생했습니다.");
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

function filterCoursesByName(searchTerm) {
    if (searchTerm.trim() === '') {
        showNoCoursesMessage();
        return;
    }
    showLoadingIndicator();
    fetch(`/api/search_courses?course_name=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.courses.length === 0) {
                    showNoCoursesMessage();
                } else {
                    allCourses = data.courses;  // 수정된 부분
                    currentPage = 1;  // 수정된 부분
                    createCourseList(allCourses);
                }
            } else {
                showErrorMessage(data.message || "과목을 불러오는데 실패했습니다.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage("서버 오류가 발생했습니다.");
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

function fetchAllCourses() {
    showLoadingIndicator();
    fetch('/api/search_courses')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allCourses = data.courses;  // 수정된 부분
                currentPage = 1;  // 수정된 부분
                createCourseList(allCourses);
            } else {
                showErrorMessage(data.message || "과목을 불러오는데 실패했습니다.");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage("서버 오류가 발생했습니다.");
        })
        .finally(() => {
            hideLoadingIndicator();
        });
}

// 로딩 인디케이터 표시/숨김 함수
function showLoadingIndicator() {
    // 로딩 인디케이터를 표시하는 코드 (구현 필요)
    console.log("Loading indicator shown"); // Placeholder
}

function hideLoadingIndicator() {
    // 로딩 인디케이터를 숨기는 코드 (구현 필요)
    console.log("Loading indicator hidden"); // Placeholder
}

// 에러 메시지 표시 함수
function showErrorMessage(message) {
    alert(message);
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

function showNoCoursesMessage() {
    const courseTableBody = document.getElementById('courseTableBody');
    if (courseTableBody) {
        courseTableBody.innerHTML = `
            <tr>
                <td colspan="10" style="height: 240px; text-align: center; color: rgba(128, 128, 128, 0.7);">
                    조회된 강좌가 없습니다.
                </td>
            </tr>
        `;
    }
    updatePagination(0);
}

document.addEventListener('DOMContentLoaded', function() {
    fetchCourseData();
    fetchDropdownOptions();

    const courseTableBody = document.getElementById('courseTableBody');
    if (courseTableBody) {
        courseTableBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('apply-button') && !e.target.disabled) {
                const courseKey = e.target.getAttribute('data-course-key');
                applyCourse(courseKey);
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

    const keywordSearchBtn = document.getElementById('keywordSearchBtn');
    const courseNameSearchBtn = document.getElementById('courseNameSearchBtn');
    const courseNameInput = document.getElementById('courseNameInput');
    const creditsDropdown = document.getElementById('creditsDropdown');
    const departmentDropdown = document.getElementById('departmentDropdown');

    if (keywordSearchBtn) {
        keywordSearchBtn.addEventListener('click', function() {
            const credits = creditsDropdown.value;
            const department = departmentDropdown.value;
            filterCourses(credits, department);
        });
    }

    if (courseNameSearchBtn) {
        courseNameSearchBtn.addEventListener('click', function() {
            const searchTerm = courseNameInput.value;
            filterCoursesByName(searchTerm);
        });
    }

    const allCoursesBtn = document.getElementById('allCoursesBtn');
    if (allCoursesBtn) {
        allCoursesBtn.addEventListener('click', function() {
            currentPage = 1;
            fetchAllCourses();
        });
    }

    // 검색 버튼에 로딩 인디케이터 추가
    const searchButtons = document.querySelectorAll('.search-button');
    searchButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.textContent;
            this.innerHTML = '<span class="loading-spinner"></span> 검색 중...';
            setTimeout(() => {
                this.textContent = originalText;
            }, 1000);  // 1초 후 원래 텍스트로 복구
        });
    });
});