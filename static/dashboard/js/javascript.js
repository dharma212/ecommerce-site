// ================================
// Toast Messages
document.addEventListener("DOMContentLoaded", function () {
  const toastElList = document.querySelectorAll(".toast");
  toastElList.forEach((toastEl) => {
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  });
});

// ================================
// Download Excel
$(document).ready(function () {
  $("#download-excel").on("click", function () {
    window.location.href = "/product/download-excel/";
  });
});

// ================================
// Profile Dropdown
const profileBtn = document.getElementById("profileBtn");
const profileCard = document.getElementById("profileCard");

if (profileBtn && profileCard) {
  profileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    profileCard.style.display =
      profileCard.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", () => {
    profileCard.style.display = "none";
  });
}

// ================================
// Reusable DataTable Initializer (IMPORTANT)
function initDataTable(tableId, options = {}) {
  if (
    $(tableId).length &&
    !$.fn.DataTable.isDataTable(tableId)
  ) {
    $(tableId).DataTable({
      pageLength: 10,
      lengthMenu: [5, 10, 25, 50],
      ordering: true,
      searching: true,
      responsive: true,
      ...options
    });
  }
}

// ================================
// Orders Table
$(document).ready(function () {
  initDataTable("#orderTable", {
    columnDefs: [{ orderable: false, targets: -1 }]
  });
});

// ================================
// Wishlist Table
$(document).ready(function () {
  initDataTable("#wishlistTable", {
    order: [[5, "desc"]],
    columnDefs: [{ orderable: false, targets: [0] }]
  });
});

// ================================
// Cart Table
$(document).ready(function () {
  initDataTable("#cartTable", {
    order: [[7, "desc"]],
    columnDefs: [{ orderable: false, targets: [0] }]
  });
});

// ================================
$(document).ready(function () {
  initDataTable("#userTable", {
    autoWidth: false,
    responsive: false,
    columnDefs: [
      { orderable: false, targets: [8] }, // Action column index
      { width: "50px", targets: [8] }
    ]
  });
});

// ================================
// Category Table
$(document).ready(function () {
  initDataTable("#categoryTable", {
    columnDefs: [{ orderable: false, targets: [1, 4] }]
  });
});

// ================================
// Sub Category Table
$(document).ready(function () {
  initDataTable("#subCategoryTable", {
    columnDefs: [{ orderable: false, targets: [4] }]
  });
});

// ================================
// Product Table
$(document).ready(function () {
  initDataTable("#productTable", {
    order: [[8, "desc"]],
    columnDefs: [{ orderable: false, targets: -1 }]
  });
});

// ================================
// Banner Table
$(document).ready(function () {
  initDataTable("#bannerTable", {
    columnDefs: [{ orderable: false, targets: -1 }]
  });
});

