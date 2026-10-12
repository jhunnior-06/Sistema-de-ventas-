const cart = new Map();
const currency = (value) => `S/ ${Number(value).toFixed(2)}`;
const productList = document.getElementById("product-list");
const cartItems = document.getElementById("cart-items");
const totalEl = document.getElementById("total");
const messageEl = document.getElementById("sale-message");
const confirmButton = document.getElementById("confirm-sale");

function total() {
  return [...cart.values()].reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function renderCart() {
  if (!cart.size) {
    cartItems.innerHTML = '<p class="muted">Aún no agregaste productos.</p>';
  } else {
    cartItems.innerHTML = [...cart.values()].map(item => `
      <div class="cart-row">
        <div><b>${item.name}</b><small>${currency(item.price)} c/u</small></div>
        <div class="cart-price">${currency(item.price * item.quantity)}
          <div class="qty"><button data-action="minus" data-id="${item.id}">−</button><span>${item.quantity}</span><button data-action="plus" data-id="${item.id}">+</button></div>
        </div>
      </div>`).join("");
  }
  totalEl.textContent = currency(total());
}

productList?.addEventListener("click", event => {
  const card = event.target.closest(".product-card");
  if (!card) return;
  const id = Number(card.dataset.id);
  const current = cart.get(id);
  if (current && current.quantity >= current.stock) return;
  cart.set(id, current ? {...current, quantity: current.quantity + 1} : {
    id, name: card.dataset.name, price: Number(card.dataset.price),
    stock: Number(card.dataset.stock), quantity: 1
  });
  renderCart();
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

renderCart();
