const MIN_DATE = '2026-01-01';

const stateFilter = document.getElementById('stateFilter');
const themeFilter = document.getElementById('themeFilter');
const startDate = document.getElementById('startDate');
const endDate = document.getElementById('endDate');
const hidePaywall = document.getElementById('hidePaywall');
const newsList = document.getElementById('newsList');
const newsCount = document.getElementById('newsCount');
const activeFilterInfo = document.getElementById('activeFilterInfo');
const sourceList = document.getElementById('sourceList');

const data = await Promise.all([
  fetch('./data/news.json').then((r) => r.json()),
  fetch('./data/sources.json').then((r) => r.json())
]);

const rawNews = data[0].items || [];
const news = rawNews.filter((n) => n.published_at >= MIN_DATE);
const sources = data[1].sources.filter((s) => s.active);

function unique(arr) {
  return [...new Set(arr)].sort();
}

function buildFilters() {
  const states = unique(news.map((n) => n.state));
  const themes = unique(news.flatMap((n) => n.themes));

  stateFilter.innerHTML = ['<option value="">Todos</option>', ...states.map((s) => `<option value="${s}">${s}</option>`)].join('');
  themeFilter.innerHTML = ['<option value="">Todos</option>', ...themes.map((t) => `<option value="${t}">${t}</option>`)].join('');
}

function renderSources() {
  sourceList.innerHTML = sources
    .map((s) => `<li><strong>${s.name}</strong> (${s.state}) • <a href="${s.url}" target="_blank" rel="noreferrer">${s.url}</a></li>`)
    .join('');
}

function card(item) {
  const locked = item.paywall ? ' 🔒' : '';
  return `
  <article class="news-item">
    <p>✏️ <strong>${item.title}</strong></p>
    <p>👉🏾 ${item.summary}</p>
    <p>📰 ${item.source}</p>
    <p>🔗 <a href="${item.url}" target="_blank" rel="noreferrer">${item.url}</a><span class="paywall">${locked}</span></p>
    <p class="meta">${item.published_at} • ${item.state} • ${item.themes.join(', ')}</p>
  </article>`;
}

function applyFilters() {
  const state = stateFilter.value;
  const theme = themeFilter.value;
  const start = startDate.value || MIN_DATE;
  const end = endDate.value || '9999-12-31';

  const filtered = news.filter((n) => {
    const okState = !state || n.state === state;
    const okTheme = !theme || n.themes.includes(theme);
    const okDate = n.published_at >= start && n.published_at <= end && n.published_at >= MIN_DATE;
    const okPaywall = !hidePaywall.checked || !n.paywall;
    return okState && okTheme && okDate && okPaywall;
  });

  newsCount.textContent = `${filtered.length} notícia(s) encontrada(s)`;
  const details = [
    `Base carregada: ${rawNews.length} notícia(s)`,
    `Recorte mínimo: ${MIN_DATE} (antes disso é removido)`,
    `Data inicial ativa: ${start}`,
    `Data final ativa: ${end === '9999-12-31' ? 'sem limite' : end}`,
    `Estado: ${state || 'todos'}`,
    `Tema: ${theme || 'todos'}`,
    `Paywall: ${hidePaywall.checked ? 'ocultando' : 'mostrando'}`
  ];
  activeFilterInfo.textContent = details.join(' • ');
  newsList.innerHTML = filtered.length ? filtered.map(card).join('') : '<p>Nenhuma notícia encontrada com os filtros atuais.</p>';
}

[stateFilter, themeFilter, startDate, endDate, hidePaywall].forEach((el) => el.addEventListener('change', applyFilters));

buildFilters();
renderSources();
applyFilters();
