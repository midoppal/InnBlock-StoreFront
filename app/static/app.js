const API_BASE_URL = "http://127.0.0.1:8000";




function getProductIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}


async function fetchProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/products/${productId}`);

  if (!response.ok) {
    throw new Error("Product not found");
  }

  return await response.json();
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

    container.innerHTML = "";

    products.forEach(product => {
      const card = document.createElement("div");
      card.className = "product-card";

      card.innerHTML = `
        <img src="${product.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}" alt="${product.name}" />
        <h3>${product.name}</h3>
        <p>${product.description || ""}</p>
        <p class="price">$${Number(product.price).toFixed(2)}</p>
        <p>Stock: ${product.stock}</p>
        <a class="secondary-link" href="/static/product-detail.html?id=${product.id}">View Details</a>
      `;

      const button = document.createElement("button");
      button.className = "button";
      button.textContent = "Add to Cart";
      button.addEventListener("click", () => addToCart(product));

      card.appendChild(button);
      container.appendChild(card);
    });

  } catch (error) {
    console.error("Error loading products:", error);
    container.innerHTML = "<p>Failed to load products.</p>";
  }
}

async function loadProductDetail() {
  const container = document.getElementById("product-detail-container");
  if (!container) return;

  const productId = getProductIdFromUrl();

  if (!productId) {
    container.innerHTML = "<p>No product selected.</p>";
    return;
  }

  try {
    const product = await fetchProduct(productId);

    container.innerHTML = `
      <div class="product-detail">
        <img src="${product.image_url || 'https://via.placeholder.com/450x300?text=No+Image'}" alt="${product.name}" />
        <h2>${product.name}</h2>
        <p>${product.description || ""}</p>
        <p class="price">$${Number(product.price).toFixed(2)}</p>
        <p>Stock: ${product.stock}</p>

        <label for="detail-quantity">Quantity</label>
        <input id="detail-quantity" type="number" min="1" max="${product.stock}" value="1" />

        <br /><br />
        <button id="detail-add-button" class="button">Add to Cart</button>
      </div>
    `;

    document.getElementById("detail-add-button").addEventListener("click", () => {
      const quantityInput = document.getElementById("detail-quantity");
      const quantity = Number(quantityInput.value);

      if (!quantity || quantity < 1) {
        alert("Please enter a valid quantity.");
        return;
      }

      addToCart(product, quantity);
    });

  } catch (error) {
    console.error(error);
    container.innerHTML = "<p>Product not found.</p>";
  }
}


async function getOrCreateCartId() {
  let cartId = localStorage.getItem("cart_id");

  if (cartId) {
    return Number(cartId);
  }

  const response = await fetch(`${API_BASE_URL}/cart`, {
    method: "POST"
  });

  const cart = await response.json();
  localStorage.setItem("cart_id", cart.id);

  return cart.id;
}

function clearCartId() {
  localStorage.removeItem("cart_id");
}

async function fetchBackendCart() {
  const cartId = await getOrCreateCartId();

  const response = await fetch(`${API_BASE_URL}/cart/${cartId}`);

  if (!response.ok) {
    clearCartId();
    return await fetchBackendCart();
  }

  return await response.json();
}

async function addToCart(product, quantity = 1) {
  const cartId = await getOrCreateCartId();

  const response = await fetch(`${API_BASE_URL}/cart/${cartId}/items`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      product_id: product.id,
      quantity: quantity
    })
  });

  const data = await response.json();

  if (!response.ok) {
    alert(data.detail || "Failed to add item to cart.");
    return;
  }

  alert(`${product.name} added to cart`);
}

async function loadCart() {
  const container = document.getElementById("cart-container");
  const totalContainer = document.getElementById("cart-total");

  if (!container || !totalContainer) return;

  const cart = await fetchBackendCart();

  if (cart.items.length === 0) {
    container.innerHTML = "<p>Your cart is empty.</p>";
    totalContainer.innerHTML = "";
    return;
  }

  container.innerHTML = "";

  cart.items.forEach(item => {
    const itemDiv = document.createElement("div");
    itemDiv.className = "cart-item";

    itemDiv.innerHTML = `
      <h3>${item.name}</h3>
      <p>Price: $${Number(item.price).toFixed(2)}</p>
      <div class="quantity-controls">
        <button class="button decrease-button">-</button>
        <span>Quantity: ${item.quantity}</span>
        <button class="button increase-button">+</button>
      </div>
      <p>Item Total: $${Number(item.item_total).toFixed(2)}</p>
      <button class="button remove-button">Remove</button>
    `;

    itemDiv.querySelector(".decrease-button").addEventListener("click", async () => {
      await updateCartQuantity(item.product_id, item.quantity - 1);
    });

    itemDiv.querySelector(".increase-button").addEventListener("click", async () => {
      await updateCartQuantity(item.product_id, item.quantity + 1);
    });

    itemDiv.querySelector(".remove-button").addEventListener("click", async () => {
      await removeFromCart(item.product_id);
    });

    container.appendChild(itemDiv);
  });

  totalContainer.innerHTML = `Total: $${Number(cart.total_amount).toFixed(2)}`;
}

async function updateCartQuantity(productId, newQuantity) {
  const cartId = await getOrCreateCartId();

  const response = await fetch(`${API_BASE_URL}/cart/${cartId}/items/${productId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      quantity: newQuantity
    })
  });

  const data = await response.json();

  if (!response.ok) {
    alert(data.detail || "Failed to update cart.");
    return;
  }

  await loadCart();
  await loadCheckoutSummary();
}

