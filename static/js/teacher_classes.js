// Teacher Classes - Dynamic Data & Logic

let classesData = [];
let todayDayCode = 0; // Set on load
// Colors to cycle through for cards
const classColors = [
  "#8c7ae6", // Purple
  "#ff7675", // Salmon
  "#00b894", // Teal
  "#74b9ff", // Blue
  "#e67e22", // Orange
  "#fd79a8", // Pink
  "#fbc531", // Yellow
  "#2d3436"  // Dark Grey
];

document.addEventListener("DOMContentLoaded", () => {
  const cardViewBtn = document.getElementById("cardViewBtn");
  const tableViewBtn = document.getElementById("tableViewBtn");
  const classesContainer = document.getElementById("classesContainer");
  const classesTableContainer = document.getElementById("classesTableContainer");
  const classesTableBody = document.getElementById("classesTableBody");
  const dayTabs = document.querySelectorAll(".day-tab");
  let currentDayFilter = "today";

  // Fetch Data from Backend
  async function fetchClasses(search = "") {
    try {
      const response = await fetch(
        `/teacher/api/classes-list${search ? `?search=${search}` : ""}`
      );
      if (!response.ok) throw new Error("Failed to fetch classes");

      const data = await response.json();

      // Enhance data with colors
      classesData = data.map((cls, index) => ({
        ...cls,
        color: classColors[index % classColors.length],
      }));

      renderAll();
      renderTodayOverview();
    } catch (error) {
      console.error("Error loading classes:", error);
      if (classesContainer) {
        classesContainer.innerHTML = `<p class="error-msg">Failed to load classes. Please try again.</p>`;
      }
    }
  }

  // Search Functionality with Debounce
  let searchTimeout;
  const searchInput = document.querySelector(".search-bar input");

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        fetchClasses(e.target.value.trim());
      }, 500);
    });
  }

  function renderAll() {
    const filteredData = filterDataByDay(classesData, currentDayFilter);
    renderCards(filteredData);
    renderTable(filteredData);
  }

  function filterDataByDay(data, filter) {
    if (filter === "all") return data;

    let targetDay;
    if (filter === "today") {
      // getDay() returns 0 for Sunday, 1 for Monday...
      // Our backend day_code is 1 for Mon, 7 for Sun
      const day = new Date().getDay();
      targetDay = day === 0 ? 7 : day;
    } else {
      targetDay = parseInt(filter, 10);
    }

    // BUG FIX: Use Number() on both sides to prevent string vs number mismatch
    return data.filter(cls => Number(cls.day_code) === Number(targetDay));
  }

  // ----- Today's Overview Bar -----
  function renderTodayOverview() {
    const overviewEl = document.getElementById("todayOverview");
    if (!overviewEl) return;

    const day = new Date().getDay();
    todayDayCode = day === 0 ? 7 : day;

    const todayClasses = classesData.filter(
      cls => Number(cls.day_code) === todayDayCode
    );

    if (todayClasses.length === 0) {
      overviewEl.innerHTML = `
        <div class="overview-item">
          <i class="fa-solid fa-mug-hot"></i>
          <div class="overview-label">Today</div>
          <div class="overview-value">No classes scheduled</div>
        </div>
      `;
      return;
    }

    const totalStudentsToday = todayClasses.reduce((sum, c) => sum + (c.students || 0), 0);

    // Find next class by parsing time string (e.g. "Monday 10:00 AM")
    const now = new Date();
    const nowMinutes = now.getHours() * 60 + now.getMinutes();

    // Extract time from the "Day HH:MM AM/PM" format
    function parseTimeToMinutes(timeStr) {
      const match = timeStr.match(/(\d+):(\d+)\s*(AM|PM)/i);
      if (!match) return -1;
      let hours = parseInt(match[1], 10);
      const mins = parseInt(match[2], 10);
      const period = match[3].toUpperCase();
      if (period === "PM" && hours !== 12) hours += 12;
      if (period === "AM" && hours === 12) hours = 0;
      return hours * 60 + mins;
    }

    let nextClass = null;
    let nextClassMins = Infinity;
    for (const cls of todayClasses) {
      const classMins = parseTimeToMinutes(cls.time);
      if (classMins > nowMinutes && classMins < nextClassMins) {
        nextClassMins = classMins;
        nextClass = cls;
      }
    }

    const nextClassHTML = nextClass
      ? `<span class="overview-highlight">${nextClass.subject}</span> at <span class="overview-highlight">${nextClass.time.split(" ").slice(1).join(" ")}</span>`
      : `<span style="color: rgba(255,255,255,0.5)">All classes done for today</span>`;

    overviewEl.innerHTML = `
      <div class="overview-item">
        <div class="overview-icon-wrap purple-wrap"><i class="fa-solid fa-calendar-check"></i></div>
        <div class="overview-text">
          <div class="overview-label">Today's Classes</div>
          <div class="overview-value">${todayClasses.length} class${todayClasses.length !== 1 ? "es" : ""}</div>
        </div>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-item">
        <div class="overview-icon-wrap teal-wrap"><i class="fa-solid fa-users"></i></div>
        <div class="overview-text">
          <div class="overview-label">Total Students</div>
          <div class="overview-value">${totalStudentsToday}</div>
        </div>
      </div>
      <div class="overview-divider"></div>
      <div class="overview-item">
        <div class="overview-icon-wrap orange-wrap"><i class="fa-solid fa-clock"></i></div>
        <div class="overview-text">
          <div class="overview-label">Next Class</div>
          <div class="overview-value next-class-val">${nextClassHTML}</div>
        </div>
      </div>
    `;
  }

  // Render Functions
  function renderCards(data) {
    if (!classesContainer) return;

    if (data.length === 0) {
      classesContainer.innerHTML = '<p class="empty-msg" style="color: var(--text-secondary); grid-column: 1/-1; text-align: center; padding: 2rem;">No classes found for this day.</p>';
      return;
    }

    classesContainer.innerHTML = data
      .map(
        (cls, index) => `
            <div class="class-card" style="animation-delay: ${index * 0.1}s">
                <!-- Top Half: Solid Color -->
                <div class="class-header-color" style="background: ${cls.color}">
                    <span class="class-badge">${cls.name}</span>
                </div>
                
                <!-- Bottom Half: Dark Glass -->
                <div class="class-body-glass">
                    <h3 class="class-title">${cls.subject}</h3>
                    
                    <div class="class-meta-row">
                        <span><i class="fa-solid fa-clock"></i> ${cls.time}</span>
                        <span><i class="fa-solid fa-user-group"></i> ${cls.students} Students</span>
                    </div>
                    
                    <div class="class-actions-row">
                        <button class="action-btn btn-primary" onclick="openClass(${cls.id})">Start Class</button>
                        <button class="action-btn btn-outline" onclick="openAttendance(${cls.id})">Attendance</button>
                    </div>
                </div>
            </div>
        `
      )
      .join("");
  }

  function renderTable(data) {
    if (!classesTableBody) return;

    classesTableBody.innerHTML = data
      .map(
        (cls) => `
            <tr>
                <td style="font-weight: 500;">${cls.name}</td>
                <td>${cls.subject}</td>
                <td>${cls.students}</td>
                <td>${cls.time}</td>
                <td>
                    <button class="table-action-btn" onclick="openClass(${cls.id})">
                        Open Class
                    </button>
                </td>
            </tr>
        `
      )
      .join("");
  }

  // Day Filter Logic
  dayTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      // Update UI
      dayTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      // Update Filter & Render
      currentDayFilter = tab.dataset.day;
      renderAll();
    });
  });

  // View Toggles
  if (cardViewBtn && tableViewBtn) {
    const homeworkContainer = document.getElementById("homeworkContainer");

    cardViewBtn.addEventListener("click", () => {
      cardViewBtn.classList.add("active");
      tableViewBtn.classList.remove("active");
      classesContainer.classList.remove("hidden");
      classesTableContainer.classList.add("hidden");
      if (homeworkContainer) homeworkContainer.classList.remove("hidden");
    });

    tableViewBtn.addEventListener("click", () => {
      tableViewBtn.classList.add("active");
      cardViewBtn.classList.remove("active");
      classesTableContainer.classList.remove("hidden");
      classesContainer.classList.add("hidden");
      if (homeworkContainer) homeworkContainer.classList.add("hidden");
    });
  }

  // Fetch Homework Data
  async function fetchHomework() {
    const homeworkRows = document.getElementById("homeworkRows");
    if (!homeworkRows) return;

    try {
      const response = await fetch("/teacher/api/homework-list");
      if (!response.ok) throw new Error("Failed to fetch homework");
      const data = await response.json();
      renderHomework(data);
    } catch (error) {
      console.error("Error loading homework:", error);
      homeworkRows.innerHTML = `<p class="error-msg">Failed to load homework.</p>`;
    }
  }

  function renderHomework(data) {
    const homeworkRows = document.getElementById("homeworkRows");
    if (!homeworkRows) return;

    if (data.length === 0) {
      homeworkRows.innerHTML = `
        <div class="homework-row" style="justify-content: center; padding: 2rem; color: var(--text-secondary);">
          No recent homework found.
        </div>
      `;
      return;
    }

    homeworkRows.innerHTML = data.map(hw => `
      <div class="homework-row">
        <div class="hw-col hw-col-title">
          <div class="hw-title-content">
            <div class="hw-icon ${hw.percent === 100 ? 'teal-icon' : 'purple-icon'}">
              <i class="fa-solid fa-file-lines"></i>
            </div>
            <div class="hw-title-info">
              <h4>${hw.title}</h4>
              <p>${hw.subject} • ${hw.batch}</p>
            </div>
          </div>
        </div>
        <div class="hw-col hw-col-date">
          <div class="hw-date-info">
            <span class="hw-date-day">${hw.due_day}</span>
            <span class="hw-date-full">${hw.due_date}</span>
          </div>
        </div>
        <div class="hw-col hw-col-status">
          <span class="hw-status-badge ${hw.percent === 100 ? 'completed' : 'pending'}">${hw.status}</span>
        </div>
        <div class="hw-col hw-col-submissions">
          <div class="hw-submission-info">
            <span class="hw-submission-count">${hw.submissions_count} / ${hw.total_students}</span>
            <span class="hw-submission-percent">${hw.percent}% Collected</span>
          </div>
        </div>
        <div class="hw-col hw-col-actions">
          <button class="hw-action-button ${hw.percent === 100 ? 'check-btn' : 'primary-btn'}" onclick="viewHomework(${hw.id})">
            ${hw.percent === 100 ? '<i class="fa-solid fa-check"></i>' : 'Review'}
          </button>
        </div>
      </div>
    `).join("");
  }

  // Initial Fetch
  fetchClasses();
  fetchHomework();
});

window.viewHomework = function (id) {
  console.log("Viewing homework:", id);
  // Future: window.location.href = `/teacher/homework/${id}`;
};

// Global navigation functions
window.openClass = function (batchId) {
  // Can link to a specific "Start Class" view or just the details
  window.location.href = `/teacher/classes/details?batch_id=${batchId}&mode=start`;
};

window.openAttendance = function (batchId) {
  // Link to the attendance tab of the details page
  window.location.href = `/teacher/classes/details?batch_id=${batchId}&tab=attendance`;
};
