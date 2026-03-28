#!/usr/bin/env python3
#v9
import http.server, json, urllib.request, urllib.error, time, sys, os, socket

def find_port():
    for p in range(8765, 8800):
        try:
            s = socket.socket(); s.bind(('', p)); s.close(); return p
        except: continue
    return 8765

PORT = int(os.environ.get('PORT', find_port()))
# Persistent storage via JSONBin.io (free, survives Railway deploys)
JSONBIN_BIN_ID = os.environ.get('JSONBIN_BIN_ID', '')
JSONBIN_API_KEY = os.environ.get('JSONBIN_API_KEY', '')

def load_db():
    # Try JSONBin first
    if JSONBIN_BIN_ID and JSONBIN_API_KEY:
        try:
            req = urllib.request.Request(
                'https://api.jsonbin.io/v3/b/' + JSONBIN_BIN_ID + '/latest',
                headers={'X-Master-Key': JSONBIN_API_KEY, 'X-Bin-Meta': 'false'},
                method='GET'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                data = json.loads(raw)
                if isinstance(data, list):
                    print('[DB] Loaded', len(data), 'records from JSONBin')
                    return data
                print('[DB] JSONBin returned non-list:', type(data), str(raw)[:100])
        except Exception as e:
            print('[DB] JSONBin load error:', e)
    else:
        print('[DB] No JSONBin credentials - BIN_ID:', bool(JSONBIN_BIN_ID), 'API_KEY:', bool(JSONBIN_API_KEY))
    # Fallback to local file
    try:
        db_file = '/tmp/scout_db.json'
        if os.path.exists(db_file):
            with open(db_file) as f:
                data = json.load(f)
            if isinstance(data, list):
                print('[DB] Loaded', len(data), 'records from local file')
                return data
    except Exception as e:
        print('[DB] Local load error:', e)
    return []

def save_db(data):
    # Always save to local file first as immediate backup
    try:
        db_file = '/tmp/scout_db.json'
        with open(db_file, 'w') as f:
            json.dump(data, f)
        print('[DB] Saved', len(data), 'records to local file')
    except Exception as e:
        print('[DB] Local save error:', e)
    # Then try JSONBin
    if JSONBIN_BIN_ID and JSONBIN_API_KEY:
        try:
            payload = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                'https://api.jsonbin.io/v3/b/' + JSONBIN_BIN_ID,
                data=payload,
                headers={'Content-Type': 'application/json', 'X-Master-Key': JSONBIN_API_KEY},
                method='PUT'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                print('[DB] Saved', len(data), 'records to JSONBin, status:', resp.status)
        except Exception as e:
            print('[DB] JSONBin save error:', e)
    else:
        print('[DB] No JSONBin credentials - BIN_ID:', bool(JSONBIN_BIN_ID), 'API_KEY:', bool(JSONBIN_API_KEY))

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07090f;--sur:#0e1119;--sur2:#141824;
  --bor:#1d2333;--bor2:#252d3f;
  --grn:#00e676;--grn-dim:rgba(0,230,118,0.08);--grn-bor:rgba(0,230,118,0.2);
  --amb:#ffb300;--red:#ff5252;--blu:#448aff;
  --tx:#dde4f0;--tx2:#8492aa;--tx3:#4a5570;
}
body{background:var(--bg);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:13px;min-height:100vh}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-bottom:1px solid var(--bor);position:sticky;top:0;background:var(--bg);z-index:10}
.topbar-left{display:flex;align-items:center;gap:12px}
.logo-mark{width:28px;height:28px;background:var(--grn);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px;color:#000}
.logo-text{font-size:16px;font-weight:800;letter-spacing:-0.02em}
.stats{display:flex;gap:20px}
.stat-n{font-size:20px;font-weight:800;color:var(--grn);text-align:right;line-height:1}
.stat-l{font-size:8px;color:var(--tx3);text-transform:uppercase;text-align:right}
.main{max-width:980px;margin:0 auto;padding:24px}
.panel{background:var(--sur);border:1px solid var(--bor);padding:16px;margin-bottom:12px}
.irow{display:flex;gap:8px}
#ci{flex:1;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:13px;padding:10px 14px;outline:none}
#ci:focus{border-color:var(--grn)}
#ci:disabled{opacity:.5}
#rb{background:var(--grn);color:#000;border:none;font-weight:700;font-size:12px;padding:0 20px;cursor:pointer;white-space:nowrap;font-family:'JetBrains Mono',monospace}
#rb:hover{opacity:.85}
#rb:disabled{opacity:.35;cursor:not-allowed}
#ldg{display:none;align-items:center;gap:10px;margin-top:12px;padding-top:12px;border-top:1px solid var(--bor);font-size:11px;color:var(--tx3)}
.spinner{width:13px;height:13px;border:2px solid var(--bor2);border-top-color:var(--grn);border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}
.timer{margin-left:auto;font-size:10px;color:var(--tx3)}
#err{display:none;margin-top:10px;padding:10px 14px;background:rgba(255,82,82,0.06);border:1px solid rgba(255,82,82,0.2);color:var(--red);font-size:11px;word-break:break-all;line-height:1.6}
.action-row{display:flex;gap:16px;margin-top:10px}
.tlink{background:none;border:none;color:var(--tx3);font-size:10px;cursor:pointer;font-family:'JetBrains Mono',monospace;text-decoration:underline;padding:0}
.tlink.blu{color:var(--blu)}
.panel-extra{display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--bor)}
.panel-label{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px}
#bi,#ii{width:100%;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:'JetBrains Mono',monospace;font-size:12px;padding:8px 12px;min-height:80px;resize:vertical;outline:none;line-height:1.6}
#bi:focus{border-color:var(--grn)}
#ii{border-color:rgba(68,138,255,0.3)}
#ii:focus{border-color:var(--blu)}
.sub-btn{background:var(--grn);color:#000;border:none;font-weight:700;font-size:12px;padding:8px 18px;cursor:pointer;margin-top:8px;font-family:'JetBrains Mono',monospace}
.sub-btn.blu{background:var(--blu);color:#fff}
#ierr{display:none;color:var(--red);font-size:11px;margin-top:6px}

.fetch-panel{background:var(--grn-dim);border:1px solid var(--grn-bor);padding:16px;margin-bottom:12px}
.fetch-title{font-size:13px;font-weight:700;color:var(--grn);margin-bottom:4px}
.fetch-sub{font-size:10px;color:var(--tx3);margin-bottom:12px}
.fetch-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.src-pills{display:flex;gap:6px;flex-wrap:wrap}
.src-pill{padding:3px 10px;font-size:10px;font-weight:600;border:1px solid var(--bor);background:var(--bg);color:var(--tx3);cursor:pointer;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.04em}
.src-pill.on{border-color:var(--grn);color:var(--grn);background:var(--grn-dim)}
#fetch-btn{background:var(--grn);color:#000;border:none;font-weight:700;font-size:11px;padding:8px 16px;cursor:pointer;font-family:'JetBrains Mono',monospace;white-space:nowrap;flex-shrink:0}
#fetch-btn:disabled{opacity:.35;cursor:not-allowed}
#fetch-ldg{display:none;align-items:center;gap:8px;font-size:11px;color:var(--tx3);margin-top:10px}
#fetch-err{display:none;margin-top:10px;padding:10px;background:rgba(255,82,82,0.06);border:1px solid rgba(255,82,82,0.2);color:var(--red);font-size:11px}
#fetch-results{display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--grn-bor)}
.fetch-list{display:flex;flex-direction:column;gap:4px;margin-bottom:10px;max-height:260px;overflow-y:auto}
.fetch-item{display:flex;align-items:center;gap:8px;padding:8px 10px;background:var(--bg);border:1px solid var(--bor);cursor:pointer}
.fetch-item:hover{border-color:var(--grn)}
.fetch-item.sel{border-color:var(--grn);background:var(--grn-dim)}
.fetch-item input{accent-color:var(--grn);width:14px;height:14px;cursor:pointer;flex-shrink:0}
.fetch-item-name{font-size:12px;font-weight:700;color:var(--tx)}
.fetch-item-meta{font-size:10px;color:var(--tx3);margin-top:1px}
#res-sel-btn{background:var(--grn);color:#000;border:none;font-weight:700;font-size:11px;padding:8px 16px;cursor:pointer;font-family:'JetBrains Mono',monospace}
#fetch-count{font-size:10px;color:var(--tx3);margin-left:10px}

.toolbar{display:none;align-items:center;gap:6px;margin-bottom:10px;flex-wrap:wrap}
.fb{font-size:9px;padding:3px 10px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:'JetBrains Mono',monospace;text-transform:uppercase}
.fb.on{border-color:var(--grn);color:var(--grn)}
.tb-right{margin-left:auto;display:flex;gap:6px}
.tb-btn{font-size:10px;padding:5px 12px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:'JetBrains Mono',monospace}
.tb-btn.danger{color:var(--red);border-color:rgba(255,82,82,0.2)}

.card{background:var(--sur);border:1px solid var(--bor);margin-bottom:2px}
.ctop{display:flex;align-items:center;gap:12px;padding:11px 16px;cursor:pointer}
.ctop:hover{background:rgba(255,255,255,.015)}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.cinfo{flex:1;min-width:0}
.cname-row{display:flex;align-items:center;gap:8px;margin-bottom:2px}
.cname{font-size:15px;font-weight:700}
.visit-link{font-size:9px;color:var(--blu);border:1px solid var(--bor);padding:1px 5px;text-decoration:none}
.cmeta{display:flex;gap:8px;flex-wrap:wrap}
.cmeta span{font-size:10px;color:var(--tx3)}
.score-area{display:flex;align-items:center;gap:8px;flex-shrink:0}
.clbl{font-size:9px;font-weight:600;padding:2px 8px;text-transform:uppercase;border:1px solid;white-space:nowrap}
.cscore{font-size:20px;font-weight:800;min-width:28px;text-align:right}
.cbody{display:none;border-top:1px solid var(--bor)}
.cbody.open{display:flex;flex-wrap:wrap}
.cleft{flex:1 1 280px;padding:16px;border-right:1px solid var(--bor)}
.cright{flex:1 1 220px;padding:16px;background:var(--sur2)}
.sec{font-size:8px;color:var(--tx3);text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;display:flex;align-items:center;gap:8px}
.sec::after{content:'';flex:1;height:1px;background:var(--bor)}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:14px}
.pcell{background:var(--bg);border:1px solid var(--bor);padding:6px 8px}
.pkey{font-size:8px;color:var(--tx3);text-transform:uppercase;margin-bottom:2px}
.pval{font-size:11px;color:var(--tx)}
.pval.dim{color:var(--tx3);font-style:italic}
.pval a{color:var(--blu);text-decoration:none}
.social-links{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:14px}
.social-links a{font-size:10px;padding:3px 8px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none}
.social-links a:hover{border-color:var(--tx2)}
.founder-row{display:flex;gap:8px;align-items:center;padding:6px 8px;background:var(--bg);border:1px solid var(--bor);margin-bottom:3px}
.fav{width:26px;height:26px;border-radius:50%;background:var(--bor2);display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:var(--grn);flex-shrink:0}
.fname{font-size:12px;font-weight:500}
.frole{font-size:10px;color:var(--tx3)}
.atext{font-size:11px;color:var(--tx2);line-height:1.7}
.sig-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid var(--bor);font-size:11px}
.sig-row:last-child{border-bottom:none}
.sy{font-size:10px;font-weight:600;color:var(--grn)}
.sn{font-size:10px;font-weight:600;color:var(--red)}
.su{font-size:10px;font-weight:600;color:var(--tx3)}
.pitch-box{background:var(--grn-dim);border:1px solid var(--grn-bor);padding:12px;margin-top:4px}
.pitch-label{font-size:8px;color:var(--grn);text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px}
.pitch-text{font-size:11px;color:#c8ffe0;line-height:1.75;font-style:italic}
.cact{display:flex;gap:5px;padding:10px 16px;background:var(--bg);border-top:1px solid var(--bor);flex-wrap:wrap}
.abtn{font-size:10px;padding:5px 10px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:'JetBrains Mono',monospace}
.abtn:hover{border-color:var(--tx2)}
.abtn.g{border-color:var(--grn-bor);color:var(--grn)}
.abtn.g:hover{background:var(--grn-dim)}
.abtn.ghost{margin-left:auto;color:var(--tx3)}
.empty{text-align:center;padding:60px 20px;color:var(--tx3);font-size:11px;line-height:2}
.empty-title{font-size:15px;font-weight:700;color:var(--tx2);margin-bottom:8px}
"""

JS = """
var DB = [], busy = false, fil = 'all', ti = null;
var activeSources = ['techcrunch','blockworks','theblock'];

var SYS = "Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, hiring_remote (bool - true if they have open remote job listings especially marketing/growth/comms roles), gtm_readiness_score (integer 0-100), gtm_label (exactly Hot Lead if 80+, Warm Lead if 50-79, Cold Lead if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker, outreach_status (always set to not_contacted). Use null for unknown.";
var FETCH_SYS = "You are a funding news analyst. Search the web for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, blockchain, DeFi, fintech. Return ONLY a valid JSON array, no markdown. Each item: {company:Name,sector:AI/Web3/etc,funding:$XM,stage:Seed/Series A/etc,source:publication}. Max 15 companies. Only include real recent raises.";

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
  var ldg=document.getElementById('fetch-ldg');
  var errEl=document.getElementById('fetch-err');
  var res=document.getElementById('fetch-results');
  btn.disabled=true; errEl.style.display='none'; res.style.display='none'; ldg.style.display='flex';
  var srcNames=activeSources.map(function(s){return s==='techcrunch'?'TechCrunch':s==='blockworks'?'Blockworks':s==='theblock'?'The Block':'crypto-fundraising.info';}).join(', ');
  var prompt='Search '+srcNames+' and other tech/crypto news for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, fintech. Return a JSON array of recently funded companies.';
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:prompt,system:FETCH_SYS,mode:'fetch'})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=d.text||'';t=t.replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']');if(a<0||b<0)throw new Error('No results found');
    var cos=JSON.parse(t.slice(a,b+1));if(!cos.length)throw new Error('No companies found');
    var list=document.getElementById('fetch-list');list.innerHTML='';
    cos.forEach(function(co){
      var item=document.createElement('div');item.className='fetch-item sel';
      item.innerHTML='<input type="checkbox" checked data-co="'+encodeURIComponent(JSON.stringify(co))+'"><div><div class="fetch-item-name">'+(co.company||'?')+'</div><div class="fetch-item-meta">'+[co.sector,co.funding,co.stage,co.source].filter(Boolean).join(' · ')+'</div></div>';
      item.onclick=function(e){if(e.target.type==='checkbox')return;var cb=item.querySelector('input');cb.checked=!cb.checked;item.classList.toggle('sel',cb.checked);updateCount();};
      item.querySelector('input').onchange=function(){item.classList.toggle('sel',this.checked);updateCount();};
      list.appendChild(item);
    });
    updateCount();ldg.style.display='none';res.style.display='block';btn.disabled=false;
  }).catch(function(e){ldg.style.display='none';errEl.textContent='Error: '+e.message;errEl.style.display='block';btn.disabled=false;});
}

