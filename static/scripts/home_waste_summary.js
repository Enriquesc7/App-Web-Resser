/**
 * home_waste_summary.js
 * ----------------------
 * Populates the "Vos déchets cumulés" card on the home page from
 * GET /receipt/summary. Ownership (guest bucket vs logged-in user) is
 * resolved server-side, same rule as /receipt/scans and /receipt/{scan_id}.
 */

'use strict';

document.addEventListener('DOMContentLoaded', loadWasteSummary);

async function loadWasteSummary() {
  const content = document.getElementById('waste-summary-content');
  if (!content) return;

  let data;
  try {
    const resp = await fetch('/receipt/summary');
    if (!resp.ok) throw new Error('bad status');
    data = await resp.json();
  } catch (_) {
    content.innerHTML = `
      <p style="font-size:0.875rem;color:var(--neutral-400);text-align:center;padding:8px 0;">
        Impossible de charger vos statistiques.
      </p>`;
    return;
  }

  if (!data.total_scans) {
    content.innerHTML = `
      <div style="padding:8px 0;text-align:center;">
        <p style="font-size:0.875rem;color:var(--neutral-600);margin:0 0 8px;">
          Scannez votre premier ticket pour voir votre impact ici.
        </p>
        <a href="/receipt" class="btn-secondary" style="display:inline-block;padding:6px 14px;font-size:0.8125rem;">
          Scanner un ticket
        </a>
      </div>`;
    return;
  }

  content.innerHTML = renderSummary(data);
}

function renderSummary(data) {
  const co2Value = data.total_co2_kg != null ? data.total_co2_kg.toFixed(2) : '—';

  const statsHtml = `
    <div class="stats-grid" style="grid-template-columns: repeat(2, minmax(0, 1fr));">
      <div class="stat-card">
        <div class="stat-value">${data.total_grams.toFixed(0)}<small style="font-size:0.75rem;font-weight:500;">g</small></div>
        <div class="stat-label">Déchets cumulés</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:2px;">
          ${leafIconSvg()}<span>${co2Value}</span><small style="font-size:0.75rem;font-weight:500;">kg CO2e</small>
        </div>
        <div class="stat-label">Impact estimé</div>
      </div>
    </div>`;

  const breakdown = data.breakdown || [];
  const barSegments = breakdown.map(b => {
    const color = WASTE_COLORS[b.waste_type] || WASTE_COLORS.inconnu;
    return `<div class="waste-bar-segment" style="width:${b.pct}%;background:${color};"></div>`;
  }).join('');

  const legendItems = breakdown.map(b => {
    const color = WASTE_COLORS[b.waste_type] || WASTE_COLORS.inconnu;
    return `<span class="waste-legend-item">
      <span class="waste-legend-dot" style="background:${color};"></span>
      ${esc(b.label)} (${b.grams.toFixed(0)} g)
    </span>`;
  }).join('');

  const chartHtml = `
    <div style="margin-top:12px;">
      <div class="waste-bar">${barSegments}</div>
      <div class="waste-legend">${legendItems}</div>
    </div>`;

  const unclassifiedNote = data.unclassified_grams > 0
    ? `<p style="font-size:0.75rem;color:var(--neutral-400);margin:10px 0 0;line-height:1.4;">
        « Non classifié » (${data.unclassified_grams.toFixed(0)} g) n'est pas inclus dans l'estimation CO2 ci-dessus.
       </p>`
    : '';

  return statsHtml + chartHtml + unclassifiedNote;
}

function leafIconSvg() {
  return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M11 20A7 7 0 019.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/>
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
  </svg>`;
}

function esc(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
