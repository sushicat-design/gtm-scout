#!/usr/bin/env python3
import http.server, json, urllib.request, urllib.error, time, sys, os, socket

def find_port():
    for p in range(8765, 8800):
        try:
            s = socket.socket(); s.bind(('', p)); s.close(); return p
        except: continue
    return 8765

PORT = int(os.environ.get('PORT', find_port()))
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gtm_data.json')

def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f: return json.load(f)
    except: pass
    return []

def save_db(data):
    try:
        with open(DB_FILE, 'w') as f: json.dump(data, f)
    except: pass

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07090f;--bg2:#0e1119;--bg3:#141824;
  --sur:#0e1119;--sur2:#141824;
  --bor:#1d2333;--bor2:#252d3f;
  --tx:#dde4f0;--tx2:#8492aa;--tx3:#4a5570;
  --grn:#00e676;--grn-bg:rgba(0,230,118,0.08);--grn-bor:rgba(0,230,118,0.2);
  --amb:#ffb300;--amb-bg:rgba(255,179,0,0.08);
  --red:#ff5252;--red-bg:rgba(255,82,82,0.08);
  --blu:#448aff;--blu-bg:rgba(68,138,255,0.08);--blu-bor:rgba(68,138,255,0.2);
  --acc:#FF5C35;--acc-bg:rgba(255,92,53,0.08);--acc-bor:rgba(255,92,53,0.2);
}
body{background:var(--bg);color:var(--tx);font-family:'Manrope',sans-serif;font-size:14px;min-height:100vh;line-height:1.5}

.topbar{display:flex;align-items:center;justify-content:space-between;padding:14px 28px;background:var(--bg);border-bottom:1px solid var(--bor);position:sticky;top:0;z-index:100}
.logo-wrap{display:flex;align-items:center;gap:10px}
.logo-icon{width:30px;height:30px;background:var(--acc);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px}
.logo-text{font-size:16px;font-weight:800;color:var(--tx);letter-spacing:-0.03em}
.topbar-right{display:flex;align-items:center;gap:12px}
.stat-pill{display:flex;align-items:center;gap:6px;background:var(--bg2);border:1px solid var(--bor);border-radius:20px;padding:5px 12px}
.stat-n{font-size:14px;font-weight:800;color:var(--tx)}
.stat-l{font-size:11px;font-weight:500;color:var(--tx3)}
.stat-pill.hot .stat-n{color:var(--grn)}

.main{max-width:1000px;margin:0 auto;padding:28px 20px}

.fetch-card{background:var(--acc-bg);border:1.5px solid var(--acc-bor);border-radius:14px;padding:18px;margin-bottom:16px}
.fetch-title{font-size:15px;font-weight:800;color:var(--tx);letter-spacing:-0.02em;margin-bottom:2px}
.fetch-sub{font-size:12px;color:var(--tx2);font-weight:500;margin-bottom:12px}
.fetch-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.source-pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.src-pill{padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;border:1.5px solid var(--bor);background:var(--bg2);color:var(--tx2);cursor:pointer;transition:all 0.15s;font-family:'Manrope',sans-serif}
.src-pill.active{background:var(--acc);border-color:var(--acc);color:#fff}
#fetch-btn{background:var(--acc);color:#fff;border:none;border-radius:10px;font-family:'Manrope',sans-serif;font-weight:700;font-size:13px;padding:9px 18px;cursor:pointer;white-space:nowrap;transition:opacity 0.15s;flex-shrink:0}
#fetch-btn:hover{opacity:0.85}
#fetch-btn:disabled{opacity:.4;cursor:not-allowed}
#fetch-loading{display:none;align-items:center;gap:8px;margin-top:10px;font-size:13px;color:var(--tx2);font-weight:500}
#fetch-err{display:none;margin-top:10px;padding:10px 12px;background:var(--red-bg);border:1px solid rgba(255,82,82,0.2);border-radius:8px;color:var(--red);font-size:12px;font-weight:500}
#fetch-results{display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--acc-bor)}
.fetch-list{display:flex;flex-direction:column;gap:5px;margin-bottom:12px;max-height:260px;overflow-y:auto}
.fetch-item{display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--bg2);border:1.5px solid var(--bor);border-radius:10px;cursor:pointer;transition:all 0.15s}
.fetch-item:hover{border-color:var(--acc)}
.fetch-item.sel{border-color:var(--acc);background:var(--acc-bg)}
.fetch-item input{accent-color:var(--acc);width:15px;height:15px;cursor:pointer;flex-shrink:0}
.fetch-item-name{font-size:13px;font-weight:700;color:var(--tx)}
.fetch-item-meta{font-size:11px;color:var(--tx3);font-weight:500;margin-top:1px}
#res-sel-btn{background:var(--acc);color:#fff;border:none;border-radius:8px;font-family:'Manrope',sans-serif;font-weight:700;font-size:13px;padding:9px 18px;cursor:pointer}
#fetch-count{font-size:12px;color:var(--tx3);font-weight:500;margin-left:8px}

