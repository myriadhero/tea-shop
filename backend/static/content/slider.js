var swiper = new Swiper(".mySwiper", {
  
    slidesPerView: 2,
    spaceBetween:30,
    // Responsive breakpoints
    breakpoints: {
        // touch devices
        769: {
          slidesPerView: 3,
        },
        // desktop
        1024: {
          slidesPerView: 4,
        },
        // widescreen
        1216: {
          slidesPerView: 5,
        },
      },
  
   
    

    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
   
});