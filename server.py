import os, time, statistics, requests
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

APIFY_BASE  = "https://api.apify.com/v2"
APIFY_ACTOR = "antonionduarte~glovo-scraper"

CITY_NAMES = {
    "verona":  "Verona",
    "milano":  "Milan",
    "roma":    "Rome",
    "torino":  "Turin",
    "napoli":  "Naples",
    "bologna": "Bologna",
    "firenze": "Florence",
}

HTML = '<!DOCTYPE html>\n<html lang="it">\n<head>\n<meta charset="UTF-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n<title>Glovo Price Monitor</title>\n<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700&display=swap" rel="stylesheet" />\n<style>\n:root {\n  --bg:#0f0f0f; --surface:#161616; --surface2:#1e1e1e;\n  --border:rgba(255,255,255,0.07); --border2:rgba(255,255,255,0.13);\n  --text:#f0ede8; --text2:#888880; --text3:#505050;\n  --accent:#ff4d00; --accent2:#ff6a28;\n  --green:#2ecc71; --amber:#f39c12; --red:#e74c3c;\n  --red-bg:rgba(231,76,60,0.10); --green-bg:rgba(46,204,113,0.10); --amber-bg:rgba(243,156,18,0.10);\n  --font-d:\'Syne\',sans-serif; --font-m:\'DM Mono\',monospace;\n  --r:8px; --rl:14px;\n}\n*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}\nbody{background:var(--bg);color:var(--text);font-family:var(--font-m);font-size:13px;line-height:1.6;min-height:100vh;}\nheader{border-bottom:1px solid var(--border);padding:0 2rem;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;background:rgba(15,15,15,0.93);backdrop-filter:blur(12px);z-index:100;}\n.logo{font-family:var(--font-d);font-weight:700;font-size:17px;letter-spacing:-0.02em;display:flex;align-items:center;gap:10px;}\n.logo-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:pulse 2s infinite;}\n@keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.5;transform:scale(.7);}}\n.htag{font-size:11px;color:var(--text3);border:1px solid var(--border);padding:3px 10px;border-radius:20px;}\nmain{max-width:1200px;margin:0 auto;padding:2.5rem 2rem 4rem;}\n.hero{margin-bottom:2rem;animation:fadeUp .5s ease both;}\n@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}\n.hero h1{font-family:var(--font-d);font-size:clamp(26px,5vw,44px);font-weight:700;letter-spacing:-.03em;line-height:1.1;margin-bottom:10px;}\n.hero h1 span{color:var(--accent);}\n.hero p{color:var(--text2);font-size:12px;max-width:500px;}\n.controls{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);padding:1.25rem 1.5rem;margin-bottom:1.5rem;animation:fadeUp .5s .1s ease both;}\n.crow{display:flex;gap:10px;margin-bottom:1rem;flex-wrap:wrap;}\n.crow:last-child{margin-bottom:0;}\n.clabel{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px;}\n.cgroup{display:flex;flex-direction:column;flex:1;min-width:140px;}\n.cgroup.wide{flex:2;min-width:220px;}\ninput[type=text],input[type=password],select{background:var(--surface2);border:1px solid var(--border2);border-radius:var(--r);color:var(--text);font-family:var(--font-m);font-size:12px;padding:0 12px;height:38px;outline:none;transition:border-color .2s;width:100%;}\ninput:focus,select:focus{border-color:var(--accent);}\ninput::placeholder{color:var(--text3);}\n.btn{height:38px;padding:0 18px;border-radius:var(--r);border:none;font-family:var(--font-m);font-size:12px;font-weight:500;cursor:pointer;display:inline-flex;align-items:center;gap:7px;transition:all .15s;white-space:nowrap;}\n.btn-accent{background:var(--accent);color:#fff;}\n.btn-accent:hover{background:var(--accent2);}\n.btn-accent:disabled{opacity:.45;cursor:not-allowed;}\n.btn-ghost{background:transparent;color:var(--text2);border:1px solid var(--border2);}\n.btn-ghost:hover{color:var(--text);background:var(--surface2);}\n.trow{display:flex;align-items:center;gap:12px;color:var(--text2);font-size:12px;flex-wrap:wrap;}\ninput[type=range]{-webkit-appearance:none;width:130px;height:4px;background:var(--border2);border-radius:2px;outline:none;}\ninput[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;border-radius:50%;background:var(--accent);cursor:pointer;}\n.tval{color:var(--accent);font-weight:500;min-width:38px;}\n.note{font-size:11px;color:var(--text3);margin-top:8px;line-height:1.6;}\n.note a{color:var(--accent);text-decoration:none;}\n.note a:hover{text-decoration:underline;}\n.prog-wrap{height:2px;background:var(--border);border-radius:2px;margin:.75rem 0;overflow:hidden;display:none;}\n.prog-fill{height:100%;background:var(--accent);border-radius:2px;width:0%;transition:width .5s ease;}\n.scan-st{display:none;align-items:center;gap:8px;font-size:12px;color:var(--text2);margin:.5rem 0;}\n.scan-st.on{display:flex;}\n.spinner{width:13px;height:13px;border:1.5px solid var(--border2);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;}\n@keyframes spin{to{transform:rotate(360deg);}}\n.error-box{background:var(--red-bg);border:1px solid rgba(231,76,60,.3);border-radius:var(--rl);padding:.85rem 1.1rem;margin-bottom:1.25rem;font-size:12px;color:var(--red);display:none;}\n.ai-box{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:var(--rl);padding:1rem 1.25rem;margin-bottom:1.5rem;display:none;animation:fadeUp .4s ease both;}\n.ai-hd{font-size:10px;font-weight:500;color:var(--accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;display:flex;align-items:center;gap:6px;}\n.ai-hd::before{content:\'\';display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--accent);}\n#aiText{color:var(--text2);line-height:1.75;font-size:12px;}\n.metrics{display:none;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:1.5rem;animation:fadeUp .4s ease both;}\n.metric{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);padding:14px 16px;transition:border-color .2s;}\n.metric:hover{border-color:var(--border2);}\n.ml{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;}\n.mv{font-family:var(--font-d);font-size:26px;font-weight:700;color:var(--text);}\n.mv.alert{color:var(--accent);}\n.tabs{display:none;gap:6px;margin-bottom:1.25rem;}\n.tab{font-family:var(--font-m);font-size:12px;padding:6px 16px;border-radius:20px;border:1px solid var(--border);cursor:pointer;color:var(--text2);background:transparent;transition:all .15s;}\n.tab:hover{border-color:var(--border2);color:var(--text);}\n.tab.active{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:500;}\n.twrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--rl);overflow:hidden;animation:fadeUp .4s ease both;}\ntable{width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed;}\nth{background:var(--surface2);color:var(--text3);font-weight:500;text-align:left;padding:11px 16px;border-bottom:1px solid var(--border);font-size:10px;text-transform:uppercase;letter-spacing:.07em;white-space:nowrap;}\nth.s{cursor:pointer;user-select:none;}\nth.s:hover{color:var(--text2);}\nth.sa{color:var(--accent)!important;}\ntd{padding:11px 16px;border-bottom:1px solid var(--border);color:var(--text2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}\ntr:last-child td{border-bottom:none;}\ntr.anom td{background:rgba(255,77,0,0.04);}\ntr:hover td{background:rgba(255,255,255,0.02);}\ntr.anom:hover td{background:rgba(255,77,0,0.07);}\n.pl{color:var(--text);text-decoration:none;font-weight:500;display:inline-flex;align-items:center;gap:5px;transition:color .15s;}\n.pl:hover{color:var(--accent);}\n.sl{color:var(--text3);text-decoration:none;transition:color .15s;}\n.sl:hover{color:var(--accent);}\n.badge{display:inline-block;font-size:10px;font-weight:500;padding:3px 9px;border-radius:20px;letter-spacing:.03em;}\n.bd{background:var(--red-bg);color:var(--red);border:1px solid rgba(231,76,60,.25);}\n.bo{background:var(--green-bg);color:var(--green);border:1px solid rgba(46,204,113,.2);}\n.bw{background:var(--amber-bg);color:var(--amber);border:1px solid rgba(243,156,18,.25);}\n.buybtn{display:inline-flex;align-items:center;gap:5px;background:var(--accent);color:#fff;text-decoration:none;border-radius:6px;padding:4px 10px;font-size:11px;font-weight:500;font-family:var(--font-m);transition:background .15s,transform .1s;}\n.buybtn:hover{background:var(--accent2);transform:scale(1.03);}\n.pdrop{color:var(--accent);font-weight:500;}\n.empty{text-align:center;padding:4rem 1rem;color:var(--text3);}\n.empty-icon{font-size:36px;margin-bottom:12px;opacity:.4;}\nfooter{border-top:1px solid var(--border);padding:1.5rem 2rem;color:var(--text3);font-size:11px;display:flex;justify-content:space-between;align-items:center;max-width:1200px;margin:4rem auto 0;}\nfooter a{color:var(--text3);text-decoration:none;}\nfooter a:hover{color:var(--accent);}\n@media(max-width:768px){.metrics{grid-template-columns:repeat(2,1fr);}main{padding:1.5rem 1rem 3rem;}header{padding:0 1rem;}td,th{padding:9px 10px;}}\n</style>\n</head>\n<body>\n<header>\n  <div class="logo"><div class="logo-dot"></div>Glovo Price Monitor</div>\n  <span class="htag">dati reali · Apify</span>\n</header>\n\n<main>\n  <div class="hero">\n    <h1>Trova errori di<br><span>prezzo al ribasso</span></h1>\n    <p>Dati reali da Glovo via Apify Scraper. Rileva automaticamente prodotti con prezzi anomali rispetto alla mediana di categoria.</p>\n  </div>\n\n  <div class="controls">\n    <div class="crow">\n      <div class="cgroup wide">\n        <div class="clabel">Token Apify</div>\n        <input type="password" id="apifyToken" placeholder="apify_api_xxxxxxxxxxxx" />\n      </div>\n      <div class="cgroup wide">\n        <div class="clabel">API Key Anthropic (opzionale)</div>\n        <input type="password" id="anthropicKey" placeholder="sk-ant-..." />\n      </div>\n    </div>\n    <div class="note">\n      Token Apify: <a href="https://console.apify.com/account/integrations" target="_blank">console.apify.com → API tokens</a> ·\n      API Key Anthropic: <a href="https://console.anthropic.com/keys" target="_blank">console.anthropic.com/keys</a> ·\n      Le chiavi restano solo nel browser.\n    </div>\n\n    <div class="crow" style="margin-top:1rem;">\n      <div class="cgroup">\n        <div class="clabel">Città</div>\n        <select id="citySelect">\n          <option value="verona">Verona</option>\n          <option value="milano">Milano</option>\n          <option value="roma">Roma</option>\n          <option value="torino">Torino</option>\n          <option value="napoli">Napoli</option>\n          <option value="bologna">Bologna</option>\n          <option value="firenze">Firenze</option>\n        </select>\n      </div>\n      <div class="cgroup">\n        <div class="clabel">Max prodotti</div>\n        <select id="maxItems">\n          <option value="50">50 — veloce (~1 min)</option>\n          <option value="100">100 (~2 min)</option>\n          <option value="200" selected>200 (~4 min)</option>\n          <option value="500">500 — lento (~10 min)</option>\n        </select>\n      </div>\n      <div style="display:flex;align-items:flex-end;gap:8px;">\n        <button class="btn btn-accent" id="scanBtn" onclick="startScan()">\n          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="5" cy="5" r="4" stroke="currentColor" stroke-width="1.5"/><path d="M8.5 8.5L11 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>\n          Analizza\n        </button>\n        <button class="btn btn-ghost" onclick="resetAll()">Reset</button>\n      </div>\n    </div>\n\n    <div class="crow" style="margin-top:.75rem;">\n      <div class="trow">\n        <span>Soglia anomalia:</span>\n        <input type="range" id="threshold" min="10" max="70" value="30" step="5" oninput="onThr(this.value)" />\n        <span class="tval" id="thrLabel">−30%</span>\n        <span>rispetto alla mediana di categoria</span>\n      </div>\n    </div>\n  </div>\n\n  <div class="prog-wrap" id="progWrap"><div class="prog-fill" id="progFill"></div></div>\n  <div class="scan-st" id="scanSt"><div class="spinner"></div><span id="scanStTxt">Avvio...</span></div>\n  <div class="error-box" id="errorBox"></div>\n\n  <div class="ai-box" id="aiBox">\n    <div class="ai-hd">Analisi AI — Claude</div>\n    <div id="aiText"></div>\n  </div>\n\n  <div class="metrics" id="metricsRow">\n    <div class="metric"><div class="ml">Prodotti scansionati</div><div class="mv" id="mTotal">0</div></div>\n    <div class="metric"><div class="ml">Anomalie rilevate</div><div class="mv alert" id="mAnom">0</div></div>\n    <div class="metric"><div class="ml">Sconto medio anomalie</div><div class="mv" id="mDrop">—</div></div>\n    <div class="metric"><div class="ml">Risparmio potenziale</div><div class="mv" id="mSave">—</div></div>\n  </div>\n\n  <div class="tabs" id="tabsRow">\n    <button class="tab active" onclick="switchTab(\'all\',this)">Tutti i prodotti</button>\n    <button class="tab" onclick="switchTab(\'anomalies\',this)">Solo anomalie</button>\n  </div>\n\n  <div id="tableContainer">\n    <div class="twrap">\n      <div class="empty"><div class="empty-icon">◎</div><p>Inserisci il token Apify, seleziona la città e premi Analizza.</p></div>\n    </div>\n  </div>\n</main>\n\n<footer>\n  <span>Glovo Price Monitor · Powered by Apify + Claude AI</span>\n  <a href="https://glovoapp.com" target="_blank">glovoapp.com ↗</a>\n</footer>\n\n<script>\nconst BACKEND = \'\';  // Su Render frontend e backend sono sullo stesso dominio\nconst ARR = `<svg style="width:10px;height:10px;flex-shrink:0" viewBox="0 0 12 12" fill="none"><path d="M2 10L10 2M10 2H4M10 2V8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`;\n\nlet allProducts = [];\nlet currentTab = \'all\';\nlet sortCol = \'drop\';\nlet sortAsc = false;\n\nfunction onThr(v){ document.getElementById(\'thrLabel\').textContent=\'−\'+v+\'%\'; if(allProducts.length) renderTable(); }\nfunction getThr(){ return parseInt(document.getElementById(\'threshold\').value)/100; }\nfunction switchTab(t,el){ currentTab=t; document.querySelectorAll(\'.tab\').forEach(x=>x.classList.remove(\'active\')); el.classList.add(\'active\'); renderTable(); }\nfunction showErr(msg){ const b=document.getElementById(\'errorBox\'); b.textContent=\'⚠ \'+msg; b.style.display=\'block\'; }\nfunction hideErr(){ document.getElementById(\'errorBox\').style.display=\'none\'; }\n\nfunction resetAll(){\n  allProducts=[];\n  [\'metricsRow\',\'tabsRow\',\'aiBox\',\'progWrap\',\'errorBox\'].forEach(id=>document.getElementById(id).style.display=\'none\');\n  document.getElementById(\'scanSt\').classList.remove(\'on\');\n  document.getElementById(\'tableContainer\').innerHTML=`<div class="twrap"><div class="empty"><div class="empty-icon">◎</div><p>Inserisci il token Apify, seleziona la città e premi Analizza.</p></div></div>`;\n}\n\nasync function startScan(){\n  const apifyToken=document.getElementById(\'apifyToken\').value.trim();\n  if(!apifyToken){ showErr(\'Inserisci il token Apify per continuare.\'); return; }\n  hideErr();\n\n  const city=document.getElementById(\'citySelect\').value;\n  const threshold=getThr();\n  const maxItems=parseInt(document.getElementById(\'maxItems\').value);\n  const btn=document.getElementById(\'scanBtn\');\n\n  btn.disabled=true;\n  btn.innerHTML=\'<div class="spinner" style="width:12px;height:12px"></div> Scansione...\';\n  document.getElementById(\'progWrap\').style.display=\'block\';\n  document.getElementById(\'progFill\').style.width=\'0%\';\n  const ss=document.getElementById(\'scanSt\'); ss.classList.add(\'on\');\n\n  // Simula step progress mentre il backend lavora\n  const steps=[[15,\'Connessione ad Apify...\'],[35,\'Avvio Glovo Scraper...\'],[55,\'Raccolta prodotti...\'],[75,\'Calcolo mediane per categoria...\'],[88,\'Rilevamento anomalie...\']];\n  let si=0;\n  const iv=setInterval(()=>{ if(si<steps.length){ document.getElementById(\'progFill\').style.width=steps[si][0]+\'%\'; document.getElementById(\'scanStTxt\').textContent=steps[si][1]; si++; } },4000);\n\n  try{\n    const res=await fetch(`${BACKEND}/scan`,{\n      method:\'POST\',\n      headers:{\'Content-Type\':\'application/json\'},\n      body:JSON.stringify({apifyToken,city,threshold,maxItems})\n    });\n    clearInterval(iv);\n\n    if(!res.ok){\n      const err=await res.json().catch(()=>({error:\'Errore sconosciuto\'}));\n      throw new Error(err.error||`HTTP ${res.status}`);\n    }\n\n    const data=await res.json();\n    document.getElementById(\'progFill\').style.width=\'100%\';\n    await new Promise(r=>setTimeout(r,300));\n    document.getElementById(\'progWrap\').style.display=\'none\';\n    ss.classList.remove(\'on\');\n\n    allProducts=data.products;\n    document.getElementById(\'mTotal\').textContent=data.total;\n    document.getElementById(\'mAnom\').textContent=data.anomalies;\n    document.getElementById(\'mDrop\').textContent=data.anomalies>0?\'−\'+Math.round(data.avgDrop*100)+\'%\':\'—\';\n    document.getElementById(\'mSave\').textContent=data.anomalies>0?\'€\'+data.totalSaving.toFixed(2):\'—\';\n    document.getElementById(\'metricsRow\').style.display=\'grid\';\n    document.getElementById(\'tabsRow\').style.display=\'flex\';\n\n    renderTable();\n    const anoms=allProducts.filter(p=>p.isAnomaly);\n    if(anoms.length>0) analyzeWithAI(anoms,city);\n\n  }catch(e){\n    clearInterval(iv);\n    document.getElementById(\'progWrap\').style.display=\'none\';\n    ss.classList.remove(\'on\');\n    showErr(e.message);\n  }\n\n  btn.disabled=false;\n  btn.innerHTML=\'<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="5" cy="5" r="4" stroke="currentColor" stroke-width="1.5"/><path d="M8.5 8.5L11 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg> Analizza\';\n}\n\nasync function analyzeWithAI(anomalies,city){\n  const apiKey=document.getElementById(\'anthropicKey\').value.trim();\n  document.getElementById(\'aiBox\').style.display=\'block\';\n  document.getElementById(\'aiText\').innerHTML=\'<span style="color:var(--text3)">Analisi in corso...</span>\';\n\n  if(!apiKey){ document.getElementById(\'aiText\').textContent=\'Inserisci la tua API key Anthropic per abilitare l\\\'analisi AI.\'; return; }\n\n  const list=anomalies.slice(0,10).map(p=>`- ${p.name} (${p.store}): €${p.price} vs mediana €${p.avgPrice} → −${Math.round(p.drop*100)}%`).join(\'\\n\');\n\n  try{\n    const res=await fetch(\'https://api.anthropic.com/v1/messages\',{\n      method:\'POST\',\n      headers:{\'Content-Type\':\'application/json\',\'x-api-key\':apiKey,\'anthropic-version\':\'2023-06-01\',\'anthropic-dangerous-direct-browser-access\':\'true\'},\n      body:JSON.stringify({model:\'claude-sonnet-4-20250514\',max_tokens:800,messages:[{role:\'user\',content:`Sei un analista prezzi food delivery. Analizza queste anomalie reali da Glovo a ${city}:\\n\\n${list}\\n\\nValuta errori vs promozioni e quali acquistare subito. Italiano, max 120 parole.`}]})\n    });\n    const d=await res.json();\n    document.getElementById(\'aiText\').textContent=d.content?.find(b=>b.type===\'text\')?.text||\'Risposta non disponibile.\';\n  }catch(e){\n    document.getElementById(\'aiText\').textContent=\'Errore analisi AI: \'+e.message;\n  }\n}\n\nfunction renderTable(){\n  let products=currentTab===\'anomalies\'?allProducts.filter(p=>p.isAnomaly):[...allProducts];\n  products.sort((a,b)=>{\n    const av=a[sortCol]!==undefined?a[sortCol]:a.name, bv=b[sortCol]!==undefined?b[sortCol]:b.name;\n    if(typeof av===\'string\') return sortAsc?av.localeCompare(bv):bv.localeCompare(av);\n    return sortAsc?av-bv:bv-av;\n  });\n\n  if(!products.length){\n    document.getElementById(\'tableContainer\').innerHTML=`<div class="twrap"><div class="empty"><div class="empty-icon">◎</div><p>Nessun prodotto. Abbassa la soglia o cambia tab.</p></div></div>`;\n    return;\n  }\n\n  const th=(col,lbl,w)=>{\n    const ac=sortCol===col?\' sa\':\'\', ar=sortCol===col?(sortAsc?\' ↑\':\' ↓\'):\'\';\n    return `<th class="s${ac}" style="width:${w}" onclick="sortBy(\'${col}\')">${lbl}${ar}</th>`;\n  };\n\n  const rows=products.map(p=>{\n    const pct=Math.round((p.drop||0)*100);\n    const badge=p.isAnomaly?`<span class="badge bd">Anomalia −${pct}%</span>`:pct>=15?`<span class="badge bw">−${pct}%</span>`:`<span class="badge bo">Normale</span>`;\n    const pUrl=p.productUrl||p.storeUrl||\'#\';\n    const sUrl=p.storeUrl||\'#\';\n    const act=p.isAnomaly?`<a href="${pUrl}" class="buybtn" target="_blank" rel="noopener">Acquista ${ARR}</a>`:`<span style="color:var(--text3)">—</span>`;\n    return `<tr class="${p.isAnomaly?\'anom\':\'\'}">\n      <td style="width:22%"><a href="${pUrl}" class="pl" target="_blank" rel="noopener">${p.name} ${ARR}</a></td>\n      <td style="width:16%"><a href="${sUrl}" class="sl" target="_blank" rel="noopener">${p.store}</a></td>\n      <td style="width:10%">${p.category}</td>\n      <td style="width:9%">€${(p.price||0).toFixed(2)}</td>\n      <td style="width:9%">${p.avgPrice?\'€\'+p.avgPrice.toFixed(2):\'—\'}</td>\n      <td style="width:9%" class="${p.isAnomaly?\'pdrop\':\'\'}">${p.isAnomaly&&p.saving>0?\'−€\'+p.saving.toFixed(2):\'—\'}</td>\n      <td style="width:13%">${badge}</td>\n      <td style="width:12%">${act}</td>\n    </tr>`;\n  }).join(\'\');\n\n  document.getElementById(\'tableContainer\').innerHTML=`\n    <div class="twrap"><table>\n      <thead><tr>\n        ${th(\'name\',\'Prodotto\',\'22%\')}<th style="width:16%">Store</th><th style="width:10%">Categoria</th>\n        ${th(\'price\',\'Prezzo\',\'9%\')}${th(\'avgPrice\',\'Mediana\',\'9%\')}${th(\'saving\',\'Risparmio\',\'9%\')}\n        ${th(\'drop\',\'Stato\',\'13%\')}<th style="width:12%">Azione</th>\n      </tr></thead><tbody>${rows}</tbody>\n    </table></div>`;\n}\n\nfunction sortBy(col){ if(sortCol===col) sortAsc=!sortAsc; else{sortCol=col;sortAsc=false;} renderTable(); }\n</script>\n</body>\n</html>\n'