.search-card{background:var(--sur);border:1px solid var(--bor);border-radius:14px;padding:18px;margin-bottom:16px}
.search-row{display:flex;gap:8px;margin-bottom:12px}
#ci{flex:1;background:var(--bg);border:1.5px solid var(--bor2);border-radius:10px;color:var(--tx);font-family:'Manrope',sans-serif;font-size:14px;font-weight:500;padding:10px 14px;outline:none;transition:border-color 0.15s}
#ci:focus{border-color:var(--acc)}
#ci:disabled{opacity:.5}
#ci::placeholder{color:var(--tx3)}
#rb{background:var(--acc);color:#fff;border:none;border-radius:10px;font-family:'Manrope',sans-serif;font-weight:700;font-size:14px;padding:0 20px;cursor:pointer;white-space:nowrap;transition:opacity 0.15s}
#rb:hover{opacity:0.85}
#rb:disabled{opacity:.4;cursor:not-allowed}
#ldg{display:none;align-items:center;gap:8px;margin-bottom:10px;font-size:13px;color:var(--tx2);font-weight:500}
#err{display:none;margin-top:8px;padding:10px 12px;background:var(--red-bg);border:1px solid rgba(255,82,82,0.2);border-radius:8px;color:var(--red);font-size:12px;font-weight:500;word-break:break-all}
.dot-pulse{width:8px;height:8px;border-radius:50%;background:var(--acc);animation:dp 1s ease-in-out infinite;flex-shrink:0}
@keyframes dp{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.3;transform:scale(0.7)}}
.action-row{display:flex;gap:8px;flex-wrap:wrap}
.pill-btn{display:inline-flex;align-items:center;background:var(--bg2);border:1.5px solid var(--bor);border-radius:20px;padding:5px 12px;font-family:'Manrope',sans-serif;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;transition:all 0.15s}
.pill-btn:hover{border-color:var(--bor2);color:var(--tx)}
.pill-btn.blu{color:var(--blu);border-color:var(--blu-bor);background:var(--blu-bg)}
.panel-extra{display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--bor)}
.panel-label{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px}
#bi,#ii{width:100%;background:var(--bg);border:1.5px solid var(--bor2);border-radius:10px;color:var(--tx);font-family:'Manrope',sans-serif;font-size:13px;padding:10px 14px;min-height:90px;resize:vertical;outline:none;line-height:1.6;font-weight:500}
#bi:focus{border-color:var(--acc)}
#ii{border-color:var(--blu-bor)}
#ii:focus{border-color:var(--blu)}
.act-btn2{background:var(--acc);color:#fff;border:none;border-radius:8px;font-family:'Manrope',sans-serif;font-weight:700;font-size:13px;padding:8px 16px;cursor:pointer;margin-top:8px;transition:opacity 0.15s}
.act-btn2:hover{opacity:0.85}
.act-btn2.blu{background:var(--blu)}
#ierr{display:none;color:var(--red);font-size:12px;margin-top:6px;font-weight:500}

.toolbar{display:none;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.f-btn{padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1.5px solid var(--bor);background:var(--bg2);color:var(--tx2);cursor:pointer;transition:all 0.15s;font-family:'Manrope',sans-serif}
.f-btn.on{background:var(--tx);border-color:var(--tx);color:var(--bg)}
.f-btn.on.hot{background:var(--grn);border-color:var(--grn);color:#000}
.f-btn.on.warm{background:var(--amb);border-color:var(--amb);color:#000}
.f-btn.on.cold{background:var(--tx3);border-color:var(--tx3);color:var(--bg)}
.tb-right{margin-left:auto;display:flex;gap:6px}
.tb-btn{padding:5px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1.5px solid var(--bor);background:var(--bg2);color:var(--tx2);cursor:pointer;font-family:'Manrope',sans-serif;transition:all 0.15s}
.tb-btn.danger{color:var(--red);border-color:rgba(255,82,82,0.2)}
.tb-btn.danger:hover{background:var(--red-bg)}

.card{background:var(--sur);border:1.5px solid var(--bor);border-radius:14px;margin-bottom:10px;overflow:hidden;transition:box-shadow 0.15s,border-color 0.15s}
.card:hover{box-shadow:0 4px 24px rgba(0,0,0,0.3);border-color:var(--bor2)}
.ctop{display:flex;align-items:center;gap:14px;padding:16px 18px;cursor:pointer}
.score-badge{min-width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:800;flex-shrink:0;letter-spacing:-0.02em}
.score-badge.hot{background:var(--grn-bg);color:var(--grn)}
.score-badge.warm{background:var(--amb-bg);color:var(--amb)}
.score-badge.cold{background:rgba(74,85,112,0.15);color:var(--tx3)}
.cinfo{flex:1;min-width:0}
.cname-row{display:flex;align-items:center;gap:8px;margin-bottom:3px}
.cname{font-size:16px;font-weight:800;color:var(--tx);letter-spacing:-0.02em}
.visit-link{font-size:10px;font-weight:700;color:var(--blu);background:var(--blu-bg);border:1px solid var(--blu-bor);border-radius:6px;padding:2px 7px;text-decoration:none;transition:background 0.15s}
.visit-link:hover{background:rgba(68,138,255,0.15)}
.cmeta{font-size:12px;color:var(--tx3);font-weight:500;display:flex;gap:6px;flex-wrap:wrap}
.clbl{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;flex-shrink:0}
.clbl.hot{background:var(--grn-bg);color:var(--grn)}
.clbl.warm{background:var(--amb-bg);color:var(--amb)}
.clbl.cold{background:rgba(74,85,112,0.15);color:var(--tx3)}
.chv{font-size:11px;color:var(--tx3);flex-shrink:0;transition:transform 0.2s}
.chv.open{transform:rotate(180deg)}

.cbody{display:none;border-top:1px solid var(--bor)}
.cbody.open{display:flex;flex-wrap:wrap}
.cleft{flex:1 1 280px;padding:18px;border-right:1px solid var(--bor)}
.cright{flex:1 1 220px;padding:18px;background:var(--bg3)}
.sec{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.08em;margin:14px 0 7px}
.sec:first-child{margin-top:0}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:4px}
.pcell{background:var(--bg);border:1px solid var(--bor2);border-radius:8px;padding:7px 10px}
.pkey{font-size:9px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px}
.pval{font-size:12px;font-weight:600;color:var(--tx)}
.pval.dim{color:var(--tx3);font-weight:400}
.pval a{color:var(--blu);text-decoration:none}
.social-chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:4px}
.social-chip{font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid var(--bor2);color:var(--tx2);text-decoration:none;background:var(--bg2);transition:border-color 0.15s}
.social-chip:hover{border-color:var(--bor2);color:var(--tx)}
.founder-row{display:flex;gap:10px;align-items:center;padding:8px 10px;background:var(--bg);border:1px solid var(--bor2);border-radius:8px;margin-bottom:5px}
.fav{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;flex-shrink:0}
.fname{font-size:12px;font-weight:700;color:var(--tx)}
.frole{font-size:11px;color:var(--tx3);font-weight:500}
.atext{font-size:12px;color:var(--tx2);line-height:1.7;font-weight:500}
.sig-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--bor)}
.sig-row:last-child{border-bottom:none}
.sig-label{font-size:12px;font-weight:500;color:var(--tx2)}
.sig-val{font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px}
.sig-val.y{background:var(--grn-bg);color:var(--grn)}
.sig-val.n{background:var(--red-bg);color:var(--red)}
.sig-val.u{background:rgba(74,85,112,0.15);color:var(--tx3)}
.pitch-box{background:var(--acc-bg);border:1.5px solid var(--acc-bor);border-radius:10px;padding:14px;margin-top:4px}
.pitch-label{font-size:10px;font-weight:700;color:var(--acc);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px}
.pitch-text{font-size:12px;color:#ffb89e;line-height:1.75;font-weight:500;font-style:italic}
.reach-val{font-size:13px;font-weight:700;color:var(--blu);margin-bottom:14px}

.cact{display:flex;gap:6px;padding:10px 18px;background:var(--bg);border-top:1px solid var(--bor);flex-wrap:wrap}
.abtn{font-size:12px;font-weight:600;padding:6px 12px;border-radius:8px;border:1.5px solid var(--bor);background:var(--bg2);color:var(--tx2);cursor:pointer;font-family:'Manrope',sans-serif;transition:all 0.15s}
.abtn:hover{border-color:var(--bor2);color:var(--tx)}
.abtn.primary{background:var(--acc);border-color:var(--acc);color:#fff}
.abtn.primary:hover{opacity:0.85}
.abtn.ghost{margin-left:auto;color:var(--tx3)}

.empty{text-align:center;padding:80px 20px}
.empty-icon{font-size:44px;margin-bottom:14px;opacity:0.25}
.empty-title{font-size:18px;font-weight:800;color:var(--tx2);margin-bottom:8px;letter-spacing:-0.02em}
.empty-sub{font-size:13px;color:var(--tx3);font-weight:500;line-height:1.8}
"""

JS = """
var DB = [], busy = false, fil = 'all', ti = null;
var activeSources = ['techcrunch','blockworks','theblock'];

var SYS = 'Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, gtm_readiness_score (integer 0-100), gtm_label (exactly "Hot Lead" if 80+, "Warm Lead" if 50-79, "Cold Lead" if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker. Use null for unknown.';
var FETCH_SYS = 'You are a funding news analyst. Search the web for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, blockchain, DeFi, fintech. Return ONLY a valid JSON array, no markdown. Each item: {"company":"Name","sector":"AI/Web3/etc","funding":"$XM","stage":"Seed/Series A/etc","source":"publication"}. Max 15 companies. Only include real recent raises.';

function load() {
  fetch('/db').then(function(r){return r.json();}).then(function(d){if(Array.isArray(d)){DB=d;renderAll();}}).catch(function(){DB=[];});
}
function save() {
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(DB)}).catch(function(){});
}

