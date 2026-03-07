document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const body = document.body;
    const container = document.querySelector('.dashboard-container');

    // Create overlay element dynamically
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';

    // Append to container if it exists (for z-index context), otherwise body
    if (container) {
        container.appendChild(overlay);
    } else {
        body.appendChild(overlay);
    }

    // Mobile Resize Sync Logic (Critical)
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            // Reset to Desktop State
            sidebar.classList.remove('sidebar-toggled');
            overlay.classList.remove('active');
            body.style.overflow = ''; // Allow scrolling
            sidebar.style.transform = ''; // Clear inline styles if any
        }
    });

    function closeSidebar() {
        sidebar.classList.remove('sidebar-toggled');
        overlay.classList.remove('active');
        body.style.overflow = '';
    }

    function openSidebar() {
        sidebar.classList.add('sidebar-toggled');
        overlay.classList.add('active');
        // Only lock scroll on mobile
        if (window.innerWidth <= 768) {
            body.style.overflow = 'hidden';
        }
    }

    function toggleSidebar() {
        if (sidebar.classList.contains('sidebar-toggled')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSidebar();
        });
    }

    // Close when clicking overlay
    overlay.addEventListener('click', closeSidebar);

    // Close when clicking any nav link on mobile
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });

    // Prevent FOUC: Add class to body once loaded
    document.documentElement.classList.add('loaded');
    // Global Search Logic
    const searchInput = document.querySelector('.search-bar input');
    const searchResults = document.getElementById('searchResults');
    let searchTimeout;

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length < 2) {
                searchResults.classList.add('hidden');
                return;
            }

            searchTimeout = setTimeout(async () => {
                try {
                    const response = await fetch(`/teacher/api/global-search?search=${query}`);
                    if (!response.ok) throw new Error('Search failed');
                    const data = await response.json();
                    renderSearchResults(data);
                } catch (error) {
                    console.error('Global search error:', error);
                }
            }, 500);
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add('hidden');
            }
        });

        // Close search results on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchResults.classList.add('hidden');
            }
        });
    }

    function renderSearchResults(data) {
        if (data.classes.length === 0 && data.students.length === 0) {
            searchResults.innerHTML = '<p style="padding: 20px; text-align: center; color: var(--text-muted);">No results found.</p>';
        } else {
            let html = '';

            if (data.classes.length > 0) {
                html += '<div class="search-section-title">Classes & Batches</div>';
                data.classes.forEach(c => {
                    html += `
                        <a href="/teacher/classes/details?batch_id=${c.id}" class="search-item">
                            <div class="item-icon"><i class="fa-solid fa-book"></i></div>
                            <div class="item-info">
                                <h4>${c.name}</h4>
                                <p>${c.subject}</p>
                            </div>
                            <span class="item-type">Class</span>
                        </a>
                    `;
                });
            }

            if (data.students.length > 0) {
                html += '<div class="search-section-title">Students</div>';
                data.students.forEach(s => {
                    html += `
                        <a href="/teacher/students?batch_id=${s.batch_id}" class="search-item">
                            <div class="item-icon">${s.initials}</div>
                            <div class="item-info">
                                <h4>${s.name}</h4>
                                <p>View in Student List</p>
                            </div>
                            <span class="item-type">Student</span>
                        </a>
                    `;
                });
            }

            searchResults.innerHTML = html;
        }
        searchResults.classList.remove('hidden');
    }
});
