const cart = new Map();
const currency = (value) => `S/ ${Number(value).toFixed(2)}`;
const productList = document.getElementById("product-list");
const cartItems = document.getElementById("cart-items");
const totalEl = document.getElementById("total");
const messageEl = document.getElementById("sale-message");
const confirmButton = document.getElementById("confirm-sale");
const cartCounter = document.getElementById("cart-counter");
const cartSummary = document.getElementById("cart-summary");
const cartShortcut = document.getElementById("cart-shortcut");
const cartPanel = document.getElementById("cart-panel");
const searchInput = document.getElementById("store-search");
const categoryList = document.getElementById("category-list");
const resultsCount = document.getElementById("results-count");
const emptyResults = document.getElementById("empty-results");
const cards = [...document.querySelectorAll(".market-product")];
let activeCategory = "Todos";

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

function total() {
  return [...cart.values()].reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function productCount() {
  return [...cart.values()].reduce((sum, item) => sum + item.quantity, 0);
}

function renderCart() {
  if (!cart.size) {
    cartItems.innerHTML = '<p class="muted">Aún no agregaste productos.</p>';
  } else {
    cartItems.innerHTML = [...cart.values()].map(item => `
      <div class="cart-row">
        <div><b>${escapeHtml(item.name)}</b><small>${currency(item.price)} c/u</small></div>
        <div class="cart-price">${currency(item.price * item.quantity)}
          <div class="qty"><button data-action="minus" data-id="${item.id}" aria-label="Quitar uno">−</button><span>${item.quantity}</span><button data-action="plus" data-id="${item.id}" aria-label="Agregar uno">+</button></div>
        </div>
      </div>`).join("");
  }
  const count = productCount();
  totalEl.textContent = currency(total());
  cartCounter.textContent = count;
  cartSummary.textContent = `${count} ${count === 1 ? "producto" : "productos"}`;
}

function renderCategories() {
  const categories = ["Todos", ...new Set(cards.map(card => card.dataset.category || "Otros"))];
  categoryList.innerHTML = categories.map(category => `<button type="button" class="category-chip ${category === activeCategory ? "active" : ""}" data-category="${escapeHtml(category)}">${escapeHtml(category)}</button>`).join("");
}

function filterProducts() {
  const term = (searchInput.value || "").trim().toLowerCase();
  let visible = 0;
  cards.forEach(card => {
    const matchesCategory = activeCategory === "Todos" || card.dataset.category === activeCategory;
    const searchable = `${card.dataset.name} ${card.dataset.category}`.toLowerCase();
    const matchesSearch = !term || searchable.includes(term);
    const show = matchesCategory && matchesSearch;
    card.hidden = !show;
    if (show) visible += 1;
  });
  resultsCount.textContent = `${visible} ${visible === 1 ? "producto encontrado" : "productos encontrados"}`;
  emptyResults.hidden = visible !== 0;
}

productList?.addEventListener("click", event => {
  const card = event.target.closest(".product-card");
  if (!card) return;
  const id = Number(card.dataset.id);
  const current = cart.get(id);
  if (current && current.quantity >= current.stock) return showMessage("Ya agregaste el máximo disponible.", true);
  cart.set(id, current ? {...current, quantity: current.quantity + 1} : {
    id, name: card.dataset.name, price: Number(card.dataset.price),
    stock: Number(card.dataset.stock), quantity: 1
  });
  renderCart();
  showMessage(`${card.dataset.name} se agregó al carrito.`);
});

cartItems?.addEventListener("click", event => {
  const button = event.target.closest("button[data-id]");
  if (!button) return;
  const id = Number(button.dataset.id);
  const item = cart.get(id);
  if (!item) return;
  if (button.dataset.action === "minus") {
    item.quantity === 1 ? cart.delete(id) : cart.set(id, {...item, quantity: item.quantity - 1});
  } else if (item.quantity < item.stock) {
    cart.set(id, {...item, quantity: item.quantity + 1});
  }
  renderCart();
});

categoryList?.addEventListener("click", event => {
  const button = event.target.closest("[data-category]");
  if (!button) return;
  activeCategory = button.dataset.category;
  renderCategories();
  filterProducts();
});

searchInput?.addEventListener("input", filterProducts);
cartShortcut?.addEventListener("click", () => cartPanel?.scrollIntoView({behavior: "smooth", block: "start"}));

confirmButton?.addEventListener("click", async () => {
  if (!cart.size) return showMessage("Agrega al menos un producto.", true);
  confirmButton.disabled = true;
  confirmButton.textContent = "Enviando pedido...";
  try {
    const response = await fetch("/api/compras", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({items: [...cart.values()].map(({id, quantity}) => ({product_id: id, quantity}))})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No se pudo enviar el pedido.");
    cart.clear();
    renderCart();
    showMessage(`Pedido ${data.invoice_number} enviado: ${currency(data.total)}.`);
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    confirmButton.disabled = false;
    confirmButton.textContent = "Confirmar pedido";
  }
});

function showMessage(text, error = false) {
  messageEl.textContent = text;
  messageEl.className = `sale-message ${error ? "error" : "success"}`;
}

renderCategories();
filterProducts();
renderCart();
