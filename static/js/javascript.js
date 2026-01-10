 const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  const cancelMenu = document.getElementById("cancle-menu");

  // Open menu
  menuBtn.addEventListener("click", () => {
    mobileMenu.classList.add("active");
  });

  // ❌ Close menu when cancel button clicked
  cancelMenu.addEventListener("click", () => {
    mobileMenu.classList.remove("active");
  });

  // Close when clicking outside
  document.addEventListener("click", (e) => {
    if (
      !mobileMenu.contains(e.target) &&
      !menuBtn.contains(e.target)
    ) {
      mobileMenu.classList.remove("active");
    }
  });
document.addEventListener("DOMContentLoaded", function () {

  /* ===== MOBILE CATEGORY DROPDOWN ===== */
  const categories = document.querySelectorAll(".category-item");
  const dropdowns = document.querySelectorAll(".dropdown-list");

  categories.forEach(cat => {
    cat.addEventListener("click", () => {
      const target = cat.getAttribute("data-target");

      // reset all
      categories.forEach(c => c.classList.remove("active"));
      dropdowns.forEach(d => d.classList.remove("active"));

      // activate selected
      cat.classList.add("active");
      const targetDropdown = document.getElementById(target);
      if (targetDropdown) {
        targetDropdown.classList.add("active");
      }
    });
  });

});

const swiper = new Swiper(".bannerSwiper", {
    loop: true,
    autoplay: { 
      delay: 3000,
      disableOnInteraction: false,
    },
    pagination: {
      el: ".swiper-pagination",
        clickable: true,
      },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
});