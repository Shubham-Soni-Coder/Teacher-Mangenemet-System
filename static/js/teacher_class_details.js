// Teacher Class Details - Attendance Logic


document.addEventListener('DOMContentLoaded', () => {
    // Set Date to Today
    document.getElementById('attendanceDate').valueAsDate = new Date();

    const attendanceGrid = document.getElementById('attendanceGrid');
    const presentCountEl = document.getElementById('presentCount');
    const absentCountEl = document.getElementById('absentCount');
    const markAllPresentBtn = document.getElementById('markAllPresentBtn');
    const saveAttendanceBtn = document.getElementById('saveAttendanceBtn');
    const pageMode = document.getElementById("pageMode").value;

    // Use global studentsData
    let studentsData = window.studentsData || [];

    // Render Student Cards
    function renderStudents() {
        if (!studentsData.length) {
            attendanceGrid.innerHTML = '<p style="text-align:center; width:100%; color: var(--text-muted);">No students found.</p>';
            return;
        }

        attendanceGrid.innerHTML = studentsData.map(student => `
            <div class="student-card" id="card-${student.student_id}">
                <div class="student-info">
                    <div class="student-avatar" style="background: hsl(${student.student_id * 15}, 70%, 50%)">
                        ${student.initials}
                    </div>
                    <div class="student-details">
                        <h4>${student.name}</h4>
                        <span class="student-roll">Roll No: #${student.rollNo}</span>
                    </div>
                </div>
                <button class="attendance-toggle ${student.status}" onclick="toggleAttendance(${student.student_id})">
                    <i class="fa-solid ${student.status === 'present' ? 'fa-check' : 'fa-xmark'}"></i>
                </button>
            </div>
        `).join('');
        updateStats();
    }

    // Update Counts
    function updateStats() {
        const present = studentsData.filter(s => s.status === 'present').length;
        const absent = studentsData.length - present;
        presentCountEl.textContent = present;
        absentCountEl.textContent = absent;
    }

    // Toggle Handler (Global scope)
    window.toggleAttendance = function (student_id) {
        const student = studentsData.find(s => s.student_id === student_id);
        if (student) {
            student.status = student.status === 'present' ? 'absent' : 'present';
            // Sync is_present with status
            student.is_present = (student.status === 'present');

            // Update UI for this specific card
            const btn = document.querySelector(`#card-${student_id} .attendance-toggle`);
            if (btn) {
                btn.className = `attendance-toggle ${student.status}`;
                btn.innerHTML = `<i class="fa-solid ${student.status === 'present' ? 'fa-check' : 'fa-xmark'}"></i>`;
            }

            // Update stats
            updateStats();
        }
    };

    // Mark All Present
    markAllPresentBtn.addEventListener('click', () => {
        studentsData.forEach(s => {
            s.status = 'present';
            s.is_present = true;
        });
        renderStudents();
    });

    saveAttendanceBtn.addEventListener('click', () => {
        const classid = parseInt(document.getElementById("batchId").value);
        const data = document.getElementById('attendanceDate').value;

        if (!data) {
            alert("Select a data")
            return
        }

        // Build the playload 


        const payload = {
            batch_id: classid,
            date: data,
            session_type: "morning", // later make dynamic
            attendance: studentsData.map(s => ({
                student_id: s.student_id,
                is_present: s.is_present
            }))
        };

        console.log("FINAL PAYLOAD:", payload);

        fetch("/api/attendance", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(res => {
                if (!res.ok) {
                    throw new Error("Falied to load the data");
                }
                return res.json()
            })
            .then(data => {
                alert("Attendance saved successfully");
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Failed to save attendance");
            })
    });

    // Save the attendance 


    // Initial Render
    renderStudents();
});