function showPanel(id) {
  ['bpanel','ipanel'].forEach(function(pid){
    var el=document.getElementById(pid);
    el.style.display=(pid===id&&el.style.display!=='block')?'block':'none';
  });
  document.getElementById('btog').textContent=document.getElementById('bpanel').style.display==='block'?'- Bulk research':'+ Bulk research';
  document.getElementById('itog').textContent=document.getElementById('ipanel').style.display==='block'?'- Import JSON':'+ Import JSON';
}

function fetchLeads() {
  var btn=document.getElementById('fetch-btn');
  var ldg=document.getElementById('fetch-loading');
  var errEl=document.getElementById('fetch-err');
  var res=document.getElementById('fetch-results');
  btn.disabled=true; errEl.style.display='none'; res.style.display='none'; ldg.style.display='flex';
  document.getElementById('fetch-msg').textContent='Searching funding news from the last 14 days...';
  var srcNames=activeSources.map(function(s){return s==='techcrunch'?'TechCrunch':s==='blockworks'?'Blockworks':s==='theblock'?'The Block':'crypto-fundraising.info';}).join(', ');
  var prompt='Search '+srcNames+' and other tech/crypto news for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, fintech. Return a JSON array of recently funded companies.';
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:prompt,system:FETCH_SYS,mode:'fetch'})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error) throw new Error(d.error);
    var t=d.text||''; t=t.replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']'); if(a<0||b<0) throw new Error('No results found');
    var cos=JSON.parse(t.slice(a,b+1)); if(!cos.length) throw new Error('No companies found');
    var list=document.getElementById('fetch-list'); list.innerHTML='';
    cos.forEach(function(co){
      var item=document.createElement('div'); item.className='fetch-item sel';
      item.innerHTML='<input type="checkbox" checked data-co="'+encodeURIComponent(JSON.stringify(co))+'"><div><div class="fetch-item-name">'+(co.company||'?')+'</div><div class="fetch-item-meta">'+[co.sector,co.funding,co.stage,co.source].filter(Boolean).join(' · ')+'</div></div>';
      item.onclick=function(e){if(e.target.type==='checkbox')return;var cb=item.querySelector('input');cb.checked=!cb.checked;item.classList.toggle('sel',cb.checked);updateCount();};
      item.querySelector('input').onchange=function(){item.classList.toggle('sel',this.checked);updateCount();};
      list.appendChild(item);
    });
    updateCount(); ldg.style.display='none'; res.style.display='block'; btn.disabled=false;
  }).catch(function(e){ldg.style.display='none';errEl.textContent='Error: '+e.message;errEl.style.display='block';btn.disabled=false;});
}

