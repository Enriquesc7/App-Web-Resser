/**
 * receipt_upload.js
 * -----------------
 * Vanilla JS state machine for the receipt scanner page.
 * Views: upload (A) | loading (B) | results (C)
 * History section is always visible below the active view.
 */

'use strict';

// ── Waste type colours (mirrors design_system.css tokens) ──────────────────
const WASTE_COLORS = {
  plastique: '#2563EB',
  verre:     '#14B8A6',
  carton:    '#A16207',
  papier:    '#A16207',
  mixte:     '#D97706',
  aucun:     '#65A30D',
  metal:     '#F59E0B',
  inconnu:   '#A1A19A',
};

const WASTE_LABELS = {
  plastique: 'Plastique',
  verre:     'Verre',
  carton:    'Carton',
  papier:    'Papier',
  mixte:     'Mixte',
  aucun:     'Sans emballage',
  metal:     'Métal',
  inconnu:   'Inconnu',
};

// ── Module-level state ─────────────────────────────────────────────────────
const state = {
  currentFile:   null,
  currentScanId: null,
};

// ── DOM references ─────────────────────────────────────────────────────────
let viewUpload, viewLoading, viewResults;
let uploadHero, previewContainer, previewImg;
let inputCamera, inputGallery;
let btnCamera, btnGallery, btnAnalyze, btnChange, btnNewScan;
let resultsContent;
let historyList;

// ── Initialisation ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  viewUpload  = document.getElementById('view-upload');
  viewLoading = document.getElementById('view-loading');
  viewResults = document.getElementById('view-results');

  uploadHero        = document.getElementById('upload-hero');
  previewContainer  = document.getElementById('preview-container');
  previewImg        = document.getElementById('preview-img');

  inputCamera  = document.getElementById('input-camera');
  inputGallery = document.getElementById('input-gallery');
  btnCamera    = document.getElementById('btn-camera');
  btnGallery   = document.getElementById('btn-gallery');
  btnAnalyze   = document.getElementById('btn-analyze');
  btnChange    = document.getElementById('btn-change');
  btnNewScan   = document.getElementById('btn-new-scan');

  resultsContent = document.getElementById('results-content');
  historyList    = document.getElementById('history-list');

  // Button wiring
  btnCamera.addEventListener('click',  () => inputCamera.click());
  btnGallery.addEventListener('click', () => inputGallery.click());
  inputCamera.addEventListener('change',  handleFileSelect);
  inputGallery.addEventListener('change', handleFileSelect);
  btnAnalyze.addEventListener('click',  analyzeReceipt);
  btnChange.addEventListener('click',   resetToUploadHero);
  btnNewScan.addEventListener('click',  resetToUploadView);

  loadHistory();
});

// ── View transitions ───────────────────────────────────────────────────────
function showView(name) {
  viewUpload.classList.toggle('hidden',  name !== 'upload');
  viewLoading.classList.toggle('hidden', name !== 'loading');
  viewResults.classList.toggle('hidden', name !== 'results');
  scrollSection(0);
}

function scrollSection(top) {
  const section = document.getElementById('section');
  if (section) section.scrollTop = top;
}

// ── File selection ─────────────────────────────────────────────────────────
function handleFileSelect(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;

  const err = validateFile(file);
  if (err) {
    showToast(err);
    e.target.value = '';
    return;
  }

  state.currentFile = file;
  showPreview(file);
}

function validateFile(file) {
  if (!file.type.startsWith('image/')) {
    return 'Format non supporté. Veuillez sélectionner une image.';
  }
  if (file.size > 8 * 1024 * 1024) {
    return 'Fichier trop volumineux (max 8 Mo).';
  }
  return null;
}

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    uploadHero.classList.add('hidden');
    previewContainer.classList.remove('hidden');
  };
  reader.readAsDataURL(file);
}

// ── Upload and analyse ─────────────────────────────────────────────────────
async function analyzeReceipt() {
  if (!state.currentFile) return;

  showView('loading');
  animateLoadingSteps();

  const formData = new FormData();
  formData.append('file', state.currentFile);

  let data;
  try {
    const resp = await fetch('/receipt/upload', { method: 'POST', body: formData });
    if (!resp.ok) {
      let detail = 'Erreur lors de l\'analyse.';
      try { detail = (await resp.json()).detail || detail; } catch (_) {}
      showToast(detail);
      showView('upload');
      return;
    }
    data = await resp.json();
  } catch (err) {
    showToast('Erreur réseau. Vérifiez votre connexion.');
    showView('upload');
    return;
  }

  state.currentScanId = data.scan_id;
  renderResults(data);
  showView('results');
  loadHistory();
}

