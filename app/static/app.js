const API_BASE_URL = "http://127.0.0.1:8000";

function getCart() {
  const cart = localStorage.getItem("cart");
  return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
}

function clearCart() {
  localStorage.removeItem("cart");
}

function addToCart(product) {
  const cart = getCart();

  const existingItem = cart.find(item => item.id === product.id);

  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: Number(product.price),
      image_url: product.image_url,
      quantity: 1
    });
  }

  saveCart(cart);
  alert(`${product.name} added to cart`);
}

async function loadProducts() {
  const container = document.getElementById("products-container");
  if (!container) return;

  try {
    const response = await fetch(`${API_BASE_URL}/products`);
    const products = await response.json();

    if (!products.length) {
      container.innerHTML = "<p>No products available.</p>";
      return;
    }

    container.innerHTML = products.map(product => `
      <div class="product-card">
        <img src="${product.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}" alt="${product.name}" />
        <h3>${product.name}</h3>
        <p>${product.description || ""}</p>
        <p class="price">$${Number(product.price).toFixed(2)}</p>
        <p>Stock: ${product.stock}</p>
        <button class="button" onclick='handleAddToCart(${JSON.stringify(product)})'>
          Add to Cart
        </button>
      </div>
    `).join("");

  } catch (error) {
    console.error("Error loading products:", error);
    container.innerHTML = "<p>Failed to load products.</p>";
  }
}

function handleAddToCart(product) {
  addToCart(product);
}

function loadCart() {
  const container = document.getElementById("cart-container");
  const totalContainer = document.getElementById("cart-total");

  if (!container || !totalContainer) return;

  const cart = getCart();

  if (cart.length === 0) {
    container.innerHTML = "<p>Your cart is empty.</p>";
    totalContainer.innerHTML = "";
    return;
  }

  let total = 0;

  container.innerHTML = cart.map(item => {
    const itemTotal = item.price * item.quantity;
    total += itemTotal;

    return `
      <div class="cart-item">
        <h3>${item.name}</h3>
        <p>Price: $${item.price.toFixed(2)}</p>
        <p>Quantity: ${item.quantity}</p>
        <p>Item Total: $${itemTotal.toFixed(2)}</p>
        <button class="button" onclick="removeFromCart(${item.id})">Remove</button>
      </div>
    `;
  }).join("");

  totalContainer.innerHTML = `Total: $${total.toFixed(2)}`;
}

function removeFromCart(productId) {
  let cart = getCart();
  cart = cart.filter(item => item.id !== productId);
  saveCart(cart);
  loadCart();
}

function loadCheckoutSummary() {
  const summaryContainer = document.getElementById("checkout-cart-summary");
  if (!summaryContainer) return;

  const cart = getCart();

  if (cart.length === 0) {
    summaryContainer.innerHTML = "<p>Your cart is empty. Please add items before checkout.</p>";
    return;
  }

  let total = 0;

  summaryContainer.innerHTML = `
    <h3>Order Summary</h3>
    ${cart.map(item => {
      const itemTotal = item.price * item.quantity;
      total += itemTotal;
      return `
        <p>${item.name} — Quantity: ${item.quantity} — $${itemTotal.toFixed(2)}</p>
      `;
    }).join("")}
    <p><strong>Total: $${total.toFixed(2)}</strong></p>
  `;
}

async function handleCheckoutSubmit(event) {
  event.preventDefault();

  const messageContainer = document.getElementById("checkout-message");
  const cart = getCart();

  if (cart.length === 0) {
    messageContainer.innerHTML = `<p class="error-message">Your cart is empty.</p>`;
    return;
  }

  const customerName = document.getElementById("customer-name").value.trim();
  const customerEmail = document.getElementById("customer-email").value.trim();

  const payload = {
    customer_name: customerName,
    customer_email: customerEmail,
    items: cart.map(item => ({
      product_id: item.id,
      quantity: item.quantity
    }))
  };

  try {
    const response = await fetch(`${API_BASE_URL}/orders`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      messageContainer.innerHTML = `
        <p class="error-message">${data.detail || "Failed to place order."}</p>
      `;
      return;
    }

    clearCart();

    messageContainer.innerHTML = `
      <p class="success-message">
        Order placed successfully. Order ID: ${data.id}. Total: $${Number(data.total_amount).toFixed(2)}
      </p>
    `;

    const form = document.getElementById("checkout-form");
    form.reset();

    const summaryContainer = document.getElementById("checkout-cart-summary");
    summaryContainer.innerHTML = "<p>Your cart has been cleared.</p>";

  } catch (error) {
    console.error("Checkout error:", error);
    messageContainer.innerHTML = `
      <p class="error-message">An unexpected error occurred during checkout.</p>
    `;
  }
}

function initializeCheckoutForm() {
  const form = document.getElementById("checkout-form");
  if (!form) return;

  form.addEventListener("submit", handleCheckoutSubmit);
}

document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  loadCart();
  loadCheckoutSummary();
  initializeCheckoutForm();
});