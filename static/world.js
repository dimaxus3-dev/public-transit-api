(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const DARK_STYLE = 'https://tiles.openfreemap.org/styles/dark';
  const WORLD = { center: [10, 25], zoom: 1.7 };
  const LINES_MIN_ZOOM = 5;
  const SHOWN_FEEDS = 6;
  const MODE_COLORS = { metro: '#0a84ff', rail: '#bf5af2', tram: '#ff9f0a', bus: '#64d2ff', ferry: '#5ac8fa', cable: '#ff375f' };
  const MODE_ORDER = { bus: 1, ferry: 2, tram: 3, cable: 3, rail: 4, metro: 5 };
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let data = null, cities = [], byRank = new Map(), sel = 2, filter = 'all';
  let map = null, mapReady = false, ingestedFeeds = [];
  const rows = new Map(), linesLoaded = new Map();

  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const popStr = p => (p / 1e6).toFixed(1) + ' M';
  const feedsStr = n => n + (n === 1 ? ' feed' : ' feeds');
  const shown = c => filter === 'all' || (filter === 'yes' ? c.feeds.length > 0 : c.feeds.length === 0);

  function toast(msg) { const t = $('toast'); t.textContent = msg; t.hidden = false; setTimeout(() => { t.hidden = true; }, 5000); }

  // Route colours from the feed, unless missing or too dark to read on the dark map.
  function routeColor(p) {
    const raw = p.color;
    if (typeof raw === 'string' && /^#[0-9a-fA-F]{6}$/.test(raw)) {
      const [r, g, b] = [1, 3, 5].map(i => parseInt(raw.slice(i, i + 2), 16));
      if (0.2126 * r + 0.7152 * g + 0.0722 * b > 60) return raw;
    }
    return MODE_COLORS[p.mode] || '#9fd6df';
  }

  // ── map ──────────────────────────────────────────────────────────────────
  function citiesGeoJSON() {
    const maxP = Math.max(...cities.map(c => c.population));
    return {
      type: 'FeatureCollection',
      features: cities.map(c => ({
        type: 'Feature', id: c.rank,
        geometry: { type: 'Point', coordinates: [c.lon, c.lat] },
        properties: { rank: c.rank, name: c.name, size: 3 + 6 * Math.sqrt(c.population / maxP), has: c.feeds.length > 0, ingested: c.ingested.length > 0 }
      }))
    };
  }

  function buildMap() {
    if (!window.maplibregl) { toast('Map library unavailable'); return; }
    map = new maplibregl.Map({ container: 'map', style: DARK_STYLE, center: WORLD.center, zoom: WORLD.zoom, attributionControl: { compact: true }, pitchWithRotate: false, dragRotate: false, cooperativeGestures: matchMedia('(pointer: coarse)').matches });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    if (window.ResizeObserver) new ResizeObserver(() => map.resize()).observe($('map'));
    map.on('style.load', () => { try { map.setProjection({ type: 'globe' }); } catch (_) { /* older renderer: stay flat */ } });
    map.on('error', e => { if (!mapReady) toast(e?.error?.message || 'Map tiles unavailable'); });
    map.on('load', () => {
      map.addSource('cities', { type: 'geojson', data: citiesGeoJSON() });
      map.addLayer({
        id: 'cities', type: 'circle', source: 'cities',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, ['get', 'size'], 6, ['*', ['get', 'size'], 1.6], 10, ['*', ['get', 'size'], 1.2]],
          'circle-color': ['case', ['get', 'has'], '#30d158', '#636366'],
          'circle-opacity': ['interpolate', ['linear'], ['zoom'], 8, ['case', ['boolean', ['feature-state', 'faded'], false], 0.15, 0.95], 11, ['case', ['boolean', ['feature-state', 'faded'], false], 0.1, 0.35]],
          'circle-stroke-color': ['case', ['boolean', ['feature-state', 'selected'], false], '#ffffff', ['get', 'ingested'], '#2997ff', 'rgba(0,0,0,0.6)'],
          'circle-stroke-width': ['case', ['boolean', ['feature-state', 'selected'], false], 3, ['get', 'ingested'], 2, 1],
          'circle-stroke-opacity': ['case', ['boolean', ['feature-state', 'faded'], false], 0.15, 1]
        }
      });
      // Ingested feeds outside the top 100 (e.g. Vienna) still get a marker.
      map.addSource('feeds', { type: 'geojson', data: { type: 'FeatureCollection', features: ingestedFeeds.filter(f => !cities.some(c => c.ingested.includes(f.feed))).map(f => ({ type: 'Feature', geometry: { type: 'Point', coordinates: [f.lon, f.lat] }, properties: { feed: f.feed, name: f.city } })) } });
      map.addLayer({ id: 'feeds', type: 'circle', source: 'feeds', paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, 4, 8, 7], 'circle-color': 'rgba(41,151,255,0.25)', 'circle-stroke-color': '#2997ff', 'circle-stroke-width': 2, 'circle-opacity': ['interpolate', ['linear'], ['zoom'], 8, 1, 11, 0.3] } });

      const hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12 });
      for (const layer of ['cities', 'feeds']) {
        map.on('mouseenter', layer, e => { map.getCanvas().style.cursor = 'pointer'; const p = e.features[0].properties; hover.setLngLat(e.features[0].geometry.coordinates).setText(layer === 'feeds' ? `${p.name} · ingested` : p.name).addTo(map); });
        map.on('mouseleave', layer, () => { map.getCanvas().style.cursor = ''; hover.remove(); });
      }
      map.on('click', 'cities', e => select(e.features[0].properties.rank, { fly: true }));
      map.on('click', 'feeds', e => { const f = e.features[0]; loadLines(f.properties.feed); fly(f.geometry.coordinates, 10.5); });
      map.on('moveend', loadVisibleLines);
      mapReady = true;
      paintMap();
    });
    $('map-reset').addEventListener('click', () => fly(WORLD.center, WORLD.zoom));
  }

  function fly(center, zoom) { if (map) map.flyTo({ center, zoom, duration: reduceMotion ? 0 : 1600, essential: true }); }

  async function loadLines(feed) {
    if (!map || linesLoaded.has(feed)) return;
    linesLoaded.set(feed, 'loading');
    try {
      const r = await fetch(`/map/${encodeURIComponent(feed)}/lines.geojson`);
      if (!r.ok) throw Error(`Routes for ${feed} unavailable (${r.status})`);
      const geo = await r.json();
      for (const f of geo.features) {
        f.properties.display_color = routeColor(f.properties);
        f.properties.order = MODE_ORDER[f.properties.mode] || 2;
      }
      const src = `lines-${feed}`;
      map.addSource(src, { type: 'geojson', data: geo });
      const width = ['interpolate', ['linear'], ['zoom'], LINES_MIN_ZOOM, ['*', 0.4, ['get', 'order']], 10, ['*', 0.6, ['get', 'order']], 15, ['*', 1.2, ['get', 'order']]];
      map.addLayer({ id: `${src}-glow`, type: 'line', source: src, minzoom: LINES_MIN_ZOOM, layout: { 'line-cap': 'round', 'line-join': 'round', 'line-sort-key': ['get', 'order'] }, paint: { 'line-color': ['get', 'display_color'], 'line-width': ['*', 3, width], 'line-opacity': 0.12, 'line-blur': 4 } }, 'cities');
      map.addLayer({ id: src, type: 'line', source: src, minzoom: LINES_MIN_ZOOM, layout: { 'line-cap': 'round', 'line-join': 'round', 'line-sort-key': ['get', 'order'] }, paint: { 'line-color': ['get', 'display_color'], 'line-width': width, 'line-opacity': ['interpolate', ['linear'], ['zoom'], LINES_MIN_ZOOM, 0.5, 9, 0.9] } }, 'cities');
      linesLoaded.set(feed, 'done');
    } catch (e) {
      linesLoaded.delete(feed);
      toast(e.message);
    }
  }

  function loadVisibleLines() {
    if (!map || map.getZoom() < LINES_MIN_ZOOM - 0.5) return;
    const b = map.getBounds();
    for (const f of ingestedFeeds) if (f.lat != null && b.contains([f.lon, f.lat])) loadLines(f.feed);
  }

  function paintMap() {
    if (!mapReady) return;
    for (const c of cities) map.setFeatureState({ source: 'cities', id: c.rank }, { selected: c.rank === sel, faded: !shown(c) });
  }

  // ── list & detail ────────────────────────────────────────────────────────
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
      b.addEventListener('click', () => select(c.rank, { fly: true, reveal: true }));
      grid.append(b);
      rows.set(c.rank, b);
    }
  }

  function renderDetail() {
    const c = byRank.get(sel); if (!c) return;
    const n = c.feeds.length, ing = c.ingested.length > 0;
    $('d-rank').textContent = `No. ${c.rank} by population`;
    const pill = $('d-pill');
    pill.textContent = ing ? 'Ingested' : n ? 'Ready to ingest' : 'No open feed';
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
    for (const [rank, b] of rows) {
      b.hidden = !shown(byRank.get(rank));
      b.setAttribute('aria-pressed', String(rank === sel));
    }
    for (const b of document.querySelectorAll('[data-filter]')) b.setAttribute('aria-pressed', String(b.dataset.filter === filter));
    const s = data.summary;
    $('list-title').textContent = filter === 'all' ? `All ${s.cities}, by population.` : filter === 'yes' ? `${s.covered} cities ready to go.` : `${s.uncovered} cities waiting for open data.`;
    renderDetail();
    paintMap();
  }

  function select(rank, opts = {}) {
    sel = rank; render();
    const c = byRank.get(rank);
    const url = new URL(location.href); url.searchParams.set('city', String(rank)); history.replaceState(null, '', url);
    if (opts.fly && c) {
      const ing = c.ingested.length > 0;
      if (ing) c.ingested.forEach(loadLines);
      fly([c.lon, c.lat], ing ? 10 : 7.5);
    }
    if (opts.reveal) {
      const target = $('map').getBoundingClientRect();
      if (target.top < 0 || target.bottom > innerHeight) $('map').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
    }
  }

  async function load() {
    try {
      const [r, rc] = await Promise.all([fetch('/world/cities'), fetch('/cities')]);
      if (!r.ok) throw Error(`World data unavailable (${r.status})`);
      data = await r.json();
      ingestedFeeds = rc.ok ? (await rc.json()).filter(f => f.lat != null && f.lon != null) : [];
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
      buildGrid(); buildMap();
      for (const b of document.querySelectorAll('[data-filter]')) b.addEventListener('click', () => { filter = b.dataset.filter; render(); });
      render();
    } catch (e) {
      $('d-rank').textContent = 'Unavailable';
      toast(e.message);
    }
  }

  load();
})();