// ── Loading step animation ─────────────────────────────────────────────────
function animateLoadingSteps() {
  const steps = document.querySelectorAll('.loading-step');
  let i = 0;
  const next = () => {
    if (i > 0 && steps[i - 1]) {
      steps[i - 1].classList.remove('active');
      steps[i - 1].classList.add('done');
    }
    if (i < steps.length) {
      steps[i].classList.add('active');
      i++;
      setTimeout(next, 900);
    }
  };
  steps.forEach(s => { s.classList.remove('active', 'done'); });
  next();
}

// ── Result rendering ───────────────────────────────────────────────────────
function renderResults(data) {
  const items = data.items || [];

  // Summary stats
  const totalItems    = items.length;
  const totalPlastic  = items.reduce((s, it) => s + (it.weight_grams || 0), 0);
  const recyclable    = items.filter(it => it.recyclable === true).length;

  // Receipt thumbnail
  const thumbHtml = data.image_url
    ? `<img src="${esc(data.image_url)}" class="image-preview" style="max-height:160px;margin-bottom:12px;" alt="Ticket">`
    : '';

  // Waste bar chart
  const wasteGroups = {};
  items.forEach(it => {
    const wt = it.waste_type || 'inconnu';
    wasteGroups[wt] = (wasteGroups[wt] || 0) + 1;
  });

  let chartHtml = '';
  if (totalItems > 0) {
    const barSegments = Object.entries(wasteGroups).map(([wt, count]) => {
      const pct = ((count / totalItems) * 100).toFixed(1);
      const color = WASTE_COLORS[wt] || WASTE_COLORS.inconnu;
      return `<div class="waste-bar-segment" style="width:${pct}%;background:${color};"></div>`;
    }).join('');

    const legendItems = Object.entries(wasteGroups).map(([wt, count]) => {
      const color  = WASTE_COLORS[wt] || WASTE_COLORS.inconnu;
      const label  = WASTE_LABELS[wt] || wt;
      return `<span class="waste-legend-item">
        <span class="waste-legend-dot" style="background:${color};"></span>
        ${esc(label)} (${count})
      </span>`;
    }).join('');

    chartHtml = `
      <div class="card" style="margin-bottom:12px;">
        <p class="section-label" style="margin-bottom:10px;">Composition des déchets</p>
        <div class="waste-bar">${barSegments}</div>
        <div class="waste-legend">${legendItems}</div>
      </div>`;
  }

  // Per-item cards
  const itemCardsHtml = items.length === 0
    ? `<div class="empty-state" style="padding:32px 0;">
        <p style="color:var(--neutral-400);font-size:0.875rem;">Aucun produit détecté dans ce ticket.</p>
       </div>`
    : items.map(itemCardHtml).join('');

  resultsContent.innerHTML = `
    ${thumbHtml}
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">${totalItems}</div>
        <div class="stat-label">Produits détectés</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${totalPlastic.toFixed(0)}<small style="font-size:0.75rem;font-weight:500;">g</small></div>
        <div class="stat-label">Plastique estimé</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${recyclable}</div>
        <div class="stat-label">Recyclables</div>
      </div>
    </div>
    ${chartHtml}
    <p class="section-label" style="margin-bottom:8px;">Produits (${totalItems})</p>
    ${itemCardsHtml}
  `;
}

function itemCardHtml(item) {
  const name = esc(item.normalized_name || item.raw_line || '—');
  const brand = item.brand ? `<span style="font-size:0.8125rem;color:var(--neutral-400);">${esc(item.brand)}</span>` : '';
  const qty   = (item.quantity && item.quantity > 1) ? `<span class="badge" style="background:var(--neutral-100);color:var(--neutral-600);">×${item.quantity}</span>` : '';
  const size  = item.size  ? `<span style="font-size:0.75rem;color:var(--neutral-400);">${esc(item.size)}</span>` : '';
  const price = (item.line_total != null)
    ? `<span class="item-card-price">${item.line_total.toFixed(2)} €</span>`
    : '';

  const wt          = item.waste_type || 'inconnu';
  const wasteBadge  = wasteBadgeHtml(wt);
  const recBadge    = recyclableBadgeHtml(item.recyclable);
  const reviewBadge = item.needs_review
    ? `<span class="badge badge-needs-review">À vérifier</span>`
    : '';

  const conf = item.confidence != null ? item.confidence : 0;
  const confColor = conf >= 0.9 ? 'var(--resser-500)' : (conf >= 0.65 ? 'var(--amber)' : 'var(--red)');
  const confBar = `
    <div class="item-card-conf">
      <div class="confidence-bar" style="flex:1;">
        <div class="confidence-bar-fill" style="width:${(conf*100).toFixed(0)}%;background:${confColor};"></div>
      </div>
      <span>${(conf*100).toFixed(0)}%</span>
    </div>`;

  return `
    <div class="item-card">
      <div class="item-card-header">
        <div>
          <div class="item-card-name">${name}</div>
          ${brand}
        </div>
        ${price}
      </div>
      <div class="item-card-meta">
        ${wasteBadge}${recBadge}${reviewBadge}${qty}${size}
      </div>
      ${confBar}
    </div>`;
}