async function removeFromCart(productId) {
  const cartId = await getOrCreateCartId();

  const response = await fetch(`${API_BASE_URL}/cart/${cartId}/items/${productId}`, {
    method: "DELETE"
  });

  const data = await response.json();

  if (!response.ok) {
    alert(data.detail || "Failed to remove item.");
    return;
  }

  await loadCart();
  await loadCheckoutSummary();
}

async function clearBackendCart() {
  const cartId = localStorage.getItem("cart_id");

  if (!cartId) return;

  await fetch(`${API_BASE_URL}/cart/${cartId}`, {
    method: "DELETE"
  });

  clearCartId();
}

async function loadCheckoutSummary() {
  const summaryContainer = document.getElementById("checkout-cart-summary");
  if (!summaryContainer) return;

  const cart = await fetchBackendCart();

  if (cart.items.length === 0) {
    summaryContainer.innerHTML = "<p>Your cart is empty. Please add items before checkout.</p>";
    return;
  }

  summaryContainer.innerHTML = `
    <h3>Order Summary</h3>
    ${cart.items.map(item => `
      <p>
        ${item.name} — Quantity: ${item.quantity} —
        $${Number(item.item_total).toFixed(2)}
      </p>
    `).join("")}
    <p><strong>Total: $${Number(cart.total_amount).toFixed(2)}</strong></p>
  `;
}



async function handleCheckoutSubmit(event) {
  event.preventDefault();

  const messageContainer = document.getElementById("checkout-message");

  const cart = await fetchBackendCart();

  if (cart.items.length === 0) {
    messageContainer.innerHTML = `<p class="error-message">Your cart is empty.</p>`;
    return;
  }

  const customerName = document.getElementById("customer-name").value.trim();
  const customerEmail = document.getElementById("customer-email").value.trim();
  const customerPhone = document.getElementById("customer-phone").value.trim();

  const cartId = localStorage.getItem("cart_id");

  if (!cartId) {
    messageContainer.innerHTML = `<p class="error-message">Your cart is empty.</p>`;
    return;
  }

  const payload = {
    cart_id: Number(cartId),

    customer_name: customerName,
    customer_email: customerEmail,
    customer_phone: customerPhone || null,

    shipping_address_line1: document.getElementById("shipping-address-line1").value.trim(),
    shipping_address_line2: document.getElementById("shipping-address-line2").value.trim() || null,
    shipping_city: document.getElementById("shipping-city").value.trim(),
    shipping_state: document.getElementById("shipping-state").value.trim(),
    shipping_zip: document.getElementById("shipping-zip").value.trim(),
    shipping_country: document.getElementById("shipping-country").value.trim()
  };

  try {
    const response = await fetch(`${API_BASE_URL}/orders/from-cart`, {
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

    clearCartId();

    messageContainer.innerHTML = `
      <p class="success-message">
        Order placed successfully. Order ID: ${data.id}. Total: $${Number(data.total_amount).toFixed(2)}
      </p>
    `;

    document.getElementById("checkout-form").reset();
    document.getElementById("checkout-cart-summary").innerHTML = "<p>Your cart has been cleared.</p>";

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

async function adminLoadProducts() {
  const container = document.getElementById("admin-products-container");
  if (!container) return;

  try {
    const response = await fetch(`${API_BASE_URL}/products/admin/all`);
    const products = await response.json();

    if (!products.length) {
      container.innerHTML = "<p>No active products found.</p>";
      return;
    }

    container.innerHTML = "";

    products.forEach(product => {
      const card = document.createElement("div");
      card.className = "admin-product-card";

      card.innerHTML = `
        <h3>${product.name}</h3>
        <p>ID: ${product.id}</p>
        <p>${product.description || ""}</p>
        <p>Price: $${Number(product.price).toFixed(2)}</p>
        <p>Stock: ${product.stock}</p>
        <p>Status: ${product.is_active ? "Active" : "Inactive"}</p>

        <div class="admin-inline-controls">
          <input class="admin-price-input" type="number" step="0.01" min="0" placeholder="New price" />
          <input class="admin-stock-input" type="number" min="0" placeholder="Set stock" />
          <button class="button admin-update-button">Update</button>
        </div>

        <div class="admin-inline-controls">
          <input class="admin-restock-input" type="number" min="1" placeholder="Restock qty" />
          <button class="button admin-restock-button">Restock</button>
          <button class="button admin-deactivate-button">Deactivate</button>
          <button class="button admin-activate-button">Activate</button>
        </div>
      `;

      card.querySelector(".admin-update-button").addEventListener("click", async () => {
        const priceValue = card.querySelector(".admin-price-input").value;
        const stockValue = card.querySelector(".admin-stock-input").value;

        const payload = {};

        if (priceValue !== "") {
          payload.price = Number(priceValue);
        }

        if (stockValue !== "") {
          payload.stock = Number(stockValue);
        }

        if (Object.keys(payload).length === 0) {
          alert("Enter a price or stock value to update.");
          return;
        }

        await adminUpdateProduct(product.id, payload);
      });

      card.querySelector(".admin-restock-button").addEventListener("click", async () => {
        const quantity = Number(card.querySelector(".admin-restock-input").value);

        if (!quantity || quantity < 1) {
          alert("Enter a valid restock quantity.");
          return;
        }

        await adminRestockProduct(product.id, quantity);
      });

      card.querySelector(".admin-deactivate-button").addEventListener("click", async () => {
        const confirmed = confirm(`Deactivate ${product.name}?`);

        if (!confirmed) return;

        await adminDeactivateProduct(product.id);
      });

      card.querySelector(".admin-activate-button").addEventListener("click", async () => {
        await adminActivateProduct(product.id);
      });

      container.appendChild(card);
    });

  } catch (error) {
    console.error("Admin load products error:", error);
    container.innerHTML = "<p>Failed to load products.</p>";
  }
}

async function adminCreateProduct(event) {
  event.preventDefault();

  const messageContainer = document.getElementById("admin-message");

  const payload = {
    name: document.getElementById("admin-name").value.trim(),
    description: document.getElementById("admin-description").value.trim(),
    price: Number(document.getElementById("admin-price").value),
    stock: Number(document.getElementById("admin-stock").value),
    image_url: document.getElementById("admin-image-url").value.trim() || null,
    is_active: true
  };

  try {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      messageContainer.innerHTML = `<p class="error-message">${data.detail || "Failed to create product."}</p>`;
      return;
    }

    messageContainer.innerHTML = `<p class="success-message">Created product: ${data.name}</p>`;
    document.getElementById("admin-create-product-form").reset();
    adminLoadProducts();

  } catch (error) {
    console.error("Admin create error:", error);
    messageContainer.innerHTML = `<p class="error-message">Unexpected error creating product.</p>`;
  }
}

async function adminUpdateProduct(productId, payload) {
  const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    alert("Failed to update product.");
    return;
  }

  await adminLoadProducts();
}

async function adminRestockProduct(productId, quantity) {
  const response = await fetch(`${API_BASE_URL}/products/${productId}/restock`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ quantity })
  });

  if (!response.ok) {
    alert("Failed to restock product.");
    return;
  }

  await adminLoadProducts();
}