function updateCount(){var n=document.querySelectorAll('#fetch-list input:checked').length;document.getElementById('fetch-count').textContent=n+' selected';}

function researchSelected(){
  var cbs=document.querySelectorAll('#fetch-list input:checked');
  var names=[];
  cbs.forEach(function(cb){try{var co=JSON.parse(decodeURIComponent(cb.getAttribute('data-co')));if(co.company)names.push(co.company);}catch(e){}});
  if(!names.length)return;
  document.getElementById('fetch-results').style.display='none';
  var i=0; function next(){if(i>=names.length)return;run(names[i++],next);} next();
}

function go(){var v=document.getElementById('ci').value.trim();if(!v||busy)return;document.getElementById('ci').value='';run(v);}

function bulk(){
  if(busy)return;
  var names=document.getElementById('bi').value.trim().split('\\n').map(function(s){return s.trim();}).filter(Boolean);
  if(!names.length)return;
  document.getElementById('bi').value='';
  var i=0; function next(){if(i>=names.length)return;run(names[i++],next);} next();
}

function importJSON(){
  var raw=document.getElementById('ii').value.trim();
  var errEl=document.getElementById('ierr'); errEl.style.display='none';
  try{
    var clean=raw.replace(/```json/g,'').replace(/```/g,'').trim();
    var parsed=clean.charAt(0)==='['?JSON.parse(clean):[JSON.parse(clean.slice(clean.indexOf('{'),clean.lastIndexOf('}')+1))];
    var added=0;
    for(var i=0;i<parsed.length;i++){var r=parsed[i];if(r&&r.company){r._id='id'+Date.now()+Math.floor(Math.random()*9999);r._open=true;DB.unshift(r);added++;}}
    if(!added)throw new Error('No valid company objects found');
    save();renderAll();document.getElementById('ii').value='';document.getElementById('ipanel').style.display='none';document.getElementById('itog').textContent='+ Import JSON';
  }catch(e){errEl.textContent='Error: '+e.message;errEl.style.display='block';}
}

