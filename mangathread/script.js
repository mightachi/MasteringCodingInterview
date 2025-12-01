// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Cart Functionality
let cartCount = 0;
const cartCountElement = document.querySelector('.cart-count');

// Add to cart functionality
document.querySelectorAll('.cta-button, .btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        cartCount++;
        cartCountElement.textContent = cartCount;
        
        // Cart animation
        cartCountElement.style.transform = 'scale(1.5)';
        cartCountElement.style.background = '#4ecdc4';
        setTimeout(() => {
            cartCountElement.style.transform = 'scale(1)';
            cartCountElement.style.background = '#ff6b6b';
        }, 300);
        
        // Show notification
        showNotification('Added to cart!');
    });
});

// Notification system
function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 50px;
        font-weight: 600;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 2000);
}

// Navbar scroll effect
let lastScrollY = window.scrollY;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    
    if (currentScrollY > 100) {
        navbar.style.background = 'rgba(0, 0, 0, 0.95)';
        navbar.style.backdropFilter = 'blur(20px)';
    } else {
        navbar.style.background = 'rgba(0, 0, 0, 0.9)';
        navbar.style.backdropFilter = 'blur(10px)';
    }
    
    // Hide/show navbar on scroll
    if (currentScrollY > lastScrollY && currentScrollY > 200) {
        navbar.style.transform = 'translateY(-100%)';
    } else {
        navbar.style.transform = 'translateY(0)';
    }
    
    lastScrollY = currentScrollY;
});

// Video placeholder click handler
const videoPlaceholder = document.querySelector('.video-placeholder');
if (videoPlaceholder) {
    videoPlaceholder.addEventListener('click', () => {
        // Simulate video play
        videoPlaceholder.innerHTML = '<i class="fas fa-pause"></i>';
        videoPlaceholder.style.background = 'rgba(255, 107, 107, 0.3)';
        
        // Reset after 3 seconds
        setTimeout(() => {
            videoPlaceholder.innerHTML = '<i class="fas fa-play"></i>';
            videoPlaceholder.style.background = 'rgba(255, 255, 255, 0.1)';
        }, 3000);
    });
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.collection-content, .summer-item, .customer-reviews').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(50px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// Parallax effect for hero section
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Search functionality
const searchIcon = document.querySelector('.nav-icons .fa-search');
if (searchIcon) {
    searchIcon.addEventListener('click', () => {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search anime collections...';
        searchInput.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 10px 20px;
            border: 2px solid #ff6b6b;
            border-radius: 25px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            outline: none;
            z-index: 1000;
        `;
        
        document.body.appendChild(searchInput);
        searchInput.focus();
        
        searchInput.addEventListener('blur', () => {
            document.body.removeChild(searchInput);
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const searchTerm = searchInput.value.toLowerCase();
                searchProducts(searchTerm);
                document.body.removeChild(searchInput);
            }
        });
    });
}

// Search products function
function searchProducts(term) {
    const products = [
        'Naruto Collection',
        'One Piece Collection', 
        'Dragon Ball Collection',
        'Attack on Titan Collection',
        'Demon Slayer Collection',
        'My Hero Academia Collection'
    ];
    
    const results = products.filter(product => 
        product.toLowerCase().includes(term)
    );
    
    if (results.length > 0) {
        showNotification(`Found ${results.length} products: ${results.join(', ')}`);
    } else {
        showNotification('No products found. Try different keywords.');
    }
}

// User icon functionality
const userIcon = document.querySelector('.nav-icons .fa-user');
if (userIcon) {
    userIcon.addEventListener('click', () => {
        showNotification('Login/Register feature coming soon!');
    });
}

// Cart icon functionality
const cartIcon = document.querySelector('.cart-icon');
if (cartIcon) {
    cartIcon.addEventListener('click', () => {
        if (cartCount === 0) {
            showNotification('Your cart is empty. Add some anime gear!');
        } else {
            showNotification(`You have ${cartCount} items in your cart`);
        }
    });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .navbar {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);

// Lazy loading for images
const images = document.querySelectorAll('img');
const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.style.opacity = '1';
            img.style.transform = 'scale(1)';
        }
    });
});

images.forEach(img => {
    img.style.opacity = '0';
    img.style.transform = 'scale(0.9)';
    img.style.transition = 'all 0.6s ease';
    imageObserver.observe(img);
});

// Mobile menu toggle (for future implementation)
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
}

// Add touch support for mobile
let touchStartY = 0;
let touchEndY = 0;

document.addEventListener('touchstart', e => {
    touchStartY = e.changedTouches[0].screenY;
});

document.addEventListener('touchend', e => {
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartY - touchEndY;
    
    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe up - show navbar
            navbar.style.transform = 'translateY(0)';
        } else {
            // Swipe down - hide navbar
            if (window.scrollY > 200) {
                navbar.style.transform = 'translateY(-100%)';
            }
        }
    }
}

// Performance optimization
let ticking = false;

function updateOnScroll() {
    // Throttle scroll events
    if (!ticking) {
        requestAnimationFrame(() => {
            // Scroll-based animations here
            ticking = false;
        });
        ticking = true;
    }
}

window.addEventListener('scroll', updateOnScroll);