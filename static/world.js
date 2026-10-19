(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const SHOWN_FEEDS = 6;
  let data = null, cities = [], byRank = new Map(), sel = 2, filter = 'all';
  const dots = new Map(), rows = new Map();

  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const popStr = p => (p / 1e6).toFixed(1) + ' M';
  const feedsStr = n => n + (n === 1 ? ' feed' : ' feeds');
  const shown = c => filter === 'all' || (filter === 'yes' ? c.feeds.length > 0 : c.feeds.length === 0);

  function toast(msg) { const t = $('toast'); t.textContent = msg; t.hidden = false; setTimeout(() => { t.hidden = true; }, 5000); }

  function buildMap() {
    const map = $('map'), maxP = Math.max(...cities.map(c => c.population));
    // Smallest cities last so they stay clickable on top of the big ones.
    for (const c of cities.slice().sort((a, b) => b.population - a.population)) {
      const size = Math.round(6 + 12 * Math.sqrt(c.population / maxP));
      const b = el('button', 'city-dot');
      b.type = 'button';
      b.style.left = (c.x / data.map.width * 100) + '%';
      b.style.top = (c.y / data.map.height * 100) + '%';
      b.classList.toggle('has', c.feeds.length > 0);
      b.classList.toggle('ingested', c.ingested.length > 0);
      b.setAttribute('aria-label', `${c.name}, ${c.feeds.length ? feedsStr(c.feeds.length) : 'no open feed'}`);
      const i = el('i'); i.style.width = i.style.height = size + 'px';
      b.append(i, el('span', 'tip', c.name));
      b.addEventListener('click', () => select(c.rank));
      map.append(b);
      dots.set(c.rank, { b, i, size });
    }
  }

  function buildGrid() {
    const grid = $('grid');
    for (const c of cities) {
      const b = el('button', 'row');
      b.type = 'button';
      const body = el('span', 'c');
      body.append(el('span', 'n', c.name), el('span', 'm', `${c.cc} · ${popStr(c.population)}`));
      const n = c.feeds.length;
      const pill = el('span', 'pill' + (n ? ' ok' : ''), n ? feedsStr(n) : '—');
      b.append(el('span', 'r', String(c.rank)), body, pill);
      b.addEventListener('click', () => select(c.rank, true));
      grid.append(b);
      rows.set(c.rank, b);
    }
  }

  function renderDetail() {
    const c = byRank.get(sel); if (!c) return;
    const n = c.feeds.length, ing = c.ingested.length > 0;
    $('d-rank').textContent = `No. ${c.rank} by population`;
    const pill = $('d-pill');
    pill.textContent = n ? (ing ? 'Ingested' : 'Ready to ingest') : (ing ? 'Ingested' : 'No open feed');
    pill.className = 'pill' + (ing ? ' ingested' : n ? ' ok' : '');
    $('d-name').textContent = c.name;
    $('d-meta').textContent = `${c.country} · ${popStr(c.population)} people`;
    $('d-has').hidden = !(n || ing);
    $('d-none').hidden = !!(n || ing);
    if (!(n || ing)) return;
    $('d-count').textContent = n ? `${n} keyless ${n === 1 ? 'feed' : 'feeds'} within ${data.radius_km} km` : `Ingested locally: ${c.ingested.join(', ')}`;
    const list = $('d-feeds'); list.replaceChildren(); list.hidden = !n;
    for (const f of c.feeds.slice(0, SHOWN_FEEDS)) {
      const li = el('li'); li.append(el('b', '', f.agency), el('small', '', `${f.id} · ${f.km} km`)); list.append(li);
    }
    if (n > SHOWN_FEEDS) list.append(el('li', 'more', `+ ${n - SHOWN_FEEDS} more in the registry`));
    $('d-cmd').textContent = ing ? c.ingested[0] : c.feeds[0].id;
    const open = $('d-open'); open.hidden = !ing;
    if (ing) open.href = '/demo?city=' + encodeURIComponent(c.ingested[0]);
  }

  function render() {
    for (const [rank, d] of dots) {
      const c = byRank.get(rank), on = rank === sel;
      d.b.setAttribute('aria-pressed', String(on));
      d.b.classList.toggle('faded', !shown(c));
      d.i.style.width = d.i.style.height = (on ? d.size + 6 : d.size) + 'px';
    }
    for (const [rank, b] of rows) {
      b.hidden = !shown(byRank.get(rank));
      b.setAttribute('aria-pressed', String(rank === sel));
    }
    for (const b of document.querySelectorAll('[data-filter]')) b.setAttribute('aria-pressed', String(b.dataset.filter === filter));
    const s = data.summary;
    $('list-title').textContent = filter === 'all' ? `All ${s.cities}, by population.` : filter === 'yes' ? `${s.covered} cities ready to go.` : `${s.uncovered} cities waiting for open data.`;
    renderDetail();
  }

  function select(rank, reveal) {
    sel = rank; render();
    const url = new URL(location.href); url.searchParams.set('city', String(rank)); history.replaceState(null, '', url);
    if (reveal) {
      const r = $('detail').getBoundingClientRect();
      if (r.top < 0 || r.top > innerHeight) $('detail').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    }
  }

  async function load() {
    try {
      const r = await fetch('/world/cities');
      if (!r.ok) throw Error(`World data unavailable (${r.status})`);
      data = await r.json();
      cities = data.cities;
      byRank = new Map(cities.map(c => [c.rank, c]));
      const s = data.summary;
      $('stat-total').textContent = s.cities;
      $('stat-covered').textContent = s.covered;
      $('stat-feeds').textContent = s.feeds;
      $('stat-uncovered').textContent = s.uncovered;
      $('radius').textContent = $('radius-foot').textContent = data.radius_km;
      const asked = Number(new URLSearchParams(location.search).get('city'));
      sel = byRank.has(asked) ? asked : (cities.find(c => c.ingested.length) || cities[0]).rank;
      buildMap(); buildGrid();
      for (const b of document.querySelectorAll('[data-filter]')) b.addEventListener('click', () => { filter = b.dataset.filter; render(); });
      render();
    } catch (e) {
      $('d-rank').textContent = 'Unavailable';
      toast(e.message);
    }
  }

  load();
})();
