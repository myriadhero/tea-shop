let items = document.querySelectorAll('.carousel .carousel-item')
        var minPerSlide = 1  
    
        if(window.matchMedia("(max-width:767px)").matches) {
            minPerSlide = 1    
        }
        if(window.matchMedia("(min-width:768px) and (max-width:991px)").matches) {
            minPerSlide = 3
        }
        if(window.matchMedia("(min-width:992px)").matches){
            minPerSlide = 4
           
        }

        items.forEach((el) => {
            let next = el.nextElementSibling
            for (var i=1; i<minPerSlide&(next!=null); i++) {
           
                let cloneChild = next.cloneNode(true)
                el.appendChild(cloneChild.children[0])
                next = next.nextElementSibling
          
            }
        })

        
        
        
        
		