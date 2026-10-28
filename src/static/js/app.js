/**
 * LabReserve - Single Page Application with JWT Authentication & RBAC
 * Flujo SDD con GitHub Spec Kit
 */

document.addEventListener('DOMContentLoaded', () => {
  // State
  let token = localStorage.getItem('labreserve_token') || null;
  let currentUser = null;

  // Header & Session Elements
  const btnOpenLogin = document.getElementById('btn-open-login');
  const userProfileBadge = document.getElementById('user-profile-badge');
  const userDisplayName = document.getElementById('user-display-name');
  const userDisplayRole = document.getElementById('user-display-role');
  const userAvatar = document.getElementById('user-avatar');
  const btnLogout = document.getElementById('btn-logout');
  const btnSeedData = document.getElementById('btn-seed-data');

  // Tabs & Sections
  const tabGrid = document.getElementById('tab-grid');
  const tabUserView = document.getElementById('tab-user-view');
  const tabUserViewText = document.getElementById('tab-user-view-text');
  const sectionGrid = document.getElementById('section-grid');
  const sectionMyReservations = document.getElementById('section-my-reservations');
  const sectionAdminDashboard = document.getElementById('section-admin-dashboard');

  // Controls & Filter Elements
  const selectLab = document.getElementById('select-lab');
  const inputDate = document.getElementById('input-date');
  const inputStartTime = document.getElementById('input-start-time');
  const inputEndTime = document.getElementById('input-end-time');
  const filterForm = document.getElementById('filter-form');
  const workstationsGrid = document.getElementById('workstations-grid');

  // Stats
  const statTotal = document.getElementById('stat-total');
  const statAvailable = document.getElementById('stat-available');
  const statOccupied = document.getElementById('stat-occupied');
  const statMaintenance = document.getElementById('stat-maintenance');
  const statWindow = document.getElementById('stat-window');

  // Modals
  const modalLogin = document.getElementById('modal-login');
  const modalLoginClose = document.getElementById('modal-login-close');
  const modalLoginCancel = document.getElementById('modal-login-cancel');
  const formLogin = document.getElementById('form-login');
  const btnQuickStudent = document.getElementById('btn-quick-student');
  const btnQuickAdmin = document.getElementById('btn-quick-admin');

  const modalBooking = document.getElementById('modal-booking');
  const modalClose = document.getElementById('modal-close');
  const modalCancelBtn = document.getElementById('modal-cancel-btn');
  const formBooking = document.getElementById('form-booking');
  const modalStationInfo = document.getElementById('modal-station-info');
  const bookingWsId = document.getElementById('booking-workstation-id');
  const bookingStartTime = document.getElementById('booking-start-time');
  const bookingEndTime = document.getElementById('booking-end-time');
  const summaryTimes = document.getElementById('summary-times');
  const summaryDuration = document.getElementById('summary-duration');
  const bookingAuthBox = document.getElementById('booking-auth-box');
  const bookingUnauthBox = document.getElementById('booking-unauth-box');
  const bookingUserName = document.getElementById('booking-user-name');
  const bookingUserDetails = document.getElementById('booking-user-details');
  const btnSubmitBooking = document.getElementById('btn-submit-booking');
  const btnLoginFromModal = document.getElementById('btn-login-from-modal');

  // Lists
  const myReservationsList = document.getElementById('my-reservations-list');
  const btnRefreshMyReservations = document.getElementById('btn-refresh-my-reservations');
  const adminReservationsList = document.getElementById('admin-reservations-list');
  const btnRefreshAdminReservations = document.getElementById('btn-refresh-admin-reservations');

  // Initialize Default Date: Mañana a las 10:00
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  inputDate.value = tomorrow.toISOString().split('T')[0];

  // Helper: Request with Bearer Token
  function getAuthHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  // ==========================================
  // AUTHENTICATION & SESSION MANAGEMENT
  // ==========================================
  async function initAuth() {
    if (!token) {
      updateAuthUI();
      loadLaboratories();
      return;
    }

    try {
      const res = await fetch('/api/auth/me', { headers: getAuthHeaders() });
      if (res.ok) {
        currentUser = await res.json();
      } else {
        // Token inválido o expirado
        logout(false);
      }
    } catch (e) {
      logout(false);
    }
    updateAuthUI();
    loadLaboratories();
  }

  function updateAuthUI() {
    if (currentUser) {
      btnOpenLogin.classList.add('hidden');
      userProfileBadge.classList.remove('hidden');

      userDisplayName.textContent = currentUser.full_name.split(' ')[0] + ' ' + (currentUser.full_name.split(' ')[1] || '');
      userDisplayRole.textContent = currentUser.role;
      userAvatar.textContent = currentUser.full_name.charAt(0);

      if (currentUser.role === 'ADMIN') {
        userDisplayRole.className = 'role-pill role-admin';
        tabUserViewText.textContent = 'Panel Admin';
      } else {
        userDisplayRole.className = 'role-pill role-student';
        tabUserViewText.textContent = 'Mis Reservas';
      }
    } else {
      btnOpenLogin.classList.remove('hidden');
      userProfileBadge.classList.add('hidden');
      tabUserViewText.textContent = 'Mis Reservas';
    }
  }

  function openLoginModal() {
    modalLogin.classList.remove('hidden');
    document.getElementById('input-login-username').focus();
  }

  function closeLoginModal() {
    modalLogin.classList.add('hidden');
    formLogin.reset();
  }

  btnOpenLogin.addEventListener('click', openLoginModal);
  modalLoginClose.addEventListener('click', closeLoginModal);
  modalLoginCancel.addEventListener('click', closeLoginModal);
  btnLoginFromModal.addEventListener('click', () => {
    closeBookingModal();
    openLoginModal();
  });

  // Login Handler
  async function performLogin(username, password) {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Credenciales inválidas.');
      }

      token = data.access_token;
      currentUser = data.user;
      localStorage.setItem('labreserve_token', token);

      updateAuthUI();
      closeLoginModal();
      showToast('Bienvenido', `Sesión iniciada como ${currentUser.full_name} (${currentUser.role})`, 'success');

      // Refrescar disponibilidad para reflejar opciones según el rol
      checkAvailability();
    } catch (err) {
      showToast('Error de Autenticación', err.message, 'error');
    }
  }

  formLogin.addEventListener('submit', (e) => {
    e.preventDefault();
    const u = document.getElementById('input-login-username').value.trim();
    const p = document.getElementById('input-login-password').value.trim();
    performLogin(u, p);
  });

  // Accesos Rápidos Demo
  btnQuickStudent.addEventListener('click', () => {
    performLogin('20240981', 'estudiante123');
  });

  btnQuickAdmin.addEventListener('click', () => {
    performLogin('ADMIN-01', 'admin123');
  });

  // Logout Handler
  function logout(showNotification = true) {
    token = null;
    currentUser = null;
    localStorage.removeItem('labreserve_token');
    updateAuthUI();
    showGridTab();
    if (showNotification) {
      showToast('Sesión Cerrada', 'Has salido del sistema exitosamente.', 'info');
    }
    checkAvailability();
  }

  btnLogout.addEventListener('click', () => logout(true));

  // ==========================================
  // TAB NAVIGATION
  // ==========================================
  function showGridTab() {
    tabGrid.classList.add('active');
    tabUserView.classList.remove('active');
    sectionGrid.classList.remove('hidden');
    sectionMyReservations.classList.add('hidden');
    sectionAdminDashboard.classList.add('hidden');
  }

  tabGrid.addEventListener('click', showGridTab);

  tabUserView.addEventListener('click', () => {
    if (!currentUser) {
      showToast('Autenticación Requerida', 'Inicia sesión para gestionar o revisar tus turnos.', 'warning');
      openLoginModal();
      return;
    }

    tabGrid.classList.remove('active');
    tabUserView.classList.add('active');
    sectionGrid.classList.add('hidden');

    if (currentUser.role === 'ADMIN') {
      sectionAdminDashboard.classList.remove('hidden');
      sectionMyReservations.classList.add('hidden');
      loadAdminDashboard();
    } else {
      sectionMyReservations.classList.remove('hidden');
      sectionAdminDashboard.classList.add('hidden');
      loadMyReservations();
    }
  });

  // ==========================================
  // DISPONIBILIDAD & GRID DE PUESTOS
  // ==========================================
  async function loadLaboratories() {
    try {
      const res = await fetch('/api/laboratories');
      if (!res.ok) throw new Error('Error al listar laboratorios');
      const labs = await res.json();

      selectLab.innerHTML = '';
      if (labs.length === 0) {
        selectLab.innerHTML = '<option value="" disabled selected>No hay laboratorios registrados (pulsa "Sembrar Demo")</option>';
        return;
      }

      labs.forEach((lab, index) => {
        const opt = document.createElement('option');
        opt.value = lab.id;
        opt.textContent = `${lab.code} - ${lab.name} (${lab.location})`;
        if (index === 0) opt.selected = true;
        selectLab.appendChild(opt);
      });

      checkAvailability();
    } catch (err) {
      showToast('Error', 'No se pudieron cargar los laboratorios: ' + err.message, 'error');
    }
  }

  async function checkAvailability(silent = false) {
    const labId = selectLab.value;
    if (!labId) return;

    const date = inputDate.value;
    const startVal = inputStartTime.value;
    const endVal = inputEndTime.value;

    if (!date || !startVal || !endVal) {
      if (!silent) showToast('Atención', 'Por favor ingresa fecha, hora de inicio y fin.', 'warning');
      return;
    }

    const startISO = `${date}T${startVal}:00`;
    const endISO = `${date}T${endVal}:00`;

    if (new Date(endISO) <= new Date(startISO)) {
      if (!silent) showToast('Validación', 'La hora de fin debe ser posterior a la de inicio.', 'error');
      return;
    }

    const durationMinutes = (new Date(endISO) - new Date(startISO)) / (1000 * 60);
    if (durationMinutes > 120) {
      if (!silent) showToast('Regla de Negocio', 'La duración máxima permitida por turno es de 2 horas (120 min).', 'error');
      return;
    }

    if (!silent) {
      workstationsGrid.innerHTML = `
        <div class="empty-state">
          <p>Consultando disponibilidad del laboratorio en tiempo real...</p>
        </div>
      `;
    }

    try {
      const url = `/api/laboratories/${labId}/availability?start_time=${encodeURIComponent(startISO)}&end_time=${encodeURIComponent(endISO)}`;
      const res = await fetch(url);
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'Error al obtener disponibilidad');

      renderAvailability(data, startISO, endISO, durationMinutes);
    } catch (err) {
      if (!silent) {
        workstationsGrid.innerHTML = `
          <div class="empty-state">
            <p style="color: var(--status-occupied);">${err.message}</p>
          </div>
        `;
        showToast('Error de Disponibilidad', err.message, 'error');
      }
    }
  }

  function renderAvailability(data, startISO, endISO, durationMinutes) {
    const workstations = data.available_workstations || [];
    const totalCount = data.total_workstations || workstations.length;
    const availableCount = workstations.filter(w => w.is_available && w.status !== 'MAINTENANCE').length;
    const maintenanceCount = workstations.filter(w => w.status === 'MAINTENANCE').length;
    const occupiedCount = Math.max(0, totalCount - availableCount - maintenanceCount);

    statTotal.textContent = totalCount;
    statAvailable.textContent = availableCount;
    statOccupied.textContent = occupiedCount;
    if (statMaintenance) statMaintenance.textContent = maintenanceCount;
    statWindow.textContent = `${inputStartTime.value} - ${inputEndTime.value} (${durationMinutes / 60}h)`;

    workstationsGrid.innerHTML = '';
    if (workstations.length === 0) {
      workstationsGrid.innerHTML = `
        <div class="empty-state">
          <p>Este laboratorio no tiene puestos registrados aún.</p>
        </div>
      `;
      return;
    }

    workstations.forEach(ws => {
      const card = document.createElement('div');
      const isMaint = ws.status === 'MAINTENANCE';
      const isFree = ws.is_available && !isMaint;

      let statusClass = 'occupied';
      let statusText = 'Ocupado';

      if (isMaint) {
        statusClass = 'maintenance';
        statusText = 'Mantenimiento';
      } else if (isFree) {
        statusClass = 'available';
        statusText = 'Disponible';
      }

      let mainBtnHtml = '';
      if (isMaint) {
        mainBtnHtml = `<button class="ws-action-btn" disabled>En Mantenimiento ⚠️</button>`;
      } else if (isFree) {
        mainBtnHtml = `<button class="ws-action-btn">${currentUser ? 'Reservar (1 Clic)' : 'Reservar Turno'}</button>`;
      } else {
        mainBtnHtml = `<button class="ws-action-btn" disabled>No Disponible</button>`;
      }

      let adminActionHtml = '';
      if (currentUser && currentUser.role === 'ADMIN') {
        if (isMaint) {
          adminActionHtml = `
            <button class="btn btn-outline toggle-maint-btn btn-deactivate-maint" style="font-size:0.75rem; margin-top:0.4rem; width:100%;" title="Habilitar puesto para reservas de estudiantes">
              ✅ Quitar Mantenimiento
            </button>
          `;
        } else {
          adminActionHtml = `
            <button class="btn btn-ghost toggle-maint-btn" style="font-size:0.75rem; margin-top:0.4rem; width:100%;" title="Bloquear puesto para mantenimiento preventivo">
              ⚙️ Poner en Mantenimiento
            </button>
          `;
        }
      }

      card.className = `glass-card ws-card ${statusClass}`;
      card.innerHTML = `
        <div>
          <div class="ws-header">
            <span class="ws-code">${ws.code}</span>
            <span class="ws-badge badge-${statusClass}">${statusText}</span>
          </div>
          <p class="ws-desc">${ws.description || 'Puesto estándar para prácticas'}</p>
        </div>
        <div class="ws-footer-actions">
          ${mainBtnHtml}
          ${adminActionHtml}
        </div>
      `;

      if (isFree) {
        const btn = card.querySelector('.ws-action-btn');
        btn.addEventListener('click', () => {
          openBookingModal(ws, data.laboratory_name, startISO, endISO, durationMinutes);
        });
      }

      if (currentUser && currentUser.role === 'ADMIN') {
        const maintBtn = card.querySelector('.toggle-maint-btn');
        if (maintBtn) {
          maintBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const nextStatus = isMaint ? 'AVAILABLE' : 'MAINTENANCE';
            await toggleWorkstationMaintenance(ws.workstation_id, nextStatus);
          });
        }
      }

      workstationsGrid.appendChild(card);
    });
  }

  async function toggleWorkstationMaintenance(wsId, targetStatus) {
    try {
      const res = await fetch(`/api/workstations/${wsId}/status`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify({ status: targetStatus })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'No se pudo cambiar el estado del puesto');
      }
      if (targetStatus === 'AVAILABLE') {
        showToast('Mantenimiento Desactivado ✅', `Puesto #${wsId} restablecido a DISPONIBLE para reservas.`, 'success');
      } else {
        showToast('Mantenimiento Activado ⚠️', `Puesto #${wsId} puesto en MANTENIMIENTO técnico.`, 'warning');
      }
      checkAvailability(true);
    } catch (e) {
      showToast('Error', e.message, 'error');
    }
  }

  // ==========================================
  // MODAL DE RESERVA EN 1 CLIC
  // ==========================================
  function openBookingModal(ws, labName, startISO, endISO, durationMinutes) {
    modalStationInfo.textContent = `Puesto ${ws.code} • ${labName}`;
    bookingWsId.value = ws.workstation_id;
    bookingStartTime.value = startISO;
    bookingEndTime.value = endISO;

    summaryTimes.textContent = `${inputStartTime.value} - ${inputEndTime.value} (${inputDate.value})`;
    summaryDuration.textContent = `${durationMinutes} minutos (Turno confirmado)`;

    if (currentUser) {
      bookingAuthBox.classList.remove('hidden');
      bookingUnauthBox.classList.add('hidden');
      bookingUserName.textContent = currentUser.full_name;
      bookingUserDetails.textContent = `Código: ${currentUser.username} • Correo: ${currentUser.email}`;
      btnSubmitBooking.disabled = false;
      btnSubmitBooking.textContent = 'Confirmar Reserva (1 Clic)';
    } else {
      bookingAuthBox.classList.add('hidden');
      bookingUnauthBox.classList.remove('hidden');
      btnSubmitBooking.disabled = true;
      btnSubmitBooking.textContent = 'Inicia Sesión Primero';
    }

    modalBooking.classList.remove('hidden');
  }

  function closeBookingModal() {
    modalBooking.classList.add('hidden');
  }

  modalClose.addEventListener('click', closeBookingModal);
  modalCancelBtn.addEventListener('click', closeBookingModal);

  // Submit Reserva en 1 Clic
  formBooking.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!currentUser) {
      showToast('Atención', 'Debes iniciar sesión para reservar.', 'warning');
      closeBookingModal();
      openLoginModal();
      return;
    }

    // Payload: No necesita ni student_id ni student_email, el backend los extrae del token!
    const payload = {
      workstation_id: parseInt(bookingWsId.value),
      start_time: bookingStartTime.value,
      end_time: bookingEndTime.value
    };

    btnSubmitBooking.disabled = true;
    btnSubmitBooking.textContent = 'Confirmando en 1 Clic...';

    try {
      const res = await fetch('/api/reservations', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'No se pudo completar la reserva.');
      }

      closeBookingModal();
      showToast(
        '¡Reserva Exitosa en 1 Clic! 🎉',
        `Reserva #${data.id} registrada a nombre de ${currentUser.full_name}.`,
        'success'
      );

      checkAvailability();
    } catch (err) {
      showToast('Error en Reserva', err.message, 'error');
    } finally {
      btnSubmitBooking.disabled = false;
      btnSubmitBooking.textContent = 'Confirmar Reserva (1 Clic)';
    }
  });

  // ==========================================
  // VISTA ESTUDIANTE: MIS RESERVAS (/me)
  // ==========================================
  async function loadMyReservations() {
    if (!currentUser) return;

    myReservationsList.innerHTML = `
      <div class="empty-state">
        <p>Cargando tus reservas personales mediante token seguro...</p>
      </div>
    `;

    try {
      const res = await fetch('/api/reservations/me', { headers: getAuthHeaders() });
      if (!res.ok) throw new Error('No se pudieron obtener tus reservas');
      const reservations = await res.json();

      myReservationsList.innerHTML = '';
      if (reservations.length === 0) {
        myReservationsList.innerHTML = `
          <div class="empty-state">
            <p>No tienes reservas activas ni pasadas. ¡Explora el mapa y reserva un puesto en 1 clic!</p>
          </div>
        `;
        return;
      }

      reservations.forEach(r => {
        const isConfirmed = r.status === 'CONFIRMED';
        const card = document.createElement('div');
        card.className = `res-card ${isConfirmed ? 'confirmed' : 'cancelled'}`;

        const startFormatted = new Date(r.start_time).toLocaleString();
        const endFormatted = new Date(r.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        card.innerHTML = `
          <div class="res-info">
            <h4>
              Reserva #${r.id} (Puesto #${r.workstation_id})
              <span class="ws-badge badge-${isConfirmed ? 'available' : 'occupied'}">${r.status}</span>
            </h4>
            <div class="res-details">
              Horario: <span class="res-time-badge">${startFormatted} - ${endFormatted}</span>
            </div>
          </div>
          <div class="res-actions">
            ${isConfirmed ? `
              <button class="btn btn-outline cancel-my-res-btn" style="color:var(--status-occupied); border-color:var(--status-occupied-border);">
                Cancelar Reserva
              </button>
            ` : '<span style="font-size:0.8rem; color:var(--text-dim);">Turno Anulado</span>'}
          </div>
        `;

        if (isConfirmed) {
          const cancelBtn = card.querySelector('.cancel-my-res-btn');
          cancelBtn.addEventListener('click', () => cancelMyReservation(r.id));
        }

        myReservationsList.appendChild(card);
      });
    } catch (err) {
      myReservationsList.innerHTML = `
        <div class="empty-state" style="border-color: var(--status-occupied-border);">
          <p style="color: var(--status-occupied);">${err.message}</p>
        </div>
      `;
    }
  }

  async function cancelMyReservation(reservationId) {
    if (!confirm('¿Deseas cancelar esta reserva? Recuerda que se exige un mínimo de 30 minutos de antelación.')) {
      return;
    }

    try {
      const res = await fetch(`/api/reservations/${reservationId}/cancel`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({})
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'No se pudo cancelar la reserva.');
      }

      showToast('Reserva Cancelada', 'Tu puesto ha sido liberado exitosamente.', 'success');
      loadMyReservations();
      checkAvailability();
    } catch (err) {
      showToast('No se puede Cancelar', err.message, 'error');
    }
  }

  btnRefreshMyReservations.addEventListener('click', loadMyReservations);

  // ==========================================
  // VISTA ADMINISTRADOR: PANEL ADMIN
  // ==========================================
  async function loadAdminDashboard() {
    if (!currentUser || currentUser.role !== 'ADMIN') return;

    adminReservationsList.innerHTML = `
      <div class="empty-state">
        <p>Cargando todas las reservas del sistema con privilegios de Administrador...</p>
      </div>
    `;

    try {
      const res = await fetch('/api/reservations', { headers: getAuthHeaders() });
      if (!res.ok) throw new Error('Error al consultar reservas globales');
      const reservations = await res.json();

      adminReservationsList.innerHTML = '';
      if (reservations.length === 0) {
        adminReservationsList.innerHTML = `
          <div class="empty-state">
            <p>No hay reservas registradas en el sistema para este período.</p>
          </div>
        `;
        return;
      }

      reservations.forEach(r => {
        const isConfirmed = r.status === 'CONFIRMED';
        const card = document.createElement('div');
        card.className = `res-card ${isConfirmed ? 'confirmed' : 'cancelled'}`;

        const startFormatted = new Date(r.start_time).toLocaleString();
        const endFormatted = new Date(r.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        card.innerHTML = `
          <div class="res-info">
            <h4>
              Reserva #${r.id} • Estudiante: ${r.student_id}
              <span class="ws-badge badge-${isConfirmed ? 'available' : 'occupied'}">${r.status}</span>
            </h4>
            <div class="res-details">
              Puesto #${r.workstation_id} | Correo: ${r.student_email} | Horario: <span class="res-time-badge">${startFormatted} - ${endFormatted}</span>
            </div>
          </div>
          <div class="res-actions">
            ${isConfirmed ? `
              <button class="btn btn-outline admin-cancel-btn" style="color:var(--status-occupied); border-color:var(--status-occupied-border);">
                ⚠️ Anulación Administrativa
              </button>
            ` : '<span style="font-size:0.8rem; color:var(--text-dim);">Cancelada</span>'}
          </div>
        `;

        if (isConfirmed) {
          const cancelBtn = card.querySelector('.admin-cancel-btn');
          cancelBtn.addEventListener('click', () => adminCancelReservation(r.id));
        }

        adminReservationsList.appendChild(card);
      });
    } catch (err) {
      adminReservationsList.innerHTML = `
        <div class="empty-state" style="border-color: var(--status-occupied-border);">
          <p style="color: var(--status-occupied);">${err.message}</p>
        </div>
      `;
    }
  }

  async function adminCancelReservation(reservationId) {
    if (!confirm('Como Administrador, vas a anular esta reserva por emergencia o mantenimiento (sin restricción de tiempo). ¿Continuar?')) {
      return;
    }

    try {
      const res = await fetch(`/api/reservations/${reservationId}/cancel`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({})
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'Fallo al anular reserva');

      showToast('Anulación Exitosa', `Reserva #${reservationId} anulada por administración.`, 'warning');
      loadAdminDashboard();
      checkAvailability();
    } catch (err) {
      showToast('Error', err.message, 'error');
    }
  }

  btnRefreshAdminReservations.addEventListener('click', loadAdminDashboard);

  // ==========================================
  // SEMBRAR DATOS DEMO
  // ==========================================
  btnSeedData.addEventListener('click', async () => {
    btnSeedData.disabled = true;
    try {
      const res = await fetch('/api/demo/seed', { method: 'POST' });
      const data = await res.json();
      showToast('Datos Demo y Usuarios', data.message, 'success');
      await loadLaboratories();
    } catch (err) {
      showToast('Error', 'No se pudieron sembrar los datos: ' + err.message, 'error');
    } finally {
      btnSeedData.disabled = false;
    }
  });

  // Filter Listeners
  filterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    checkAvailability();
  });
  selectLab.addEventListener('change', checkAvailability);

  // ==========================================
  // TOAST NOTIFICATIONS
  // ==========================================
  function showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
    `;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideIn 0.25s reverse';
      setTimeout(() => toast.remove(), 250);
    }, 4500);
  }

  // ==========================================
  // REAL-TIME SYNCHRONIZATION (Server-Sent Events)
  // ==========================================
  let sseSource = null;

  function initSSE() {
    if (sseSource) {
      try { sseSource.close(); } catch (_) {}
    }

    const sseIndicator = document.getElementById('sse-indicator');
    const sseStatusText = document.getElementById('sse-status-text');

    try {
      sseSource = new EventSource('/api/events');

      sseSource.onopen = () => {
        if (sseIndicator) {
          sseIndicator.className = 'sse-pill sse-connected';
          sseIndicator.title = 'Conexión en tiempo real activa (SSE)';
        }
        if (sseStatusText) sseStatusText.textContent = 'En Vivo';
      };

      sseSource.onerror = () => {
        if (sseIndicator) {
          sseIndicator.className = 'sse-pill sse-reconnecting';
          sseIndicator.title = 'Reconectando con el servidor en tiempo real...';
        }
        if (sseStatusText) sseStatusText.textContent = 'Reconectando...';
      };

      // Workstation occupied event (alguien reservó en tiempo real)
      sseSource.addEventListener('workstation_occupied', (e) => {
        try {
          const payload = JSON.parse(e.data);
          // Refrescar disponibilidad en cuadrícula si pertenece al laboratorio actual
          if (!selectLab.value || String(payload.laboratory_id) === String(selectLab.value)) {
            checkAvailability(true);
          }
          showToast('Actualización en Vivo 🔴', payload.message || `Puesto #${payload.workstation_id} reservado por otro usuario.`, 'warning');
          if (currentUser && currentUser.role === 'ADMIN' && sectionAdminDashboard && !sectionAdminDashboard.classList.contains('hidden')) {
            loadAdminDashboard();
          }
        } catch (err) {
          console.error('Error procesando workstation_occupied:', err);
        }
      });

      // Workstation freed event (alguien canceló una reserva)
      sseSource.addEventListener('workstation_freed', (e) => {
        try {
          const payload = JSON.parse(e.data);
          if (!selectLab.value || String(payload.laboratory_id) === String(selectLab.value)) {
            checkAvailability(true);
          }
          showToast('Puesto Liberado en Vivo 🟢', payload.message || `Puesto #${payload.workstation_id} vuelve a estar disponible.`, 'success');
          if (currentUser && currentUser.role === 'ADMIN' && sectionAdminDashboard && !sectionAdminDashboard.classList.contains('hidden')) {
            loadAdminDashboard();
          }
          if (currentUser && currentUser.role === 'STUDENT' && sectionMyReservations && !sectionMyReservations.classList.contains('hidden')) {
            loadMyReservations();
          }
        } catch (err) {
          console.error('Error procesando workstation_freed:', err);
        }
      });

      // Workstation status changed (admin activó o desactivó mantenimiento)
      sseSource.addEventListener('workstation_status_changed', (e) => {
        try {
          const payload = JSON.parse(e.data);
          if (!selectLab.value || String(payload.laboratory_id) === String(selectLab.value)) {
            checkAvailability(true);
          }
          const isMaint = payload.status === 'MAINTENANCE';
          showToast(
            isMaint ? 'Mantenimiento en Vivo ⚙️' : 'Puesto Habilitado en Vivo ✅',
            payload.message || `Puesto #${payload.workstation_id} ahora está ${payload.status}`,
            isMaint ? 'warning' : 'success'
          );
        } catch (err) {
          console.error('Error procesando workstation_status_changed:', err);
        }
      });

    } catch (err) {
      console.error('No se pudo inicializar EventSource SSE:', err);
    }
  }

  // Carga inicial de autenticación y conexión en tiempo real
  initAuth();
  initSSE();
});