function run(company,callback){
  busy=true;document.getElementById('rb').disabled=true;document.getElementById('ci').disabled=true;
  document.getElementById('err').style.display='none';document.getElementById('lname').textContent=company;
  document.getElementById('ldg').style.display='flex';
  var secs=0;document.getElementById('ltimer').textContent='0s';
  ti=setInterval(function(){document.getElementById('ltimer').textContent=(++secs)+'s';},1000);
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:company,system:SYS})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('{'),b=t.lastIndexOf('}');if(a<0||b<0)throw new Error('No JSON returned');
    var res=JSON.parse(t.slice(a,b+1));res._id='id'+Date.now();res._open=true;DB.unshift(res);save();renderAll();
  }).catch(function(e){var el=document.getElementById('err');el.textContent='Error: '+e.message;el.style.display='block';})
  .finally(function(){clearInterval(ti);document.getElementById('ldg').style.display='none';document.getElementById('rb').disabled=false;document.getElementById('ci').disabled=false;busy=false;if(callback)setTimeout(callback,400);});
}

function sc(n){return n>=80?'hot':n>=50?'warm':'cold';}
function su(v){if(!v||v==='null'||v==='undefined')return '';return String(v).indexOf('http')===0?v:'https://'+v;}

function renderAll(){
  document.getElementById('stt').textContent=DB.length;
  document.getElementById('sth').textContent=DB.filter(function(r){return r.gtm_label==='Hot Lead';}).length;
  document.getElementById('empty').style.display=DB.length?'none':'block';
  document.getElementById('tb').style.display=DB.length?'flex':'none';
  renderCards();
}

