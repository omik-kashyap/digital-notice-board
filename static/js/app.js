/**
 * Campus Notice Board - Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    let state = {
        adminMode: false,
        activeCategory: "all",
        sortBy: "date_desc",
        searchQuery: "",
        notices: [],
        currentNoticeToDelete: null
    };

    // DOM Elements
    const noticesContainer = document.getElementById("noticesContainer");
    const categoryTabsContainer = document.getElementById("categoryTabs");
    const searchInput = document.getElementById("searchInput");
    const searchClearBtn = document.getElementById("searchClearBtn");
    const sortSelect = document.getElementById("sortSelect");
    const resultsCount = document.getElementById("resultsCount");
    const btnRefresh = document.getElementById("btnRefresh");

    // Banner elements
    const urgentBanner = document.getElementById("urgentBanner");
    const bannerText = document.getElementById("bannerText");
    const btnBannerView = document.getElementById("btnBannerView");
    const btnBannerClose = document.getElementById("btnBannerClose");
    let currentBannerNotice = null;

    // Overview Stats
    const statTotal = document.getElementById("statTotal");
    const statUrgent = document.getElementById("statUrgent");
    const statPinned = document.getElementById("statPinned");
    const statCategories = document.getElementById("statCategories");

    // Admin Controls
    const adminToggleCheckbox = document.getElementById("adminToggleCheckbox");
    const adminLabelText = document.getElementById("adminLabelText");
    const btnOpenPostModal = document.getElementById("btnOpenPostModal");

    // Theme Toggle
    const btnThemeToggle = document.getElementById("btnThemeToggle");

    // Modals
    const viewModal = document.getElementById("viewModal");
    const noticeFormModal = document.getElementById("noticeFormModal");
    const deleteModal = document.getElementById("deleteModal");
    const noticeForm = document.getElementById("noticeForm");
    const formModalTitle = document.getElementById("formModalTitle");
    const noticeIdInput = document.getElementById("noticeId");

    // View Modal fields
    const viewTitle = document.getElementById("viewTitle");
    const viewAuthorByline = document.getElementById("viewAuthorByline");
    const viewDate = document.getElementById("viewDate");
    const viewExpiryWrap = document.getElementById("viewExpiryWrap");
    const viewExpiry = document.getElementById("viewExpiry");
    const viewContent = document.getElementById("viewContent");
    const viewBadges = document.getElementById("viewBadges");
    const viewAdminActions = document.getElementById("viewAdminActions");
    const viewBtnEdit = document.getElementById("viewBtnEdit");
    const viewBtnDelete = document.getElementById("viewBtnDelete");

    // Delete Modal fields
    const deleteNoticeTitle = document.getElementById("deleteNoticeTitle");
    const btnConfirmDelete = document.getElementById("btnConfirmDelete");

    // ----------------------------------------------------
    // Toast Notification
    // ----------------------------------------------------
    function showToast(message, type = "success") {
        const toastContainer = document.getElementById("toastContainer");
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transition = "opacity 0.2s ease";
            setTimeout(() => toast.remove(), 200);
        }, 3000);
    }

    // ----------------------------------------------------
    // API Data Fetching
    // ----------------------------------------------------
    async function loadData() {
        await Promise.all([fetchCategories(), fetchStats(), fetchNotices()]);
    }

    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.success) {
                statTotal.textContent = data.stats.total;
                statUrgent.textContent = data.stats.urgent;
                statPinned.textContent = data.stats.pinned;
                statCategories.textContent = data.stats.categories_count;
            }
        } catch (err) {
            console.error("Failed to load statistics:", err);
        }
    }

    async function fetchCategories() {
        try {
            const res = await fetch("/api/categories");
            const data = await res.json();
            if (data.success) {
                renderCategoryTabs(data.categories);
            }
        } catch (err) {
            console.error("Failed to load categories:", err);
        }
    }

    function renderCategoryTabs(categories) {
        categoryTabsContainer.innerHTML = `
            <button class="tab-button ${state.activeCategory === 'all' ? 'active' : ''}" data-category="all">
                All Notices
            </button>
        `;
        categories.forEach(cat => {
            const btn = document.createElement("button");
            btn.className = `tab-button ${state.activeCategory === cat ? 'active' : ''}`;
            btn.setAttribute("data-category", cat);
            btn.textContent = cat;
            categoryTabsContainer.appendChild(btn);
        });

        categoryTabsContainer.querySelectorAll(".tab-button").forEach(btn => {
            btn.addEventListener("click", () => {
                categoryTabsContainer.querySelectorAll(".tab-button").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                state.activeCategory = btn.getAttribute("data-category");
                fetchNotices();
            });
        });
    }

    async function fetchNotices() {
        noticesContainer.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading notices...</p>
            </div>
        `;

        try {
            const url = new URL("/api/notices", window.location.origin);
            url.searchParams.set("sort_by", state.sortBy);
            url.searchParams.set("category", state.activeCategory);
            if (state.searchQuery) {
                url.searchParams.set("search", state.searchQuery);
            }

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                state.notices = data.notices;
                resultsCount.textContent = `${data.notices.length} notice${data.notices.length === 1 ? '' : 's'}`;
                renderNotices(data.notices);
                updateBanner(data.notices);
            } else {
                noticesContainer.innerHTML = `<div class="empty-state">Error: ${data.error}</div>`;
            }
        } catch (err) {
            console.error("Failed to load notices:", err);
            noticesContainer.innerHTML = `<div class="empty-state">Unable to load notice feed.</div>`;
        }
    }

    // ----------------------------------------------------
    // Render Notices Feed
    // ----------------------------------------------------
    function renderNotices(notices) {
        if (!notices || notices.length === 0) {
            noticesContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No notices found</h3>
                    <p>There are no announcements currently matching this filter.</p>
                </div>
            `;
            return;
        }

        noticesContainer.innerHTML = "";

        notices.forEach(notice => {
            const card = document.createElement("article");
            card.className = `notice-card ${notice.is_pinned ? 'pinned' : ''}`;
            card.setAttribute("data-id", notice.id);

            let priorityBadge = "";
            if (notice.priority === "Urgent") {
                priorityBadge = `<span class="badge badge-urgent">Urgent</span>`;
            } else if (notice.priority === "High") {
                priorityBadge = `<span class="badge badge-high">High Priority</span>`;
            }

            const pinnedBadge = notice.is_pinned ? `
                <span class="badge-pinned">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                    </svg>
                    Pinned
                </span>
            ` : "";

            let adminBar = "";
            if (state.adminMode) {
                adminBar = `
                    <div class="card-admin-row" onclick="event.stopPropagation()">
                        <button class="btn btn-outline btn-xs btn-card-edit" data-id="${notice.id}">Edit</button>
                        <button class="btn btn-outline-danger btn-xs btn-card-delete" data-id="${notice.id}">Delete</button>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="card-badges">
                    <span class="badge badge-cat">${escapeHtml(notice.category)}</span>
                    ${priorityBadge}
                    ${pinnedBadge}
                </div>
                <h3 class="card-title">${escapeHtml(notice.title)}</h3>
                <p class="card-summary">${escapeHtml(notice.content)}</p>
                <div class="card-byline">
                    <span class="card-author">${escapeHtml(notice.author)}</span>
                    <time class="card-date">${formatDate(notice.created_at)}</time>
                </div>
                ${adminBar}
            `;

            card.addEventListener("click", () => openViewModal(notice));
            noticesContainer.appendChild(card);
        });

        // Admin Edit/Delete listeners
        if (state.adminMode) {
            noticesContainer.querySelectorAll(".btn-card-edit").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    const id = parseInt(btn.getAttribute("data-id"));
                    const n = state.notices.find(item => item.id === id);
                    if (n) openEditModal(n);
                });
            });

            noticesContainer.querySelectorAll(".btn-card-delete").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    const id = parseInt(btn.getAttribute("data-id"));
                    const n = state.notices.find(item => item.id === id);
                    if (n) openDeleteModal(n);
                });
            });
        }
    }

    // ----------------------------------------------------
    // Announcement Banner
    // ----------------------------------------------------
    function updateBanner(notices) {
        const urgent = notices.find(n => n.priority === "Urgent");
        if (urgent && !sessionStorage.getItem("dismissed_urgent_" + urgent.id)) {
            currentBannerNotice = urgent;
            bannerText.textContent = `${urgent.title} — ${urgent.author}`;
            urgentBanner.style.display = "block";
        } else {
            urgentBanner.style.display = "none";
        }
    }

    btnBannerClose.addEventListener("click", () => {
        urgentBanner.style.display = "none";
        if (currentBannerNotice) {
            sessionStorage.setItem("dismissed_urgent_" + currentBannerNotice.id, "true");
        }
    });

    btnBannerView.addEventListener("click", () => {
        if (currentBannerNotice) {
            openViewModal(currentBannerNotice);
        }
    });

    // ----------------------------------------------------
    // View Modal
    // ----------------------------------------------------
    function openViewModal(notice) {
        viewTitle.textContent = notice.title;
        viewAuthorByline.innerHTML = `Posted by <strong>${escapeHtml(notice.author)}</strong>`;
        viewDate.textContent = formatDate(notice.created_at);

        if (notice.expires_at) {
            viewExpiryWrap.style.display = "inline";
            viewExpiry.textContent = notice.expires_at;
        } else {
            viewExpiryWrap.style.display = "none";
        }

        viewContent.textContent = notice.content;

        let badges = `<span class="badge badge-cat">${escapeHtml(notice.category)}</span>`;
        if (notice.priority === "Urgent") badges += ` <span class="badge badge-urgent">Urgent</span>`;
        else if (notice.priority === "High") badges += ` <span class="badge badge-high">High Priority</span>`;
        if (notice.is_pinned) badges += ` <span class="badge badge-cat">📌 Pinned</span>`;
        viewBadges.innerHTML = badges;

        if (state.adminMode) {
            viewAdminActions.style.display = "flex";
            viewBtnEdit.onclick = () => {
                closeModal(viewModal);
                openEditModal(notice);
            };
            viewBtnDelete.onclick = () => {
                closeModal(viewModal);
                openDeleteModal(notice);
            };
        } else {
            viewAdminActions.style.display = "none";
        }

        openModal(viewModal);
    }

    // ----------------------------------------------------
    // Create / Edit Modal
    // ----------------------------------------------------
    function openPostModal() {
        formModalTitle.textContent = "New Notice";
        noticeForm.reset();
        noticeIdInput.value = "";
        document.getElementById("noticeAuthor").value = "Admin Office";
        document.getElementById("noticePriority").value = "Normal";
        openModal(noticeFormModal);
    }

    function openEditModal(notice) {
        formModalTitle.textContent = `Edit Notice #${notice.id}`;
        noticeIdInput.value = notice.id;
        document.getElementById("noticeTitle").value = notice.title;
        document.getElementById("noticeCategory").value = notice.category;
        document.getElementById("noticePriority").value = notice.priority || "Normal";
        document.getElementById("noticeAuthor").value = notice.author;
        document.getElementById("noticeExpiresAt").value = notice.expires_at || "";
        document.getElementById("noticeIsPinned").checked = Boolean(notice.is_pinned);
        document.getElementById("noticeContent").value = notice.content;
        openModal(noticeFormModal);
    }

    noticeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = noticeIdInput.value;
        const isEdit = Boolean(id);

        const payload = {
            title: document.getElementById("noticeTitle").value.trim(),
            category: document.getElementById("noticeCategory").value.trim(),
            priority: document.getElementById("noticePriority").value,
            author: document.getElementById("noticeAuthor").value.trim(),
            expires_at: document.getElementById("noticeExpiresAt").value || null,
            is_pinned: document.getElementById("noticeIsPinned").checked ? 1 : 0,
            content: document.getElementById("noticeContent").value.trim()
        };

        const submitBtn = document.getElementById("btnSubmitNotice");
        submitBtn.disabled = true;
        submitBtn.textContent = "Saving...";

        try {
            const url = isEdit ? `/api/notices/${id}` : "/api/notices";
            const method = isEdit ? "PUT" : "POST";

            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (data.success) {
                showToast(isEdit ? "Notice updated successfully" : "Notice published successfully");
                closeModal(noticeFormModal);
                await loadData();
            } else {
                showToast(data.error || "Failed to save notice", "error");
            }
        } catch (err) {
            console.error("Save notice error:", err);
            showToast("Server connection error", "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Publish Notice";
        }
    });

    // ----------------------------------------------------
    // Delete Modal
    // ----------------------------------------------------
    function openDeleteModal(notice) {
        state.currentNoticeToDelete = notice;
        deleteNoticeTitle.textContent = `"${notice.title}"`;
        openModal(deleteModal);
    }

    btnConfirmDelete.addEventListener("click", async () => {
        if (!state.currentNoticeToDelete) return;
        const id = state.currentNoticeToDelete.id;

        btnConfirmDelete.disabled = true;
        btnConfirmDelete.textContent = "Deleting...";

        try {
            const res = await fetch(`/api/notices/${id}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                showToast("Notice deleted");
                closeModal(deleteModal);
                state.currentNoticeToDelete = null;
                await loadData();
            } else {
                showToast(data.error || "Delete failed", "error");
            }
        } catch (err) {
            console.error("Delete notice error:", err);
            showToast("Server error", "error");
        } finally {
            btnConfirmDelete.disabled = false;
            btnConfirmDelete.textContent = "Delete Notice";
        }
    });

    // ----------------------------------------------------
    // Modal Helpers
    // ----------------------------------------------------
    function openModal(modal) {
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";
    }

    function closeModal(modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
    }

    document.querySelectorAll("[data-close-modal]").forEach(btn => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".modal-backdrop");
            if (modal) closeModal(modal);
        });
    });

    window.addEventListener("click", (e) => {
        if (e.target.classList.contains("modal-backdrop")) {
            closeModal(e.target);
        }
    });

    // ----------------------------------------------------
    // Controls: Search, Sort, Admin, Theme
    // ----------------------------------------------------
    let searchDebounceTimer = null;
    searchInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        searchClearBtn.style.display = val ? "block" : "none";
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            state.searchQuery = val;
            fetchNotices();
        }, 200);
    });

    searchClearBtn.addEventListener("click", () => {
        searchInput.value = "";
        searchClearBtn.style.display = "none";
        state.searchQuery = "";
        fetchNotices();
    });

    sortSelect.addEventListener("change", (e) => {
        state.sortBy = e.target.value;
        fetchNotices();
    });

    btnRefresh.addEventListener("click", () => {
        loadData();
        showToast("Board refreshed");
    });

    // Admin Toggle
    adminToggleCheckbox.addEventListener("change", (e) => {
        state.adminMode = e.target.checked;
        if (state.adminMode) {
            adminLabelText.textContent = "Admin Active";
            btnOpenPostModal.style.display = "inline-flex";
            showToast("Admin tools enabled");
        } else {
            adminLabelText.textContent = "Admin Access";
            btnOpenPostModal.style.display = "none";
        }
        renderNotices(state.notices);
    });

    btnOpenPostModal.addEventListener("click", openPostModal);

    // Theme toggle
    btnThemeToggle.addEventListener("click", () => {
        document.body.classList.toggle("theme-dark");
        const isDark = document.body.classList.contains("theme-dark");
        localStorage.setItem("dnb-theme", isDark ? "dark" : "light");
    });

    if (localStorage.getItem("dnb-theme") === "dark") {
        document.body.classList.add("theme-dark");
    }

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll(".modal-backdrop").forEach(m => closeModal(m));
        }
    });

    function formatDate(dateStr) {
        if (!dateStr) return "-";
        try {
            const d = new Date(dateStr.replace(" ", "T"));
            return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
        } catch {
            return dateStr;
        }
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial Load
    loadData();
});
