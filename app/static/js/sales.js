const cart = new Map();
const currency = (value) => `S/ ${Number(value).toFixed(2)}`;
const productList = document.getElementById("product-list");
const cartItems = document.getElementById("cart-items");
const subtotalEl = document.getElementById("subtotal");
const totalEl = document.getElementById("total");
const discountEl = document.getElementById("discount");
const messageEl = document.getElementById("sale-message");
const confirmButton = document.getElementById("confirm-sale");

function subtotal() { return [...cart.values()].reduce((sum, item) => sum + item.price * item.quantity, 0); }
function renderCart() {
  if (!cart.size) cartItems.innerHTML = '<p class="muted">Aún no agregaste productos.</p>';
  else cartItems.innerHTML = [...cart.values()].map(item => `<div class="cart-row"><div><b>${item.name}</b><small>${currency(item.price)} c/u · disponible: ${item.stock}</small></div><div class="cart-price">${currency(item.price * item.quantity)}<div class="qty"><button data-action="minus" data-id="${item.id}">−</button><span>${item.quantity}</span><button data-action="plus" data-id="${item.id}">+</button></div></div></div>`).join("");
  const discount = Number(discountEl.value) || 0, sub = subtotal();
  subtotalEl.textContent = currency(sub); totalEl.textContent = currency(Math.max(0, sub - discount));
}
productList?.addEventListener("click", event => {
  const card = event.target.closest(".product-card"); if (!card) return;
  const id = Number(card.dataset.id), current = cart.get(id);
  if (current && current.quantity >= current.stock) return;
  cart.set(id, current ? {...current, quantity: current.quantity + 1} : {id, name: card.dataset.name, price: Number(card.dataset.price), stock: Number(card.dataset.stock), quantity: 1});
  renderCart();
});
cartItems.addEventListener("click", event => {
  const button = event.target.closest("button[data-id]"); if (!button) return;
  const id = Number(button.dataset.id), item = cart.get(id); if (!item) return;
  if (button.dataset.action === "minus") { if (item.quantity === 1) cart.delete(id); else cart.set(id, {...item, quantity: item.quantity - 1}); }
  else if (item.quantity < item.stock) cart.set(id, {...item, quantity: item.quantity + 1});
  renderCart();
});
discountEl.addEventListener("input", renderCart);
confirmButton.addEventListener("click", async () => {
  const sub = subtotal(), discount = Number(discountEl.value) || 0;
  if (!cart.size) return showMessage("Agrega al menos un producto.", true);
  if (discount > sub) return showMessage("El descuento no puede superar el subtotal.", true);
  confirmButton.disabled = true; confirmButton.textContent = "Registrando...";
  try {
    const response = await fetch("/api/ventas", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({customer_name: document.getElementById("customer-name").value.trim() || null, payment_method: document.getElementById("payment-method").value, discount, items:[...cart.values()].map(({id, quantity}) => ({product_id:id, quantity}))})});
    const data = await response.json(); if (!response.ok) throw new Error(data.detail || "No se pudo registrar la venta.");
    cart.clear(); discountEl.value = "0"; document.getElementById("customer-name").value = ""; renderCart();
    showMessage(`Venta ${data.invoice_number} registrada: ${currency(data.total)}.`);
    setTimeout(() => window.location.href = "/", 1100);
  } catch (error) { showMessage(error.message, true); }
  finally { confirmButton.disabled = false; confirmButton.textContent = "Confirmar venta"; }
});
function showMessage(text, error=false) { messageEl.textContent=text; messageEl.className=`sale-message ${error ? "error" : "success"}`; }
renderCart();