async function adminDeactivateProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/products/${productId}/deactivate`, {
    method: "PATCH"
  });

  if (!response.ok) {
    alert("Failed to deactivate product.");
    return;
  }

  await adminLoadProducts();
}

async function adminActivateProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/products/${productId}/activate`, {
    method: "PATCH"
  });

  if (!response.ok) {
    alert("Failed to activate product.");
    return;
  }

  await adminLoadProducts();
}

async function adminLoadOrders() {
  const container = document.getElementById("admin-orders-container");
  if (!container) return;

  try {
    const response = await fetch(`${API_BASE_URL}/orders`);
    const orders = await response.json();

    if (!orders.length) {
      container.innerHTML = "<p>No orders found.</p>";
      return;
    }

    container.innerHTML = "";

    orders.forEach(order => {
      const card = document.createElement("div");
      card.className = "admin-product-card";

      const itemsHtml = order.items.map(item => `
        <li>
          Product ID: ${item.product_id},
          Quantity: ${item.quantity},
          Price: $${Number(item.price_at_purchase).toFixed(2)}
        </li>
      `).join("");

      card.innerHTML = `
        <h3>Order #${order.id}</h3>
        <p>Customer: ${order.customer_name}</p>
        <p>Email: ${order.customer_email}</p>
        <p>Phone: ${order.customer_phone || "N/A"}</p>
        <p>
          Shipping:
          ${order.shipping_address_line1 || ""}
          ${order.shipping_address_line2 || ""}
          ${order.shipping_city || ""},
          ${order.shipping_state || ""}
          ${order.shipping_zip || ""}
          ${order.shipping_country || ""}
        </p>
        <p>Total: $${Number(order.total_amount).toFixed(2)}</p>
        <p>Created: ${new Date(order.created_at).toLocaleString()}</p>
        <ul>${itemsHtml}</ul>
      `;

      container.appendChild(card);
    });

  } catch (error) {
    console.error("Admin load orders error:", error);
    container.innerHTML = "<p>Failed to load orders.</p>";
  }
}

function initializeAdminPage() {
  const form = document.getElementById("admin-create-product-form");
  const adminProductsContainer = document.getElementById("admin-products-container");
  const adminOrdersContainer = document.getElementById("admin-orders-container");

  if (form) {
    form.addEventListener("submit", adminCreateProduct);
  }

  if (adminProductsContainer) {
    adminLoadProducts();
  }

  if (adminOrdersContainer) {
    adminLoadOrders();
  }
}


document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  loadProductDetail();
  loadCart();
  loadCheckoutSummary();
  initializeCheckoutForm();
  initializeAdminPage();
});

