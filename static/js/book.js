// book.js - handles booking form preview, price + image update, and saving to server

// Convert form data to object
function formToObject(form) {
  const o = {};
  new FormData(form).forEach((v, k) => o[k] = v);

  // Get selected car details
  const carSelect = form.querySelector('select[name="car_model"]');
  if (carSelect) {
    const selectedOption = carSelect.options[carSelect.selectedIndex];
    o.car_price = parseInt(selectedOption.dataset.price || 0);
    o.car_model = carSelect.value;
  }

  return o;
}

// Calculate total price
function calculateTotalPrice(start, end, carPrice) {
  const startDate = new Date(start);
  const endDate = new Date(end);
  if (isNaN(startDate) || isNaN(endDate) || endDate < startDate) return 0;

  const diffTime = endDate - startDate;
  const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  return days * carPrice;
}

// Render preview
function renderPreview(obj) {
  const preview = document.getElementById('preview');
  if (!obj || Object.keys(obj).length === 0) {
    preview.innerHTML = '<p>No data to preview.</p>';
    return;
  }

  const totalPrice = calculateTotalPrice(obj.start_date, obj.end_date, obj.car_price || 0);

  preview.innerHTML = `
    <div class="preview-card">
      <p><strong>Name:</strong> ${obj.name || ''}</p>
      <p><strong>Email:</strong> ${obj.email || ''}</p>
      <p><strong>Phone:</strong> ${obj.phone || ''}</p>
      <p><strong>Car Model:</strong> ${obj.car_model || ''}</p>
      <div class="car-preview">
        <img src="${obj.car_image || '/static/images/default.png'}" 
             alt="Car Image" 
             style="width:150px; height:auto; border-radius:8px;">
      </div>
      <p><strong>Start Date:</strong> ${obj.start_date || ''}</p>
      <p><strong>End Date:</strong> ${obj.end_date || ''}</p>
      <p><strong>Price (per day):</strong> ₹${obj.car_price || 0}</p>
      <p><strong>Total Price:</strong> ₹${totalPrice}</p>
    </div>
  `;

  obj.price = totalPrice;
  sessionStorage.setItem('bookingDetails', JSON.stringify(obj));
}

// Save to server
async function saveToServer(data) {
  data.price = calculateTotalPrice(data.start_date, data.end_date, data.car_price || 0);
  const res = await fetch('/api/bookings', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const json = await res.json();
  if (json.success) alert('Booking saved successfully!');
  else alert('Failed to save booking.');
}

// DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('bookingForm');
  const previewBtn = document.getElementById('previewBtn');
  const carSelect = form.querySelector('select[name="car_model"]');
  const priceField = document.getElementById('priceField');
  const carImage = document.getElementById('carImage');

  // ✅ Ensure small size for main form car image
  carImage.style.width = "400px";
  carImage.style.height = "auto";
  carImage.style.borderRadius = "8px";

  // Map of car images
  const carImages = {
   
    "swift": "/static/images/swift.jpg",
    "innova_crysta": "/static/images/innova_crysta.jpg",
    "hyundai_creta": "/static/images/hyundai_creta.jpg",
    "baleno": "/static/images/baleno.jpg",
    "seltos": "/static/images/seltos.jpg",
    "fortuner": "/static/images/fortuner.jpg",
    "thar": "/static/images/thar.jpg",
    "scorpio_n": "/static/images/scorpio_n.jpg"
  };

  // 🔄 Update price + image when car changes
  carSelect.addEventListener('change', () => {
    const selectedOption = carSelect.options[carSelect.selectedIndex];
    const carPrice = selectedOption.dataset.price || 0;
    const carKey = carSelect.value;

    // update price field
    priceField.value = `₹${carPrice}/day`;

    // update image
    carImage.src = carImages[carKey] || "/static/images/default.png";
  });

  // Preview button
  previewBtn.addEventListener('click', () => {
    const obj = formToObject(form);
    obj.car_image = carImage.src; // save selected car image
    renderPreview(obj);
  });

  // Submit form
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const obj = formToObject(form);
    obj.car_image = carImage.src;
    saveToServer(obj);
  });

  // If previous booking exists, show preview and update price + image
  const existing = JSON.parse(sessionStorage.getItem('bookingDetails') || '{}');
  if (existing && Object.keys(existing).length) {
    renderPreview(existing);
    priceField.value = `₹${existing.car_price || 0}/day`;
    carImage.src = existing.car_image || "/static/images/default.png";
  }
});
