
document.addEventListener('DOMContentLoaded', function() {
       // Obtiene la URL actual
       var currentUrl = window.location.href;

       if (currentUrl.includes('/add/')) {  
          var inline_mod = document.querySelector('.inline-mod');
        
          if (inline_mod) {
            inline_mod.style.display= "none";
        } 
    }
       
});