function wasteBadgeHtml(wasteType) {
  const classes = {
    plastique: 'badge-plastic',
    verre:     'badge-glass',
    carton:    'badge-paper',
    papier:    'badge-paper',
    mixte:     'badge-paper',
    aucun:     'badge-composting',
    metal:     '',
    inconnu:   'badge-needs-review',
  };
  const cls   = classes[wasteType] || 'badge-needs-review';
  const label = WASTE_LABELS[wasteType] || wasteType;
  return cls
    ? `<span class="badge ${cls}">${esc(label)}</span>`
    : `<span class="badge" style="background:#FEF3C7;color:#92400E;">${esc(label)}</span>`;
}

function recyclableBadgeHtml(recyclable) {
  if (recyclable === true)  return `<span class="badge badge-recyclable">Recyclable</span>`;
  if (recyclable === false) return `<span class="badge badge-non-recyclable">Non recyclable</span>`;
  return '';
}

// ── History ────────────────────────────────────────────────────────────────
async function loadHistory() {
  try {
    const resp = await fetch('/receipt/scans');
    if (!resp.ok) return;
    const scans = await resp.json();
    renderHistory(scans);
  } catch (_) {
    // Silently ignore — history is non-critical
  }
}

function renderHistory(scans) {
  if (!scans || scans.length === 0) {
    historyList.innerHTML = `
      <div style="padding:24px 0;text-align:center;">
        <p style="font-size:0.875rem;color:var(--neutral-400);">Aucun ticket scanné pour l'instant.</p>
      </div>`;
    return;
  }

  historyList.innerHTML = scans.map(scan => {
    const thumb = scan.image_url
      ? `<img src="${esc(scan.image_url)}" class="history-thumbnail" alt="Ticket" loading="lazy">`
      : `<div class="history-thumbnail-placeholder">
           <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2h16v20H4z"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="12" y2="14"/></svg>
         </div>`;

    const date    = formatDate(scan.created_at);
    const plastic = scan.total_plastic_grams > 0
      ? `${scan.total_plastic_grams.toFixed(0)} g plastique`
      : 'Pas de plastique estimé';

    return `
      <div class="list-item" style="cursor:pointer;" onclick="loadScan(${scan.scan_id})">
        ${thumb}
        <div class="list-item-content">
          <div class="list-item-title">${scan.item_count} produit${scan.item_count !== 1 ? 's' : ''}</div>
          <div class="list-item-subtitle">${date} · ${plastic}</div>
        </div>
        <div class="list-item-trail">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </div>
      </div>`;
  }).join('');
}

// ── Load a past scan ───────────────────────────────────────────────────────
async function loadScan(scanId) {
  showView('loading');
  animateLoadingSteps();

  try {
    const resp = await fetch(`/receipt/${scanId}`);
    if (!resp.ok) {
      showToast('Scan introuvable.');
      showView('upload');
      return;
    }
    const data = await resp.json();
    state.currentScanId = scanId;
    renderResults(data);
    showView('results');
  } catch (_) {
    showToast('Erreur lors du chargement du scan.');
    showView('upload');
  }
}

// ── Reset helpers ──────────────────────────────────────────────────────────
function resetToUploadHero() {
  state.currentFile = null;
  inputCamera.value  = '';
  inputGallery.value = '';
  previewContainer.classList.add('hidden');
  uploadHero.classList.remove('hidden');
}

function resetToUploadView() {
  resetToUploadHero();
  showView('upload');
}

// ── Toast ──────────────────────────────────────────────────────────────────
function showToast(message, duration) {
  duration = duration || 4000;
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, duration);
}

// ── Utilities ──────────────────────────────────────────────────────────────
function esc(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;')
    .replace(/'/g,  '&#39;');
}

function formatDate(iso) {
  if (!iso) return '';
  const date = new Date(iso);
  const now  = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours   = Math.floor(diff / 3600000);
  const days    = Math.floor(diff / 86400000);

  if (minutes < 2)  return 'À l\'instant';
  if (minutes < 60) return `Il y a ${minutes} min`;
  if (hours < 24)   return `Il y a ${hours} h`;
  if (days === 1)   return 'Hier';

  const months = ['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.'];
  return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
}
