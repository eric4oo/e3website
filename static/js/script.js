// E-commerce functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('PropsWorks app loaded');
    updateCartCount();
});

// Add to cart function
function addToCart(serviceId, serviceName) {
    const quantity = 1;
    const options = {};
    
    fetch('/services/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            service_id: serviceId,
            quantity: quantity,
            options: options
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
            updateCartCount();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'error');
    });
}

// Remove from cart function
function removeFromCart(itemId) {
    if (confirm('Remove item from cart?')) {
        fetch(`/services/remove-from-cart/${itemId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.textContent = message;
    notification.className = `notification show ${type}`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Update cart count in navbar
function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (!cartCount) return;
    
    // Get cart count from localStorage or API
    const count = localStorage.getItem('cart_count') || '0';
    cartCount.textContent = count;
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
