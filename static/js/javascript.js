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

// document.addEventListener('DOMContentLoaded', () => {
//     const toggleBtn = document.getElementById('simpleProfileToggle');
//     const menu = document.getElementById('simpleMenu');

//     toggleBtn.addEventListener('click', (e) => {
//         e.stopPropagation();
//         menu.classList.toggle('show');
//         const arrow = toggleBtn.querySelector('.arrow');
//         arrow.style.transform = menu.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
//     });

//     document.addEventListener('click', () => {
//         menu.classList.remove('show');
//         toggleBtn.querySelector('.arrow').style.transform = 'rotate(0deg)';
//     });
// });


const deliverBtn = document.getElementById('deliver-here-btn');

if (deliverBtn) {
    deliverBtn.addEventListener('click', function () {
        document.getElementById('address-section')?.classList.add('d-none');
        document.getElementById('address-header')?.classList.add('d-none');
        document.getElementById('address-collapsed')?.classList.remove('d-none');
        document.getElementById('summary-header')?.classList.add('bg-primary', 'text-white');
        document.getElementById('summary-section')?.classList.remove('d-none');
    });
}
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


document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.querySelector(".navbar");

  function handleScroll() {
    if (window.scrollY > 30) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");  
    }
  }

  handleScroll(); // run on load
  window.addEventListener("scroll", handleScroll);
});



// ===============================
// Footer JS 
// ===============================
let lastScrollTop = 0;
const bottomNav = document.getElementById("bottomNav");

window.addEventListener("scroll", function () {
    let currentScroll = window.pageYOffset || document.documentElement.scrollTop;

    if (currentScroll > lastScrollTop) {
        // Scrolling DOWN
        bottomNav.classList.add("hide");
    } else {
        // Scrolling UP
        bottomNav.classList.remove("hide");
    }

    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
});


// ================================
// Order Details Page JS
// ================================
document.addEventListener("DOMContentLoaded", function () {

    const otherRadio = document.getElementById('triggerOther');
    const allRadios = document.querySelectorAll('input[name="reason"]');
    const textInput = document.getElementById('customReasonBox');
    const form = document.getElementById('cancellationForm');

    // 🚨 SAFETY CHECK
    if (!form || !otherRadio || !textInput) {
        return; // stop script if elements not on this page
    }

    allRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (otherRadio.checked) {
                textInput.style.display = "block";
                textInput.setAttribute('required', 'true');
            } else {
                textInput.style.display = "none";
                textInput.removeAttribute('required');
                textInput.value = "";
            }
        });
    });

    form.onsubmit = function () {
        const selected = document.querySelector('input[name="reason"]:checked');
        if (!selected) {
            alert("Please select a reason");
            return false;
        }
        return true;
    };
});
