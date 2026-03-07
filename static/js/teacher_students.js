document.addEventListener('DOMContentLoaded', () => {
    // Initial Setup
    initProgressBars();
    setupTableDelegation();

    // Month Selector Logic
    const months = document.querySelectorAll('.month-item');
    const attendanceEl = document.querySelector('.Attendance');

    if (months.length && attendanceEl) {
        months.forEach(month => {
            month.addEventListener('click', async () => {
                // UI Update
                months.forEach(m => m.classList.remove('active'));
                month.classList.add('active');

                const selectedMonth = month.textContent.trim();
                const batchId = document.getElementById('batchSelect').value;
                attendanceEl.innerHTML = `Attendance (${selectedMonth})`;

                // Fetch Data
                try {
                    const response = await fetch(`/teacher/students/data?month=${selectedMonth}&batch_id=${batchId}`);
                    if (!response.ok) throw new Error('Network response was not ok');
                    const students = await response.json();
                    renderTable(students);
                } catch (error) {
                    console.error('Error fetching data:', error);
                    // Optional: Show error to user
                }
            });
        });
    }

    // Search Functionality with Debounce
    let searchTimeout;
    const searchInput = document.querySelector('.search-bar input');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(async () => {
                const query = e.target.value.trim();
                const batchId = document.getElementById('batchSelect').value;
                const activeMonth = document.querySelector('.month-item.active').textContent.trim();

                try {
                    const response = await fetch(`/teacher/students/data?month=${activeMonth}&batch_id=${batchId}&search=${query}`);
                    if (!response.ok) throw new Error('Search failed');
                    const students = await response.json();

                    renderTable(students);
                } catch (error) {
                    console.error('Error during search:', error);
                }
            }, 500);
        });
    }

    // Modal Logic (Global)
    const viewModal = document.getElementById('viewModal');
    window.onclick = function (event) {
        if (event.target == viewModal) viewModal.style.display = "none";
    }
});

function initProgressBars() {
    document.querySelectorAll('.progress-bar-fill[data-width]').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
    });
}

// Replace initModalButtons with Event Delegation
function setupTableDelegation() {
    const tbody = document.getElementById('student-table-body');
    const viewModal = document.getElementById('viewModal');


    if (!tbody) return;

    tbody.addEventListener('click', (event) => {
        const target = event.target;

        // Handle View Button
        const viewBtn = target.closest('.view-btn');
        if (viewBtn) {
            document.getElementById('viewName').textContent = viewBtn.dataset.name;
            document.getElementById('viewRoll').textContent = 'Roll No: #' + viewBtn.dataset.roll;
            document.getElementById('viewFatherName').textContent = viewBtn.dataset.fatherName;
            document.getElementById('viewAttendance').textContent = viewBtn.dataset.attendance + '%';
            document.getElementById('viewAvatar').textContent = viewBtn.dataset.initials;
            viewModal.style.display = 'block';
            return;
        }


    });

}

function renderTable(students) {
    const tbody = document.getElementById('student-table-body');
    if (!tbody) return;

    // Always clear table before rendering
    tbody.innerHTML = '';

    if (students.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                <i class="fa-solid fa-user-slash" style="font-size: 2rem; display: block; margin-bottom: 1rem; opacity: 0.5;"></i>
                No students found matching your criteria.
            </td>
        `;
        tbody.appendChild(tr);
        return;
    }

    students.forEach(student => {
        const tr = document.createElement('tr');
        tr.id = `student-row-${student.serial_no}`;

        const feesStatusHtml = student.fees_paid
            ? `<span class="status-badge paid">Paid</span>`
            : `<span class="status-badge pending">Pending</span>`;

        tr.innerHTML = `
            <td>#${student.serial_no}</td>
            <td>
                <div class="table-user-info">
                    <div class="table-avatar">${student.initials}</div>
                    <div>
                        <span style="font-weight: 600; display: block;">${student.name}</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted);">${student.father_name}</span>
                    </div>
                </div>
            </td>
            <td>${feesStatusHtml}</td>
            <td>
                <div class="progress-wrapper">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" data-width="${student.attendance}%" style="width: ${student.attendance}%"></div>
                    </div>
                    <div class="progress-text">${student.days_present}/${student.total_days}</div>
                </div>
            </td>
            <td>
                <button class="table-action-btn view-btn" title="View Profile"
                    data-name="${student.name}" data-roll="${student.serial_no}"
                    data-father-name="${student.father_name}" data-attendance="${student.attendance}"
                    data-initials="${student.initials}">
                    <i class="fa-solid fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}