function renderCards(){
  var shown=fil==='all'?DB:DB.filter(function(r){return r.gtm_label===(fil==='hot'?'Hot Lead':fil==='warm'?'Warm Lead':'Cold Lead');});
  var cont=document.getElementById('cards');cont.innerHTML='';
  shown.forEach(function(r){
    var n=r.gtm_readiness_score||0,cls=sc(n),s=r.socials||{},g=r.gtm_signals||{},ff=Array.isArray(r.founders)?r.founders:[],id=r._id,open=r._open,site=su(r.website);
    var card=document.createElement('div');card.className='card';
    var top=document.createElement('div');top.className='ctop';
    var metaParts=[r.sector,r.funding_amount,r.stage].filter(function(v){return v&&v!=='Unknown';});
    top.innerHTML='<div class="score-badge '+cls+'">'+n+'</div>'+
      '<div class="cinfo"><div class="cname-row"><span class="cname">'+(r.company||'')+'</span>'+(site?'<a class="visit-link" href="'+site+'" target="_blank">visit ↗</a>':'')+
      '</div><div class="cmeta">'+metaParts.join(' · ')+'</div></div>'+
      '<span class="clbl '+cls+'">'+(r.gtm_label||'')+'</span>'+
      '<span class="chv'+(open?' open':'')+'">▾</span>';
    top.onclick=function(){r._open=!r._open;save();renderCards();};
    card.appendChild(top);

    if(open){
      var body=document.createElement('div');body.className='cbody open';
      var left=document.createElement('div');left.className='cleft';
      var pg='<div class="pgrid">';
      [['Website',r.website,true],['HQ',r.hq],['Founded',r.founded],['Team',r.employee_count],['Stage',r.stage],['Product',r.product_status],['Funding',r.funding_amount],['Investor',r.lead_investor]].forEach(function(x){
        var u=x[2]?su(x[1]):'';pg+='<div class="pcell"><div class="pkey">'+x[0]+'</div><div class="pval'+((!x[1]||x[1]==='Unknown')?' dim':'')+'">'+
        (u?'<a href="'+u+'" target="_blank">'+String(x[1]).replace(/^https?:\/\//,'')+'</a>':(x[1]&&x[1]!=='Unknown'?x[1]:'—'))+'</div></div>';
      });pg+='</div>';
      var chips='<div class="social-chips">';
      var tw=s.twitter?'https://twitter.com/'+String(s.twitter).replace('@',''):'';
      [[tw,'𝕏 Twitter'],[s.linkedin,'in LinkedIn'],[s.discord,'◈ Discord'],[s.telegram,'✈ Telegram'],[s.github,'⌥ GitHub']].forEach(function(x){var u=su(x[0]);if(u)chips+='<a class="social-chip" href="'+u+'" target="_blank">'+x[1]+'</a>';});
      chips+='</div>';
      var avatarColors=[['rgba(255,92,53,0.15)','#FF5C35'],['rgba(0,230,118,0.12)','#00e676'],['rgba(68,138,255,0.12)','#448aff'],['rgba(255,179,0,0.12)','#ffb300']];
      var fnd='<div>';
      if(ff.length){ff.forEach(function(f,i){var ini=String(f.name||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('').toUpperCase();var ac=avatarColors[i%4];fnd+='<div class="founder-row"><div class="fav" style="background:'+ac[0]+';color:'+ac[1]+'">'+ini+'</div><div><div class="fname">'+(f.name||'')+'</div><div class="frole">'+(f.role||'')+(f.background?' · '+f.background:'')+'</div></div></div>';});}
      else fnd+='<div class="atext">Unknown</div>';fnd+='</div>';
      var inv=[r.lead_investor,r.other_investors].filter(function(v){return v&&v!=='null';}).join(', ');
      left.innerHTML='<div class="sec">Profile</div>'+pg+(inv?'<div class="sec">Investors</div><div class="atext" style="margin-bottom:4px">'+inv+'</div>':'')+
        '<div class="sec">Socials</div>'+chips+'<div class="sec">Founders</div>'+fnd+
        '<div class="sec">Community</div><div class="atext">'+(r.community_size||'Unknown')+'</div>'+
        '<div class="sec">Marketing</div><div class="atext">'+(r.marketing_notes||'—')+'</div>';

      var right=document.createElement('div');right.className='cright';
      var sigs='<div class="sec" style="margin-top:0">GTM Signals</div><div>';
      [['recently_funded','Recently funded'],['no_cmo','No CMO'],['pre_launch_or_early','Pre-launch / early GTM'],['has_product','Has product'],['small_team','Small team'],['marketing_gap_visible','Marketing gap'],['active_community','Active community']].forEach(function(x){
        var v=g[x[0]],cls2=v===true?'y':v===false?'n':'u',t=v===true?'Yes':v===false?'No':'?';
        sigs+='<div class="sig-row"><span class="sig-label">'+x[1]+'</span><span class="sig-val '+cls2+'">'+t+'</span></div>';
      });sigs+='</div>';
      right.innerHTML=sigs+'<div class="sec">Why They Fit</div><div class="atext" style="margin-bottom:12px">'+(r.why_fit||'—')+'</div>'+
        '<div class="sec">Risks</div><div class="atext" style="color:var(--amb);margin-bottom:12px">'+(r.risks||'—')+'</div>'+
        '<div class="sec">Reach Out To</div><div class="reach-val">'+(r.decision_maker||'—')+'</div>'+
        '<div class="pitch-box"><div class="pitch-label">🎯 Pitch Opener</div><div class="pitch-text" id="pt'+id+'">'+(r.pitch_opener||'—')+'</div></div>';

      body.appendChild(left);body.appendChild(right);card.appendChild(body);
      var acts=document.createElement('div');acts.className='cact';
      var cp=document.createElement('button');cp.className='abtn primary';cp.textContent='Copy Pitch';
      (function(cid){cp.onclick=function(){var el=document.getElementById('pt'+cid);if(el)navigator.clipboard.writeText(el.textContent);cp.textContent='Copied!';setTimeout(function(){cp.textContent='Copy Pitch';},1800);};})(id);
      acts.appendChild(cp);
      if(site){var sb=document.createElement('button');sb.className='abtn';sb.textContent='Visit Site';(function(u){sb.onclick=function(){window.open(u,'_blank');};})(site);acts.appendChild(sb);}
      var liu=su(s.linkedin);if(liu){var lb=document.createElement('button');lb.className='abtn';lb.textContent='LinkedIn';(function(u){lb.onclick=function(){window.open(u,'_blank');};})(liu);acts.appendChild(lb);}
      if(s.twitter&&s.twitter!=='null'){var twb=document.createElement('button');twb.className='abtn';twb.textContent='Twitter';(function(h){twb.onclick=function(){window.open('https://twitter.com/'+h.replace('@',''),'_blank');};})(s.twitter);acts.appendChild(twb);}
      var rm=document.createElement('button');rm.className='abtn ghost';rm.textContent='Remove';
      (function(cid){rm.onclick=function(){DB=DB.filter(function(x){return x._id!==cid;});save();renderAll();};})(id);
      acts.appendChild(rm);card.appendChild(acts);
    }
    cont.appendChild(card);
  });
}

function doCSV(){
  var h=['Company','Tagline','Website','Sector','HQ','Founded','Stage','Funding','Date','Lead Investor','Other Investors','Employees','Twitter','LinkedIn','Discord','Telegram','GitHub','Founders','Has CMO','Mktg Notes','Product','Community','Score','Label','Funded','No CMO','Pre-launch','Has Product','Small Team','Mktg Gap','Why Fit','Risks','Pitch','Decision Maker'];
  function e(v){var s=String(v==null?'':v).replace(/"/g,'""');return(s.indexOf(',')>=0||s.indexOf('\\n')>=0)?'"'+s+'"':s;}
  var rows=DB.map(function(r){var s=r.socials||{},g=r.gtm_signals||{},f=(r.founders||[]).map(function(x){return x.name+' ('+x.role+')';}).join('; ');
    return[r.company,r.tagline,r.website,r.sector,r.hq,r.founded,r.stage,r.funding_amount,r.funding_date,r.lead_investor,r.other_investors,r.employee_count,s.twitter,s.linkedin,s.discord,s.telegram,s.github,f,r.has_cmo,r.marketing_notes,r.product_status,r.community_size,r.gtm_readiness_score,r.gtm_label,g.recently_funded,g.no_cmo,g.pre_launch_or_early,g.has_product,g.small_team,g.marketing_gap_visible,r.why_fit,r.risks,r.pitch_opener,r.decision_maker].map(e).join(',');});
  var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([[h.join(',')].concat(rows).join('\\n')],{type:'text/csv'}));a.download='gtm-leads.csv';a.click();
}

document.addEventListener('DOMContentLoaded',function(){
  load();
  document.getElementById('rb').onclick=go;
  document.getElementById('ci').addEventListener('keydown',function(e){if(e.key==='Enter')go();});
  document.getElementById('btog').onclick=function(){showPanel('bpanel');};
  document.getElementById('itog').onclick=function(){showPanel('ipanel');};
  document.getElementById('brb').onclick=bulk;
  document.getElementById('iib').onclick=importJSON;
  document.getElementById('csvbtn').onclick=doCSV;
  document.getElementById('fetch-btn').onclick=fetchLeads;
  document.getElementById('res-sel-btn').onclick=researchSelected;
  document.getElementById('clrbtn').onclick=function(){if(confirm('Clear all saved companies?')){DB=[];save();renderAll();}};
  document.querySelectorAll('.src-pill').forEach(function(p){p.onclick=function(){var s=p.getAttribute('data-src');var i=activeSources.indexOf(s);if(i>=0){activeSources.splice(i,1);p.classList.remove('active');}else{activeSources.push(s);p.classList.add('active');};};});
  document.querySelectorAll('.f-btn').forEach(function(b){b.onclick=function(){fil=b.getAttribute('data-f');document.querySelectorAll('.f-btn').forEach(function(x){x.classList.remove('on');});b.classList.add('on');renderCards();};});
});
"""

HTML = ("<!DOCTYPE html>\n<html>\n<head>\n"
  "<meta charset='UTF-8'>\n"
  "<meta name='viewport' content='width=device-width,initial-scale=1.0'>\n"
  "<title>GTM Scout</title>\n"
  "<link rel='preconnect' href='https://fonts.googleapis.com'>\n"
  "<link href='https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap' rel='stylesheet'>\n"
  "<link rel='icon' href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎯</text></svg>\">\n"
  "<style>" + CSS + "</style>\n"
  "</head>\n<body>\n"

  "<div class='topbar'>"
    "<div class='logo-wrap'><div class='logo-icon'>🎯</div><span class='logo-text'>GTM Scout</span></div>"
    "<div class='topbar-right'>"
      "<div class='stat-pill'><span class='stat-n' id='stt'>0</span><span class='stat-l'>companies</span></div>"
      "<div class='stat-pill hot'><span class='stat-n' id='sth'>0</span><span class='stat-l'>hot leads</span></div>"
    "</div>"
  "</div>\n"

  "<div class='main'>"

  "<div class='fetch-card'>"
    "<div class='fetch-top'>"
      "<div><div class='fetch-title'>✨ Fetch New Leads</div><div class='fetch-sub'>Pull recently funded companies from free news sources</div></div>"
      "<button id='fetch-btn'>Fetch Leads</button>"
    "</div>"
    "<div class='source-pills'>"
      "<div class='src-pill active' data-src='techcrunch'>TechCrunch</div>"
      "<div class='src-pill active' data-src='blockworks'>Blockworks</div>"
      "<div class='src-pill active' data-src='theblock'>The Block</div>"
      "<div class='src-pill' data-src='cryptofunding'>crypto-fundraising.info</div>"
    "</div>"
    "<div id='fetch-loading'><div class='dot-pulse'></div><span id='fetch-msg'>Searching...</span></div>"
    "<div id='fetch-err'></div>"
    "<div id='fetch-results'>"
      "<div class='panel-label'>Select companies to research:</div>"
      "<div class='fetch-list' id='fetch-list'></div>"
      "<div style='display:flex;align-items:center'>"
        "<button id='res-sel-btn'>Research Selected</button>"
        "<span id='fetch-count'></span>"
      "</div>"
    "</div>"
  "</div>"

  "<div class='search-card'>"
    "<div class='search-row'>"
      "<input id='ci' type='text' placeholder='Or research a company manually, e.g. Privy, Alchemy...'>"
      "<button id='rb'>Research</button>"
    "</div>"
    "<div id='ldg'><div class='dot-pulse'></div><span>Searching for <b id='lname'></b>... <span id='ltimer'>0s</span></span></div>"
    "<div id='err'></div>"
    "<div class='action-row'>"
      "<button class='pill-btn' id='btog'>+ Bulk research</button>"
      "<button class='pill-btn blu' id='itog'>+ Import JSON</button>"
    "</div>"
    "<div class='panel-extra' id='bpanel'>"
      "<div class='panel-label'>One company per line</div>"
      "<textarea id='bi' placeholder='Privy&#10;Alchemy&#10;EigenLayer'></textarea>"
      "<button class='act-btn2' id='brb'>Research All</button>"
    "</div>"
    "<div class='panel-extra' id='ipanel'>"
      "<div class='panel-label' style='color:var(--blu)'>Paste JSON array or single company object</div>"
      "<textarea id='ii' placeholder='[{&quot;company&quot;:&quot;Privy&quot;,...}]'></textarea>"
      "<div id='ierr'></div>"
      "<button class='act-btn2 blu' id='iib'>Import</button>"
    "</div>"
  "</div>"

  "<div class='toolbar' id='tb'>"
    "<button class='f-btn on' data-f='all'>All</button>"
    "<button class='f-btn' data-f='hot'>🔥 Hot</button>"
    "<button class='f-btn' data-f='warm'>🌤 Warm</button>"
    "<button class='f-btn' data-f='cold'>🧊 Cold</button>"
    "<div class='tb-right'>"
      "<button class='tb-btn' id='csvbtn'>↓ Export CSV</button>"
      "<button class='tb-btn danger' id='clrbtn'>Clear All</button>"
    "</div>"
  "</div>"

  "<div id='cards'></div>"
  "<div class='empty' id='empty'>"
    "<div class='empty-icon'>🎯</div>"
    "<div class='empty-title'>No leads yet</div>"
    "<div class='empty-sub'>Fetch leads from funding news above,<br>or type a company name to research manually.</div>"
  "</div>"
  "</div>"
  "<script>" + JS + "</script>\n"
  "</body>\n</html>\n")


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path == '/db':
            data = json.dumps(load_db()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        content = HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(length))
                save_db(data)
                self.respond({'ok': True})
            except Exception as e:
                self.respond({'error': str(e)})
            return
        if self.path != '/api':
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length))
        except:
            self.respond({'error': 'Bad request'}); return

        key = body.get('key', '').strip()
        company = body.get('company', '').strip()
        system = body.get('system', '')
        mode = body.get('mode', 'research')
        actual_key = os.environ.get('ANTHROPIC_API_KEY', key)

        if not actual_key: self.respond({'error': 'No API key configured'}); return
        if not company: self.respond({'error': 'Missing company name'}); return

        if mode == 'fetch':
            # Web search for fetch mode
            messages = [{'role': 'user', 'content': 'Search the web and complete this task: ' + company}]
            final_text = ''
            for _ in range(10):
                payload = json.dumps({'model': 'claude-sonnet-4-20250514', 'max_tokens': 1500, 'system': system,
                    'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}], 'messages': messages}).encode('utf-8')
                req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                    headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        data = json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    self.respond({'error': 'API error ' + str(e.code) + ': ' + e.read().decode()[:300]}); return
                except Exception as e:
                    self.respond({'error': str(e)}); return
                content = data.get('content', [])
                stop_reason = data.get('stop_reason', '')
                for block in content:
                    if block.get('type') == 'text': final_text = block.get('text', '')
                if stop_reason == 'end_turn': break
                elif stop_reason == 'tool_use':
                    messages.append({'role': 'assistant', 'content': content})
                    messages.append({'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': b['id'], 'content': [{'type': 'text', 'text': 'ok'}]} for b in content if b.get('type') == 'tool_use']})
                else: break
            self.respond({'text': final_text})
        else:
            # No web search for manual research — much cheaper
            payload = json.dumps({'model': 'claude-sonnet-4-20250514', 'max_tokens': 1200, 'system': system,
                'messages': [{'role': 'user', 'content': 'Research this company and return the JSON profile: "' + company + '"'}]}).encode('utf-8')
            req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read())
                text = ''.join(b.get('text','') for b in data.get('content',[]) if b.get('type')=='text')
                self.respond({'text': text})
            except urllib.error.HTTPError as e:
                self.respond({'error': 'API error ' + str(e.code) + ': ' + e.read().decode()[:300]})
            except Exception as e:
                self.respond({'error': str(e)})

    def respond(self, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print('\n  GTM Scout running at http://localhost:' + str(PORT))
    print('  Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)
