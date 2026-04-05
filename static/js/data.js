// data.js - Admin page: fetch bookings, show table, confirm/reject/delete & clear

async function fetchBookings() {
  try {
    const res = await fetch('/api/bookings', { method: 'GET' });

    if (res.status === 401) {
      alert('Unauthorized. Please login as admin.');
      window.location.href = '/admin';
      return [];
    }

    if (!res.ok) {
      console.error('Failed to fetch bookings:', res.status, res.statusText);
      return [];
    }

    const data = await res.json();
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.bookings)) return data.bookings;
    return [];
  } catch (err) {
    console.error('Error fetching bookings:', err);
    return [];
  }
}

function renderTable(bookings) {
  const container = document.getElementById('dataTable');
  if (!container) return;

  container.innerHTML = '';

  if (!bookings || bookings.length === 0) {
    container.innerHTML = '<p>No bookings available.</p>';
    return;
  }

  const table = document.createElement('table');
  table.className = 'admin-table';

  const thead = document.createElement('thead');
  const headRow = document.createElement('tr');

  [
    'ID','Name','Email','Phone',
    'Car','Image','Start','End',
    'Price','Status','Actions'
  ].forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    headRow.appendChild(th);
  });

  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');

  bookings.forEach((b, index) => {
    const tr = document.createElement('tr');

    // ✅ ID FIX: UI Serial Number
    const tdId = document.createElement('td');
    tdId.textContent = index + 1;   // 🔥 only change here
    tr.appendChild(tdId);

    ['name','email','phone','car_model'].forEach(key => {
      const td = document.createElement('td');
      td.textContent = b[key] || '';
      tr.appendChild(td);
    });

    const tdImg = document.createElement('td');
    if (b.car_image) {
      let imgPath = b.car_image;
      if (!imgPath.startsWith('/') && !imgPath.startsWith('http')) {
        imgPath = '/static/images/' + imgPath;
      }
      const img = document.createElement('img');
      img.src = imgPath;
      img.style.width = '80px';
      img.onerror = () => img.src = '/static/images/default.png';
      tdImg.appendChild(img);
    } else {
      tdImg.textContent = 'No Image';
    }
    tr.appendChild(tdImg);

    tr.appendChild(createTd(b.start_date));
    tr.appendChild(createTd(b.end_date));
    tr.appendChild(createTd(b.price ? `₹${b.price}` : ''));

    const tdStatus = document.createElement('td');
    tdStatus.textContent = b.status || 'Pending';
    tdStatus.style.fontWeight = 'bold';

    if (b.status === 'Confirmed') tdStatus.style.color = 'green';
    else if (b.status === 'Rejected') tdStatus.style.color = 'red';
    else tdStatus.style.color = 'blue';

    tr.appendChild(tdStatus);

    const tdActions = document.createElement('td');
    tdActions.className = 'action-cell';

    if (b.status !== 'Confirmed') {
      const confirmBtn = document.createElement('button');
      confirmBtn.textContent = 'Confirm';
      confirmBtn.className = 'btn-confirm';
      confirmBtn.onclick = () => updateStatus(b.id, 'confirm'); // real ID still used
      tdActions.appendChild(confirmBtn);
    }

    if (b.status !== 'Rejected') {
      const rejectBtn = document.createElement('button');
      rejectBtn.textContent = 'Reject';
      rejectBtn.className = 'btn-reject';
      rejectBtn.onclick = () => updateStatus(b.id, 'reject'); // real ID still used
      tdActions.appendChild(rejectBtn);
    }

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.className = 'btn-delete';
    delBtn.onclick = () => deleteBooking(b.id); // real ID still used
    tdActions.appendChild(delBtn);

    tr.appendChild(tdActions);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  container.appendChild(table);
}

function createTd(text) {
  const td = document.createElement('td');
  td.textContent = text || '';
  return td;
}

async function updateStatus(id, action) {
  if (!confirm(`Are you sure you want to ${action} this booking?`)) return;

  try {
    const res = await fetch(`/api/bookings/${action}/${id}`, { method: 'POST' });
    if (!res.ok) {
      alert('Action failed');
      return;
    }
    alert(`Booking ${action}ed successfully`);
    loadAndRender();
  } catch (err) {
    console.error(err);
  }
}

async function deleteBooking(id) {
  if (!confirm('Delete this booking?')) return;

  try {
    const res = await fetch(`/api/bookings/${id}`, { method: 'DELETE' });
    if (!res.ok) {
      alert('Delete failed');
      return;
    }
    alert('Deleted successfully');
    loadAndRender();
  } catch (err) {
    console.error(err);
  }
}

async function clearAll() {
  if (!confirm('Clear all bookings?')) return;

  try {
    const res = await fetch('/api/bookings/clear', { method: 'POST' });
    if (!res.ok) {
      alert('Failed');
      return;
    }
    alert('All bookings cleared');
    loadAndRender();
  } catch (err) {
    console.error(err);
  }
}

async function loadAndRender() {
  const bookings = await fetchBookings();
  renderTable(bookings);
}

document.addEventListener('DOMContentLoaded', () => {
  loadAndRender();
  const clearBtn = document.getElementById('clearAll');
  if (clearBtn) clearBtn.onclick = clearAll;
});