(() => {
  'use strict';
  const DARK_STYLE = 'https://tiles.openfreemap.org/styles/dark';
  const $ = id => document.getElementById(id);
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const map = new maplibregl.Map({container:'map',style:DARK_STYLE,center:[14.5,49],zoom:5.5,attributionControl:true,pitchWithRotate:false});
  map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
  let cities = [], activeCity = null, mapReady = false;
  const modeOrder = ['bus','trolleybus','tram','cable_tram','metro','rail','monorail','ferry','aerial','funicular'];
  const modeStyle = {bus:[1.15,.50],trolleybus:[1.3,.58],tram:[2.15,.80],cable_tram:[2,.77],metro:[3.5,1],rail:[3.4,.95],monorail:[2.7,.9],ferry:[1.7,.7],aerial:[1.7,.75],funicular:[1.9,.78]};
  function toast(message){const el=$('toast');el.textContent=message;el.hidden=false;window.setTimeout(()=>el.hidden=true,5500)}
  function report(message,error=false){$('network-status').textContent=message;document.querySelector('.live-pill').classList.toggle('error',error)}
  function validColor(raw){return typeof raw==='string'&&/^#[0-9a-fA-F]{6}$/.test(raw)}
  function liftColor(raw){
    if(!validColor(raw))return '#9fd6df';
    const rgb=[1,3,5].map(i=>parseInt(raw.slice(i,i+2),16)/255);
    const hi=Math.max(...rgb),lo=Math.min(...rgb),delta=hi-lo;
    let h=0,s=0,l=(hi+lo)/2;
    if(delta){s=delta/(1-Math.abs(2*l-1));switch(hi){case rgb[0]:h=((rgb[1]-rgb[2])/delta)%6;break;case rgb[1]:h=(rgb[2]-rgb[0])/delta+2;break;default:h=(rgb[0]-rgb[1])/delta+4}h=(h*60+360)%360}
    if(l>=.56)return raw;
    l=.56;s=Math.max(s,.58);
    const c=(1-Math.abs(2*l-1))*s,x=c*(1-Math.abs((h/60)%2-1)),m=l-c/2;
    const sectors=[[c,x,0],[x,c,0],[0,c,x],[0,x,c],[x,0,c],[c,0,x]];
    return '#'+sectors[Math.floor(h/60)].map(v=>Math.round((v+m)*255).toString(16).padStart(2,'0')).join('');
  }
  function prepareFeatures(fc){return {type:'FeatureCollection',features:(fc.features||[]).filter(f=>f.geometry&&f.geometry.type==='LineString').map(f=>({type:'Feature',geometry:f.geometry,properties:{...f.properties,display_color:liftColor(f.properties?.color)}}))}}
  function labelLayer(){return map.getStyle().layers.find(l=>l.type==='symbol')?.id}
  function clearNetwork(){if(map.getSource('network')){for(const m of modeOrder){for(const s of ['glow','line']){const id=`network-${m}-${s}`;if(map.getLayer(id))map.removeLayer(id)}}map.removeSource('network')}}
  function addNetwork(fc){
    clearNetwork();map.addSource('network',{type:'geojson',data:fc});
    const before=labelLayer();
    for(const mode of modeOrder){
      const [width,opacity]=modeStyle[mode],filter=['==',['get','mode'],mode];
      map.addLayer({id:`network-${mode}-glow`,type:'line',source:'network',filter,paint:{'line-color':['get','display_color'],'line-width':['interpolate',['linear'],['zoom'],8,width*2,12,width*4,16,width*6],'line-opacity':opacity*.14,'line-blur':7}},before);
      map.addLayer({id:`network-${mode}-line`,type:'line',source:'network',filter,layout:{'line-cap':'round','line-join':'round'},paint:{'line-color':['get','display_color'],'line-width':['interpolate',['linear'],['zoom'],8,width*.55,12,width,16,width*1.9],'line-opacity':opacity}},before);
    }
  }
  function boundsFor(fc){const b=new maplibregl.LngLatBounds();for(const f of fc.features){for(const c of f.geometry.coordinates){if(Number.isFinite(c[0])&&Number.isFinite(c[1]))b.extend(c)}}return b}
  async function chooseCity(id){
    activeCity=id;report('Loading network');
    try{const res=await fetch(`/map/${encodeURIComponent(id)}/lines.geojson`);if(!res.ok)throw Error(`Lines unavailable (${res.status})`);const fc=prepareFeatures(await res.json());if(activeCity!==id)return;
      addNetwork(fc);const routes=new Set(fc.features.map(f=>f.properties.route_id));const modes=new Set(fc.features.map(f=>f.properties.mode));
      $('line-count').textContent=`${routes.size.toLocaleString()} routes on the map`;$('mode-list').textContent=[...modes].sort().join(' · ').toUpperCase();report(`${cities.find(c=>c.feed===id)?.city||id} · network loaded`);
      if(fc.features.length){map.fitBounds(boundsFor(fc),{padding:{top:125,bottom:55,left:window.innerWidth>680?415:30,right:35},maxZoom:12,duration:reduceMotion?0:950})}else toast('No line geometry for this city');
    }catch(e){report('Network unavailable',true);toast(e.message)}
  }
  async function loadCities(){try{const r=await fetch('/cities');if(!r.ok)throw Error(`Cities unavailable (${r.status})`);cities=await r.json();const select=$('city');select.replaceChildren();if(!cities.length){select.add(new Option('No ingested cities',''));select.disabled=true;report('No local city data',true);toast('No ingested cities found. Load a city to explore the map.');return}for(const c of cities)select.add(new Option(`${c.city} · ${c.country||c.feed}`,c.feed));select.value=cities.find(c=>c.feed==='mdb-648')?.feed||cities[0].feed;select.addEventListener('change',()=>chooseCity(select.value));await chooseCity(select.value)}catch(e){report('Cities unavailable',true);toast(e.message)}}
  map.on('load',()=>{mapReady=true;const layers=map.getStyle().layers;for(const l of layers){if(l.type==='symbol'&&l.paint?.['text-color']){try{map.setPaintProperty(l.id,'text-opacity',.55)}catch(_){}}}loadCities()});
  map.on('error',e=>{if(!mapReady&&e.error)report('Map tiles unavailable',true)});
})();
