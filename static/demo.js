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
  function clearStops(){for(const id of ['stop-labels','stop-points','stop-cluster-count','stop-clusters'])if(map.getLayer(id))map.removeLayer(id);if(map.getSource('stops'))map.removeSource('stops')}
  function addStops(stops){
    clearStops();const features=stops.filter(s=>Number.isFinite(s.lat)&&Number.isFinite(s.lon)).map(s=>({type:'Feature',properties:{id:s.id,name:s.name},geometry:{type:'Point',coordinates:[s.lon,s.lat]}}));
    map.addSource('stops',{type:'geojson',data:{type:'FeatureCollection',features},cluster:true,clusterRadius:46,clusterMaxZoom:14});
    map.addLayer({id:'stop-clusters',type:'circle',source:'stops',minzoom:10,filter:['has','point_count'],paint:{'circle-color':'#243b50','circle-radius':['step',['get','point_count'],15,20,19,100,23],'circle-stroke-color':'#a3c9d0','circle-stroke-width':1.2,'circle-opacity':.87}});
    map.addLayer({id:'stop-cluster-count',type:'symbol',source:'stops',minzoom:10,filter:['has','point_count'],layout:{'text-field':['get','point_count_abbreviated'],'text-size':11},paint:{'text-color':'#f2f7f9'}});
    map.addLayer({id:'stop-points',type:'circle',source:'stops',minzoom:13,filter:['!',['has','point_count']],paint:{'circle-color':'#e9eff1','circle-radius':['interpolate',['linear'],['zoom'],13,2.5,16,5],'circle-stroke-color':'#273f51','circle-stroke-width':1.4}});
    map.addLayer({id:'stop-labels',type:'symbol',source:'stops',minzoom:15,filter:['!',['has','point_count']],layout:{'text-field':['get','name'],'text-size':11,'text-offset':[0,1.25],'text-anchor':'top','text-optional':true},paint:{'text-color':'#e5eff2','text-halo-color':'#081019','text-halo-width':1.5}});
  }
  async function showBoard(id,name){
    const board=$('board');board.hidden=false;$('board-name').textContent=name;$('board-list').replaceChildren();$('board-list').textContent='Loading departures…';$('board-note').textContent='Scheduled times · Live when available';
    try{const res=await fetch(`/stops/${encodeURIComponent(activeCity)}/${encodeURIComponent(id)}/departures?limit=7`);if(!res.ok)throw Error(`Departures unavailable (${res.status})`);const data=await res.json();if(board.hidden)return;$('board-name').textContent=data.stop_name||name;const list=$('board-list');list.replaceChildren();if(!data.departures?.length){list.textContent='No upcoming departures at this stop.';list.classList.add('board-empty');return}list.classList.remove('board-empty');for(const dep of data.departures){const row=document.createElement('div');row.className='departure';const route=document.createElement('span');route.className='departure-route';route.textContent=dep.route||'—';route.style.backgroundColor=validColor(dep.color)?liftColor(dep.color):'#465c70';const head=document.createElement('span');head.className='departure-headsign';head.textContent=dep.headsign||dep.mode||'Transit';const time=document.createElement('span');time.className='departure-time';time.textContent=dep.time||'—';const sub=document.createElement('small');sub.textContent=dep.in_minutes!=null?`${dep.in_minutes} min${dep.live?' · LIVE':''}`:dep.day_offset?'tomorrow':(dep.live?'LIVE':'scheduled');time.append(sub);row.append(route,head,time);list.append(row)}}catch(e){$('board-list').textContent=e.message}}
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
      addNetwork(fc);$('board').hidden=true;const routes=new Set(fc.features.map(f=>f.properties.route_id));const modes=new Set(fc.features.map(f=>f.properties.mode));
      $('line-count').textContent=`${routes.size.toLocaleString()} routes on the map`;$('mode-list').textContent=[...modes].sort().join(' · ').toUpperCase();report(`${cities.find(c=>c.feed===id)?.city||id} · network loaded`);
      if(fc.features.length){map.fitBounds(boundsFor(fc),{padding:{top:125,bottom:55,left:window.innerWidth>680?415:30,right:35},maxZoom:12,duration:reduceMotion?0:950})}else toast('No line geometry for this city');
      const stopRes=await fetch(`/stops?city=${encodeURIComponent(id)}`);if(!stopRes.ok)throw Error(`Stops unavailable (${stopRes.status})`);const stops=await stopRes.json();if(activeCity===id){addStops(stops);const query=new URLSearchParams(location.search);if(query.get('city')===id&&query.get('stop')){const stop=stops.find(s=>s.id===query.get('stop'));if(stop){map.easeTo({center:[stop.lon,stop.lat],zoom:15.4,duration:reduceMotion?0:750});showBoard(stop.id,stop.name)}}}
    }catch(e){report('Network unavailable',true);toast(e.message)}
  }
  async function loadCities(){try{const r=await fetch('/cities');if(!r.ok)throw Error(`Cities unavailable (${r.status})`);cities=await r.json();const select=$('city');select.replaceChildren();if(!cities.length){select.add(new Option('No ingested cities',''));select.disabled=true;report('No local city data',true);toast('No ingested cities found. Load a city to explore the map.');return}for(const c of cities)select.add(new Option(`${c.city} · ${c.country||c.feed}`,c.feed));const requested=new URLSearchParams(location.search).get('city');select.value=cities.find(c=>c.feed===requested)?.feed||cities.find(c=>c.feed==='mdb-648')?.feed||cities[0].feed;select.addEventListener('change',()=>{const url=new URL(location.href);url.searchParams.set('city',select.value);url.searchParams.delete('stop');history.replaceState(null,'',url);chooseCity(select.value)});await chooseCity(select.value)}catch(e){report('Cities unavailable',true);toast(e.message)}}
  $('board-close').addEventListener('click',()=>{$('board').hidden=true});
  map.on('click','stop-clusters',e=>{const f=e.features?.[0];if(!f)return;map.getSource('stops').getClusterExpansionZoom(f.properties.cluster_id).then(z=>map.easeTo({center:f.geometry.coordinates,zoom:z,duration:reduceMotion?0:500}))});
  map.on('click','stop-points',e=>{const f=e.features?.[0];if(f)showBoard(f.properties.id,f.properties.name)});
  for(const id of ['stop-clusters','stop-points']){map.on('mouseenter',id,()=>map.getCanvas().style.cursor='pointer');map.on('mouseleave',id,()=>map.getCanvas().style.cursor='')}
  map.on('load',()=>{mapReady=true;const layers=map.getStyle().layers;for(const l of layers){if(l.type==='symbol'&&l.paint?.['text-color']){try{map.setPaintProperty(l.id,'text-opacity',.55)}catch(_){}}}loadCities()});
  map.on('error',e=>{if(!mapReady&&e.error)report('Map tiles unavailable',true)});
})();