@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

def run_apify_actor(api_token, city, max_items=200):
    city_name = CITY_NAMES.get(city, "Verona")
    headers   = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    payload   = {
        "location": city_name,
        "maxItems": max_items,
    }
    r = requests.post(f"{APIFY_BASE}/acts/{APIFY_ACTOR}/runs", json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    run_id = r.json()["data"]["id"]
    status_url = f"{APIFY_BASE}/actor-runs/{run_id}"
    for _ in range(60):
        time.sleep(5)
        s = requests.get(status_url, headers=headers, timeout=15).json()
        status = s["data"]["status"]
        if status == "SUCCEEDED": break
        if status in ("FAILED","ABORTED","TIMED-OUT"):
            raise RuntimeError(f"Apify run {status}")
    dataset_id = s["data"]["defaultDatasetId"]
    return requests.get(f"{APIFY_BASE}/datasets/{dataset_id}/items?format=json&limit={max_items}", headers=headers, timeout=30).json()

def normalize_items(raw):
    products = []
    for item in raw:
        # actor returns nested structure - handle both flat and nested
        price_raw = (
            item.get("price") or item.get("priceAmount") or
            item.get("productPrice") or item.get("unitPrice") or
            (item.get("product") or {}).get("price") or 0
        )
        try:
            price = float(str(price_raw).replace(",",".").replace("€","").strip())
        except Exception:
            continue
        if price <= 0: continue

        store = (
            item.get("storeName") or item.get("restaurant") or
            item.get("store") or item.get("restaurantName") or
            (item.get("store") or {}).get("name") or "Store"
        )
        category = (
            item.get("category") or item.get("categoryName") or
            item.get("section") or "Altro"
        )
        name = (
            item.get("name") or item.get("productName") or
            item.get("title") or (item.get("product") or {}).get("name") or "Prodotto"
        )
        store_url  = item.get("storeUrl") or item.get("url") or ""
        product_url = item.get("productUrl") or store_url

        products.append({
            "name": name, "store": store, "category": category,
            "price": price, "storeUrl": store_url, "productUrl": product_url,
        })
    return products

def compute_anomalies(products, threshold):
    by_cat = {}
    for p in products:
        by_cat.setdefault(p["category"], []).append(p["price"])
    avg_by_cat = {cat: statistics.median(v) for cat, v in by_cat.items() if len(v) >= 2}
    result = []
    for p in products:
        avg = avg_by_cat.get(p["category"])
        if avg and avg > 0:
            drop = (avg - p["price"]) / avg
            p.update({"avgPrice": round(avg,2), "drop": round(drop,4),
                      "saving": round(avg-p["price"],2), "isAnomaly": drop >= threshold})
        else:
            p.update({"avgPrice": None, "drop": 0.0, "saving": 0.0, "isAnomaly": False})
        result.append(p)
    result.sort(key=lambda x: (-int(x["isAnomaly"]), -x["drop"]))
    return result

@app.route("/scan", methods=["POST"])
def scan():
    body      = request.get_json(force=True)
    api_token = (os.environ.get("APIFY_TOKEN") or body.get("apifyToken") or "").strip()
    city      = (body.get("city") or "verona").strip().lower()
    threshold = float(body.get("threshold") or 0.30)
    max_items = min(int(body.get("maxItems") or 200), 500)
    if not api_token:
        return jsonify({"error": "Token Apify mancante."}), 400
    if city not in CITY_NAMES:
        return jsonify({"error": f"Citta non supportata: {city}"}), 400
    try:
        raw = run_apify_actor(api_token, city, max_items)
    except requests.HTTPError as e:
        return jsonify({"error": f"Apify HTTP {e.response.status_code}: {e.response.text[:300]}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502
    products = normalize_items(raw)
    if not products:
        return jsonify({"error": "Nessun prodotto trovato. Verifica il token e riprova."}), 404
    products     = compute_anomalies(products, threshold)
    anomalies    = [p for p in products if p["isAnomaly"]]
    avg_drop     = sum(p["drop"] for p in anomalies) / len(anomalies) if anomalies else 0
    total_saving = sum(p["saving"] for p in anomalies if p["saving"] > 0)
    return jsonify({
        "city": city, "total": len(products), "anomalies": len(anomalies),
        "avgDrop": round(avg_drop,4), "totalSaving": round(total_saving,2),
        "products": products,
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Glovo Price Monitor -> http://localhost:{port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
