let items = document.querySelectorAll('.carousel .carousel-item')
    
        if(window.matchMedia("(max-width:767px)").matches) {
        }
        if(window.matchMedia("(min-width:768px) and (max-width:991px)").matches) {
            items.forEach((el) => {
                const minPerSlide = 3
                let next = el.nextElementSibling
                for (var i=1; i<minPerSlide&(next!=null); i++) {
               
                    let cloneChild = next.cloneNode(true)
                    el.appendChild(cloneChild.children[0])
                    next = next.nextElementSibling
              
                }
            })
        }
        if(window.matchMedia("(min-width:992px)").matches){
            items.forEach((el) => {
                const minPerSlide = 4
                let next = el.nextElementSibling
                for (var i=1; i<minPerSlide&(next!=null); i++) {
               
                    let cloneChild = next.cloneNode(true)
                    el.appendChild(cloneChild.children[0])
                    next = next.nextElementSibling
              
                }
            })
        }

        
        
        
