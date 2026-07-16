/**
 * waste_taxonomy.js
 * ------------------
 * Shared waste_type → color/label mapping, used by both receipt_upload.js
 * (per-item badges) and home_waste_summary.js (cumulative panel), so the
 * two views can't drift out of sync. Must be loaded before both.
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
  inconnu:   'Non classifié',
};
