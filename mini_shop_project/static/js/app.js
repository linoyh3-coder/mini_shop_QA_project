let cart = [];

// Trigger product load on window boot
document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
});

function fetchProducts() {
    axios.get('/api/products')
        .then(response => {
            const products = response.data;
            const container = document.getElementById('products-list');
            container.innerHTML = '';
            
            products.forEach(product => {
                container.innerHTML += `
                    <div class="product-card">
                        <div class="product-info">
                            <strong>${product.name}</strong>
                            <span>מחיר: ${product.price} ₪</span>
                            <br><small>עמודת מלאי בבסיס הנתונים: ${product.stock}</small>
                        </div>
                        <button class="btn btn-success" onclick="addToCart(${product.id}, '${product.name}', ${product.price})">📥 הוסף לסל</button>
                    </div>
                `;
            });
        })
        .catch(error => console.error("שגיאה בטעינת נתוני קטלוג מהשרת:", error));
}

function addToCart(id, name, price) {
    cart.push({ id, name, price, quantity: 1 });
    updateCartUI();
}

function updateCartUI() {
    const cartList = document.getElementById('cart-list');
    const totalSpan = document.getElementById('cart-total');
    
    if (cart.length === 0) {
        cartList.innerHTML = '<li class="empty-msg">העגלה שלך ריקה לחלוטין</li>';
        totalSpan.innerText = "0.00";
        return;
    }
    
    cartList.innerHTML = '';
    let total = 0;
    
    cart.forEach(item => {
        cartList.innerHTML += `<li><span>${item.name}</span> <strong>${item.price} ₪</strong></li>`;
        total += item.price;
    });
    
    totalSpan.innerText = total.toFixed(2);
}

// 🐛 INTENTIONAL BUG 3: The function cleans up the frontend model but skips calling the server-side Checkout API entirely!
function clearCart() {
    alert("🎉 הזמנתך בוצעה לכאורה! (בדוק האם המלאי ב-DB באמת השתנה...)");
    cart = [];
    updateCartUI();
    fetchProducts();
}
