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


document.getElementById('deliver-here-btn').addEventListener('click', function () {
        document.getElementById('address-section').classList.add('d-none');
        document.getElementById('address-header').classList.add('d-none');
        document.getElementById('address-collapsed').classList.remove('d-none');
        document.getElementById('summary-header').classList.add('bg-primary', 'text-white');
        document.getElementById('summary-section').classList.remove('d-none');
    });

 function scrollThumbs(direction) {
        const wrapper = document.getElementById('thumbWrapper');
        if (direction === 'up') wrapper.scrollTop -= 80;
        else wrapper.scrollTop += 80;
    }
       const slider = document.getElementById('imageSlider');

    const dots = document.querySelectorAll('.dot');



    if(slider) {

        slider.addEventListener('scroll', () => {

            const index = Math.round(slider.scrollLeft / slider.offsetWidth);

            dots.forEach((dot, i) => {

                dot.classList.toggle('active', i === index);

            });

        });

    }

  
  function runCheckout(e) {
    e.preventDefault();
    const loader = document.getElementById("checkout-loader");
    const successOverlay = document.getElementById("success-overlay");
    const form = e.target;

    loader.classList.remove("d-none");

    setTimeout(() => {
      loader.classList.add("d-none"); 
      successOverlay.classList.remove("d-none"); 

      setTimeout(() => {
        form.submit();
      }, 2000);
    }, 2500);
  }

  function updateProgressLine() {
    const greenLine = document.getElementById("green-line");
    if (!greenLine) return;
    const completed = document.querySelectorAll(".status-step.completed");
    const last = completed[completed.length - 1];
    greenLine.style.height = last.offsetTop + 10 + "px";
  }
  window.addEventListener("load", updateProgressLine);


