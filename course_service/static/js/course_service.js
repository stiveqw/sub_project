// API 요청을 보내는 함수
async function sendApiRequest(url, method, data) {
    const headers = {
        'Content-Type': 'application/json'
    };

    const response = await fetch(url, {
        method: method,
        headers: headers,
        body: method !== 'GET' ? JSON.stringify(data) : undefined,
        credentials: 'include'
    });

    if (!response.ok) {
        if (response.status === 401) {
            window.location.href = '/login';
            throw new Error('Authentication required');
        }
        const errorData = await response.json();
        throw new Error(errorData.error || 'API request failed');
    }

    return response.json();
}

// 신청한 코스 목록을 업데이트하는 함수
async function updateAppliedCourses() {
    try {
        const result = await sendApiRequest('/api/get_applied_courses', 'GET');
        const appliedCoursesBody = document.getElementById('appliedCoursesTableBody');
        appliedCoursesBody.innerHTML = '';

        console.log('Applied courses result:', result); // 디버깅을 위한 로그 추가

        if (result.success && result.courses && result.courses.length > 0) {
            result.courses.forEach(course => {
                const row = `
                    <tr>
                        <td>${course.id}</td>
                        <td>${course.course_name}</td>
                        <td>${course.professor}</td>
                        <td>${course.credits}</td>
                        <td>${course.department}</td>
                        <td>${course.year}</td>
                        <td>Applied</td>
                        <td><button onclick="handleCancel(${course.key})">Cancel</button></td>
                    </tr>
                `;
                appliedCoursesBody.innerHTML += row;
            });
        } else {
            appliedCoursesBody.innerHTML = `
                <tr>
                    <td id="no-applied-courses-message" colspan="8" style="height: 18em; text-align: center; vertical-align: middle;">
                        조회된 데이터가 없습니다
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        console.error('Error fetching applied courses:', error);
        const appliedCoursesBody = document.getElementById('appliedCoursesTableBody');
        appliedCoursesBody.innerHTML = `
            <tr>
                <td colspan="8" style="height: 18em; text-align: center; vertical-align: middle;">
                    데이터를 불러오는 중 오류가 발생했습니다
                </td>
            </tr>
        `;
    }
}

// CANCEL 버튼 클릭 핸들러
async function handleCancel(courseId) {
    try {
        const result = await sendApiRequest('/api/cancel_course', 'POST', { course_id: courseId });
        if (result.success) {
            alert('Course cancellation successful!');
            updateAppliedCourses();
        } else {
            alert('Course cancellation failed: ' + result.message);
        }
    } catch (error) {
        console.error('Error cancelling course:', error);
        alert('An error occurred while cancelling the course.');
    }
}

// 코스 검색 함수
async function searchCourses() {
    const credits = document.getElementById('creditsDropdown').value;
    const department = document.getElementById('departmentDropdown').value;
    const courseName = document.getElementById('courseNameInput').value.trim();

    // Check if search criteria are empty or default
    if ((credits === 'Select Credits' || credits === '') &&
        (department === 'Select Department' || department === '') &&
        courseName === '') {
        updateCourseTable([]);  // This will display "조회된 데이터가 없습니다"
        return;
    }

    try {
        const result = await sendApiRequest(`/api/search_courses?credits=${credits}&department=${department}&course_name=${courseName}`, 'GET');
        if (result.courses) {
            updateCourseTable(result.courses);
        } else {
            console.error('Failed to fetch courses:', result.message);
            updateCourseTable([]);  // This will display "조회된 데이터가 없습니다"
        }
    } catch (error) {
        console.error('Error searching courses:', error);
        updateCourseTable([]);  // This will display "조회된 데이터가 없습니다"
    }
}

// 코스 테이블 업데이트 함수
function updateCourseTable(courses) {
    const courseTableBody = document.getElementById('courseTableBody');
    courseTableBody.innerHTML = '';
    if (courses.length === 0) {
        const emptyRow = `
            <tr>
                <td id="no-data-message" colspan="10" style="height: 18em; text-align: center; vertical-align: middle;">
                    조회된 데이터가 없습니다
                </td>
            </tr>
        `;
        courseTableBody.innerHTML = emptyRow;
    } else {
        courses.forEach(course => {
            const row = `
                <tr>
                    <td>${course.id}</td>
                    <td>${course.course_name}</td>
                    <td>${course.professor}</td>
                    <td>${course.max_students}</td>
                    <td>${course.current_students}</td>
                    <td>${course.credits}</td>
                    <td>${course.department}</td>
                    <td>${course.year}</td>
                    <td><button class="keep-button" data-course-key="${course.key}">Keep</button></td>
                    <td><button class="apply-button" data-course-key="${course.key}">Apply</button></td>
                </tr>
            `;
            courseTableBody.innerHTML += row;
        });
    }
}

// KEEP 버튼 클릭 핸들러
function handleKeep(courseKey) {
    // 여기에 KEEP 기능 구현
    console.log('Keep course:', courseKey);
}

// 드롭다운 메뉴 채우기
async function populateDropdowns() {
    try {
        const creditsResult = await sendApiRequest('/api/credits', 'GET');
        const departmentsResult = await sendApiRequest('/api/departments', 'GET');

        const creditsDropdown = document.getElementById('creditsDropdown');
        const departmentDropdown = document.getElementById('departmentDropdown');

        creditsResult.credits.forEach(credit => {
            const option = document.createElement('option');
            option.value = credit;
            option.textContent = credit;
            creditsDropdown.appendChild(option);
        });

        departmentsResult.departments.forEach(department => {
            const option = document.createElement('option');
            option.value = department;
            option.textContent = department;
            departmentDropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error populating dropdowns:', error);
    }
}

// 이벤트 리스너 설정
function attachEventListeners() {
    document.getElementById('keywordSearchBtn').addEventListener('click', searchCourses);
    document.getElementById('courseNameSearchBtn').addEventListener('click', searchCourses);
}

function addButtonEventListeners() {
    const courseTableBody = document.getElementById('courseTableBody');
    courseTableBody.addEventListener('click', function(event) {
        if (event.target.classList.contains('keep-btn')) {
            handleKeep(event.target.dataset.courseKey);
        } else if (event.target.classList.contains('apply-btn')) {
            handleApply(event.target.dataset.courseKey);
        }
    });
}

// 페이지 로드 시 실행되는 초기화 함수
async function initializePage() {
    await updateAppliedCourses();
    await populateDropdowns();
    attachEventListeners();
    addButtonEventListeners();
    updateCourseTable([]); // 페이지 로드 시 Course List를 빈 상태로 초기화
}

// 페이지 로드 시 초기화 함수 실행
document.addEventListener('DOMContentLoaded', initializePage);

// APPLY 버튼 클릭 핸들러
async function handleApply(courseKey) {
    try {
        const result = await sendApiRequest('/api/apply_course', 'POST', { course_key: courseKey });
        if (result.success) {
            alert('Course application successful!');
            updateAppliedCourses();
        } else {
            alert('Course application failed: ' + result.message);
        }
    } catch (error) {
        console.error('Error applying for course:', error);
        alert('An error occurred while applying for the course.');
    }
}

