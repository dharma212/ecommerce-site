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
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('simpleProfileToggle');
    const menu = document.getElementById('simpleMenu');

    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('show');
        const arrow = toggleBtn.querySelector('.arrow');
        arrow.style.transform = menu.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    });

    document.addEventListener('click', () => {
        menu.classList.remove('show');
        toggleBtn.querySelector('.arrow').style.transform = 'rotate(0deg)';
    });
});