function updateCount(){var n=document.querySelectorAll('#fetch-list input:checked').length;document.getElementById('fetch-count').textContent=n+' selected';}

function researchSelected(){
  var cbs=document.querySelectorAll('#fetch-list input:checked');
  var names=[];
  cbs.forEach(function(cb){try{var co=JSON.parse(decodeURIComponent(cb.getAttribute('data-co')));if(co.company)names.push(co.company);}catch(e){}});
  if(!names.length)return;
  document.getElementById('fetch-results').style.display='none';
  var i=0;function next(){if(i>=names.length)return;run(names[i++],next);}next();
}

function go(){var v=document.getElementById('ci').value.trim();if(!v||busy)return;document.getElementById('ci').value='';run(v);}

function bulk(){
  if(busy)return;
  var names=document.getElementById('bi').value.trim().split('\\n').map(function(s){return s.trim();}).filter(Boolean);
  if(!names.length)return;
  document.getElementById('bi').value='';
  var i=0;function next(){if(i>=names.length)return;run(names[i++],next);}next();
}

function importJSON(){
  var raw=document.getElementById('ii').value.trim();
  var errEl=document.getElementById('ierr');errEl.style.display='none';
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

function sc(n){return n>=80?'var(--grn)':n>=50?'var(--amb)':'var(--tx3)';}
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
    var n=r.gtm_readiness_score||0,c=sc(n),s=r.socials||{},g=r.gtm_signals||{},ff=Array.isArray(r.founders)?r.founders:[],id=r._id,open=r._open,site=su(r.website);
    var card=document.createElement('div');card.className='card';
    var top=document.createElement('div');top.className='ctop';
    var metaHtml=[r.sector,r.funding_amount,r.stage].filter(function(v){return v&&v!=='Unknown';}).map(function(v){return '<span>'+v+'</span>';}).join('');
    var remoteBadge = r.hiring_remote ? '<span style="font-size:9px;color:var(--blu);border:1px solid rgba(68,138,255,0.3);padding:1px 6px;margin-left:4px;font-weight:600">hiring remotely</span>' : '';
    top.innerHTML='<div class="dot" style="background:'+c+'"></div>'+
      '<div class="cinfo"><div class="cname-row"><span class="cname">'+(r.company||'')+'</span>'+(site?'<a class="visit-link" href="'+site+'" target="_blank">visit</a>':'')+remoteBadge+
      '</div><div class="cmeta">'+metaHtml+'</div></div>'+
      '<div class="score-area"><span class="clbl" style="color:'+c+';border-color:'+c+'">'+(r.gtm_label||'')+'</span><span class="cscore" style="color:'+c+'">'+n+'</span></div>';
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
      var chips='<div class="social-links">';
      var tw=s.twitter?'https://twitter.com/'+String(s.twitter).replace('@',''):'';
      [[tw,'Twitter'],[s.linkedin,'LinkedIn'],[s.discord,'Discord'],[s.telegram,'Telegram'],[s.github,'GitHub']].forEach(function(x){var u=su(x[0]);if(u)chips+='<a href="'+u+'" target="_blank">'+x[1]+'</a>';});
      chips+='</div>';
      var fnd='<div style="margin-bottom:14px">';
      if(ff.length){ff.forEach(function(f){var ini=String(f.name||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('').toUpperCase();fnd+='<div class="founder-row"><div class="fav">'+ini+'</div><div><div class="fname">'+(f.name||'')+'</div><div class="frole">'+(f.role||'')+(f.background?' · '+f.background:'')+'</div></div></div>';});}
      else fnd+='<div class="atext">Unknown</div>';fnd+='</div>';
      var inv=[r.lead_investor,r.other_investors].filter(function(v){return v&&v!=='null';}).join(', ');
      left.innerHTML='<div class="sec">Profile</div>'+pg+(inv?'<div class="sec">Investors</div><div class="atext" style="margin-bottom:14px">'+inv+'</div>':'')+
        '<div class="sec">Socials</div>'+chips+'<div class="sec">Founders</div>'+fnd+
        '<div class="sec">Community</div><div class="atext" style="margin-bottom:12px">'+(r.community_size||'Unknown')+'</div>'+
        '<div class="sec">Marketing</div><div class="atext">'+(r.marketing_notes||'—')+'</div>';

      var right=document.createElement('div');right.className='cright';
      var sigs='<div class="sec" style="margin-top:0">GTM Signals</div><div>';
      [['recently_funded','Recently funded'],['no_cmo','No CMO'],['pre_launch_or_early','Pre-launch / early GTM'],['has_product','Has product'],['small_team','Small team'],['marketing_gap_visible','Marketing gap'],['active_community','Active community']].forEach(function(x){
        var v=g[x[0]],cls=v===true?'sy':v===false?'sn':'su',t=v===true?'Yes':v===false?'No':'?';
        sigs+='<div class="sig-row"><span style="color:var(--tx2)">'+x[1]+'</span><span class="'+cls+'">'+t+'</span></div>';
      });sigs+='</div>';
      right.innerHTML=sigs+'<div class="sec">Why They Fit</div><div class="atext" style="margin-bottom:12px">'+(r.why_fit||'—')+'</div>'+
        '<div class="sec">Risks</div><div class="atext" style="color:var(--amb);margin-bottom:12px">'+(r.risks||'—')+'</div>'+
        '<div class="sec">Reach Out To</div><div class="atext" style="color:var(--blu);margin-bottom:12px">'+(r.decision_maker||'—')+'</div>'+
        '<div class="pitch-box"><div class="pitch-label">Pitch Opener</div><div class="pitch-text" id="pt'+id+'">'+(r.pitch_opener||'—')+'</div></div>';

      body.appendChild(left);body.appendChild(right);card.appendChild(body);
      var acts=document.createElement('div');acts.className='cact';
      var cp=document.createElement('button');cp.className='abtn g';cp.textContent='Copy Pitch';
      (function(cid){cp.onclick=function(){var el=document.getElementById('pt'+cid);if(el)navigator.clipboard.writeText(el.textContent);cp.textContent='Copied!';setTimeout(function(){cp.textContent='Copy Pitch';},1800);};})(id);
      acts.appendChild(cp);
      if(site){var sb=document.createElement('button');sb.className='abtn';sb.textContent='Visit Site';(function(u){sb.onclick=function(){window.open(u,'_blank');};})(site);acts.appendChild(sb);}
      var liu=su(s.linkedin);if(liu){var lb=document.createElement('button');lb.className='abtn';lb.textContent='LinkedIn';(function(u){lb.onclick=function(){window.open(u,'_blank');};})(liu);acts.appendChild(lb);}
      if(s.twitter&&s.twitter!=='null'){var twb=document.createElement('button');twb.className='abtn';twb.textContent='Twitter';(function(h){twb.onclick=function(){window.open('https://twitter.com/'+h.replace('@',''),'_blank');};})(s.twitter);acts.appendChild(twb);}
      // Status button
      var statusColors = {'not_contacted':'var(--tx3)','contacted':'var(--amb)','in_talks':'var(--blu)','closed':'var(--grn)'};
      var statusLabels = {'not_contacted':'Not Contacted','contacted':'Contacted','in_talks':'In Talks','closed':'Closed ✓'};
      var statusBtn = document.createElement('button');
      statusBtn.className='abtn';
      var curStatus = r.outreach_status || 'not_contacted';
      statusBtn.textContent = statusLabels[curStatus] || 'Not Contacted';
      statusBtn.style.color = statusColors[curStatus] || 'var(--tx3)';
      statusBtn.style.borderColor = statusColors[curStatus] || 'var(--bor2)';
      (function(rec){
        statusBtn.onclick = function(){
          var order = ['not_contacted','contacted','in_talks','closed'];
          var cur = rec.outreach_status || 'not_contacted';
          var next = order[(order.indexOf(cur)+1)%order.length];
          rec.outreach_status = next;
          save(); renderCards();
        };
      })(r);
      acts.appendChild(statusBtn);
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
  document.getElementById('clrbtn').onclick=function(){if(confirm('Clear all?')){DB=[];save();renderAll();}};
  document.querySelectorAll('.src-pill').forEach(function(p){p.onclick=function(){var s=p.getAttribute('data-src');var i=activeSources.indexOf(s);if(i>=0){activeSources.splice(i,1);p.classList.remove('on');}else{activeSources.push(s);p.classList.add('on');};};});
  document.querySelectorAll('.fb').forEach(function(b){b.onclick=function(){fil=b.getAttribute('data-f');document.querySelectorAll('.fb').forEach(function(x){x.classList.remove('on');});b.classList.add('on');renderCards();};});
});
"""

HTML = ("<!DOCTYPE html>\n<html>\n<head>\n"
  "<meta charset='UTF-8'>\n"
  "<title>Scout</title>\n"
  "<link href='https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@300;400;500&display=swap' rel='stylesheet'>\n"
  "<link rel='icon' type='image/png' href='data:image/png;base64,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'>\n"
  "<style>" + CSS + "</style>\n"
  "</head>\n<body>\n"

  "<div class='topbar'>"
    "<div class='topbar-left'>"
      "<img src='data:image/png;base64,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' style='width:32px;height:32px;object-fit:contain;display:block;'>"
      "<span class='logo-text' style=\"font-family:'Syne',sans-serif\">Scout</span>"
    "</div>"
    "<div class='stats'>"
      "<div><div class='stat-n' id='stt'>0</div><div class='stat-l'>Total</div></div>"
      "<div><div class='stat-n' id='sth'>0</div><div class='stat-l'>Hot Leads</div></div>"
    "</div>"
  "</div>\n"

  "<div class='main'>"

  "<div class='fetch-panel'>"
    "<div class='fetch-top'>"
      "<div><div class='fetch-title'>Fetch New Leads</div><div class='fetch-sub'>Pull recently funded companies from free news sources</div></div>"
      "<button id='fetch-btn'>Fetch Leads →</button>"
    "</div>"
    "<div class='src-pills'>"
      "<div class='src-pill on' data-src='techcrunch'>TechCrunch</div>"
      "<div class='src-pill on' data-src='blockworks'>Blockworks</div>"
      "<div class='src-pill on' data-src='theblock'>The Block</div>"
      "<div class='src-pill' data-src='cryptofunding'>crypto-fundraising.info</div>"
    "</div>"
    "<div id='fetch-ldg'><div class='spinner'></div><span id='fetch-msg'>Searching funding news...</span></div>"
    "<div id='fetch-err'></div>"
    "<div id='fetch-results'>"
      "<div style='font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px'>Select companies to research:</div>"
      "<div class='fetch-list' id='fetch-list'></div>"
      "<div style='display:flex;align-items:center'>"
        "<button id='res-sel-btn'>Research Selected →</button>"
        "<span id='fetch-count'></span>"
      "</div>"
    "</div>"
  "</div>"

  "<div class='panel'>"
    "<div class='irow'>"
      "<input id='ci' type='text' placeholder='Company name, e.g. Privy, Alchemy, EigenLayer...'>"
      "<button id='rb'>Research →</button>"
    "</div>"
    "<div id='ldg'><div class='spinner'></div><span>Researching <b id='lname'></b>... <span id='ltimer'>0s</span></span><span class='timer' id='ltimer2'></span></div>"
    "<div id='err'></div>"
    "<div class='action-row'>"
      "<button class='tlink' id='btog'>+ Bulk research</button>"
      "<button class='tlink blu' id='itog'>+ Import JSON</button>"
    "</div>"
    "<div class='panel-extra' id='bpanel'>"
      "<div class='panel-label'>One company per line</div>"
      "<textarea id='bi' placeholder='Privy&#10;Alchemy&#10;EigenLayer'></textarea>"
      "<button class='sub-btn' id='brb'>Research All →</button>"
    "</div>"
    "<div class='panel-extra' id='ipanel'>"
      "<div class='panel-label' style='color:var(--blu)'>Paste JSON array or single company object</div>"
      "<textarea id='ii' placeholder='[{&quot;company&quot;:&quot;Privy&quot;,...}]'></textarea>"
      "<div id='ierr'></div>"
      "<button class='sub-btn blu' id='iib'>Import</button>"
    "</div>"
  "</div>"

  "<div class='toolbar' id='tb'>"
    "<button class='fb on' data-f='all'>All</button>"
    "<button class='fb' data-f='hot'>Hot</button>"
    "<button class='fb' data-f='warm'>Warm</button>"
    "<button class='fb' data-f='cold'>Cold</button>"
    "<div class='tb-right'>"
      "<button class='tb-btn' id='csvbtn'>↓ Export CSV</button>"
      "<button class='tb-btn danger' id='clrbtn'>Clear All</button>"
    "</div>"
  "</div>"

  "<div id='cards'></div>"
  "<div class='empty' id='empty'>"
    "<div class='empty-title'>No companies yet</div>"
    "Fetch leads from funding news above, or type a company name and hit Research.<br>"
    "Full profile, GTM score, pitch opener, CSV export."
  "</div>"
  "</div>"
  "<script>" + JS + "</script>\n"
  "</body>\n</html>\n")


PIN_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#07090f;color:#dde4f0;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#0e1119;border:1px solid #1d2333;padding:40px;width:320px;text-align:center}
.logo{width:36px;height:36px;background:#00e676;color:#000;font-weight:800;font-size:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 20px}
h2{font-size:16px;font-weight:700;margin-bottom:6px;letter-spacing:-0.02em}
p{font-size:10px;color:#4a5570;margin-bottom:24px;text-transform:uppercase;letter-spacing:.1em}
.dots{display:flex;gap:12px;justify-content:center;margin-bottom:24px}
.dot{width:14px;height:14px;border-radius:50%;border:2px solid #1d2333;background:transparent;transition:background 0.15s}
.dot.filled{background:#00e676;border-color:#00e676}
.numpad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
.key{background:#141824;border:1px solid #1d2333;color:#dde4f0;font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;padding:14px;cursor:pointer;transition:background 0.1s}
.key:hover{background:#1d2333}
.key:active{background:#252d3f}
.key.del{color:#4a5570;font-size:12px}
#err{color:#ff5252;font-size:11px;min-height:16px;margin-top:4px}
</style>
</head>
<body>
<div class="box">
  <img src="data:image/png;base64,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" style="width:36px;height:36px;object-fit:contain;display:block;margin:0 auto 20px;">
  <h2>Scout</h2>
  <p>Enter PIN to continue</p>
  <div class="dots" id="dots">
    <div class="dot" id="d0"></div>
    <div class="dot" id="d1"></div>
    <div class="dot" id="d2"></div>
    <div class="dot" id="d3"></div>
  </div>
  <div class="numpad">
    <button class="key" onclick="press(1)">1</button>
    <button class="key" onclick="press(2)">2</button>
    <button class="key" onclick="press(3)">3</button>
    <button class="key" onclick="press(4)">4</button>
    <button class="key" onclick="press(5)">5</button>
    <button class="key" onclick="press(6)">6</button>
    <button class="key" onclick="press(7)">7</button>
    <button class="key" onclick="press(8)">8</button>
    <button class="key" onclick="press(9)">9</button>
    <button class="key" onclick="press(0)" style="grid-column:2">0</button>
    <button class="key del" onclick="del()">⌫</button>
  </div>
  <div id="err"></div>
</div>
<script>
var entered = '';
var correct = '__PIN__';
function press(n) {
  if (entered.length >= 4) return;
  entered += n;
  update();
  if (entered.length === 4) {
    setTimeout(check, 150);
  }
}
function del() {
  entered = entered.slice(0,-1);
  update();
  document.getElementById('err').textContent = '';
}
function update() {
  for (var i=0;i<4;i++) {
    document.getElementById('d'+i).classList.toggle('filled', i < entered.length);
  }
}
function check() {
  if (entered === correct) {
    window.location.href = '/app';
  } else {
    entered = '';
    update();
    document.getElementById('err').textContent = 'Incorrect PIN';
    for(var i=0;i<4;i++) document.getElementById('d'+i).style.borderColor='#ff5252';
    setTimeout(function(){for(var i=0;i<4;i++) document.getElementById('d'+i).style.borderColor='';},800);
  }
}
document.addEventListener('keydown', function(e) {
  if (e.key >= '0' && e.key <= '9') press(parseInt(e.key));
  if (e.key === 'Backspace') del();
});
</script>
</body>
</html>'''

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path == '/dbtest':
            result = {'bin_id': bool(JSONBIN_BIN_ID), 'api_key': bool(JSONBIN_API_KEY), 'records': 0, 'error': None}
            try:
                req = urllib.request.Request(
                    'https://api.jsonbin.io/v3/b/' + JSONBIN_BIN_ID + '/latest',
                    headers={'X-Master-Key': JSONBIN_API_KEY, 'X-Bin-Meta': 'false'},
                    method='GET'
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                    result['records'] = len(data) if isinstance(data, list) else -1
                    result['type'] = str(type(data))
                    result['preview'] = str(data)[:200] if not isinstance(data, list) else 'list ok'
            except Exception as e:
                result['error'] = str(e)
            out = json.dumps(result).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return
        if self.path == '/db':
            data = json.dumps(load_db()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        # Serve PIN page if PIN is set
        app_pin = os.environ.get('APP_PIN', '')
        if app_pin and self.path == '/':
            content = PIN_HTML.replace('__PIN__', app_pin).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path not in ('/', '/app', ''):
            self.send_response(404); self.end_headers(); return
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


def monday_autofetch():
    """Runs every Monday at 8am UTC, auto-fetches leads and saves to DB"""
    import threading, datetime
    def schedule():
        while True:
            now = datetime.datetime.utcnow()
            # Check if it's Monday (weekday 0) and 8am UTC
            if now.weekday() == 0 and now.hour == 8 and now.minute == 0:
                print('  [Auto-fetch] Running Monday morning lead fetch...')
                try:
                    key = os.environ.get('ANTHROPIC_API_KEY','')
                    if not key:
                        time.sleep(60); continue
                    FETCH_SYS = 'You are a funding news analyst. Search the web for startup funding announcements from the last 7 days. Focus on AI, web3, crypto, blockchain, DeFi, fintech. Return ONLY a valid JSON array, no markdown. Each item: {"company":"Name","sector":"AI/Web3/etc","funding":"$XM","stage":"Seed/Series A/etc","source":"publication"}. Max 15 companies. Only include real recent raises.'
                    messages = [{'role':'user','content':'Search TechCrunch, Blockworks, and The Block for startup funding announcements from the last 7 days. Return a JSON array of recently funded companies.'}]
                    final_text = ''
                    for _ in range(10):
                        payload = json.dumps({'model':'claude-sonnet-4-20250514','max_tokens':1500,'system':FETCH_SYS,'tools':[{'type':'web_search_20250305','name':'web_search'}],'messages':messages}).encode('utf-8')
                        req = urllib.request.Request('https://api.anthropic.com/v1/messages',data=payload,headers={'Content-Type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01'},method='POST')
                        with urllib.request.urlopen(req,timeout=90) as resp:
                            data = json.loads(resp.read())
                        content = data.get('content',[])
                        stop_reason = data.get('stop_reason','')
                        for block in content:
                            if block.get('type')=='text': final_text=block.get('text','')
                        if stop_reason=='end_turn': break
                        elif stop_reason=='tool_use':
                            messages.append({'role':'assistant','content':content})
                            messages.append({'role':'user','content':[{'type':'tool_result','tool_use_id':b['id'],'content':[{'type':'text','text':'ok'}]} for b in content if b.get('type')=='tool_use']})
                        else: break
                    # Parse and save companies
                    t = final_text.replace('```json','').replace('```','').strip()
                    a,b2 = t.find('['),t.rfind(']')
                    if a>=0 and b2>=0:
                        companies = json.loads(t[a:b2+1])
                        db = load_db()
                        existing = set(r.get('company','').lower() for r in db)
                        added = 0
                        for co in companies:
                            if co.get('company') and co['company'].lower() not in existing:
                                co['_id'] = 'auto_'+str(int(time.time()))+'_'+co['company'].replace(' ','_')
                                co['_open'] = False
                                co['outreach_status'] = 'not_contacted'
                                co['gtm_label'] = 'Warm Lead'
                                co['gtm_readiness_score'] = 60
                                co['auto_fetched'] = True
                                db.insert(0, co)
                                existing.add(co['company'].lower())
                                added += 1
                        if added:
                            save_db(db)
                            print(f'  [Auto-fetch] Added {added} new companies to DB')
                except Exception as e:
                    print(f'  [Auto-fetch] Error: {e}')
                time.sleep(60)  # sleep 1 min after running to avoid double-trigger
            else:
                time.sleep(30)  # check every 30 seconds
    threading.Thread(target=schedule, daemon=True).start()

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    monday_autofetch()
    print('\n  Scout running at http://localhost:' + str(PORT))
    print('  Monday auto-fetch: enabled (8am UTC)')
    print('  Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)
