#!/usr/bin/env python3
import http.server, json, urllib.request, urllib.error, threading, time, sys, os

import os
PORT = int(os.environ.get('PORT', 8765))

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GTM Scout</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
:root { --bg:#07090f;--sur:#0e1119;--sur2:#141824;--bor:#1d2333;--bor2:#252d3f;--grn:#00e676;--amb:#ffb300;--red:#ff5252;--blu:#448aff;--tx:#dde4f0;--tx2:#8492aa;--tx3:#4a5570; }
body { background:var(--bg);color:var(--tx);font-family:monospace;font-size:13px;min-height:100vh; }
.topbar { display:flex;align-items:center;justify-content:space-between;padding:13px 24px;border-bottom:1px solid var(--bor);position:sticky;top:0;background:var(--bg);z-index:10; }
.logo { color:var(--grn);font-weight:bold;font-size:16px;letter-spacing:-.01em; }
.stats { display:flex;gap:20px; }
.stat-n { font-size:20px;font-weight:bold;color:var(--grn);text-align:right; }
.stat-l { font-size:9px;color:var(--tx3);text-transform:uppercase;text-align:right; }
.main { max-width:960px;margin:0 auto;padding:24px; }
.panel { background:var(--sur);border:1px solid var(--bor);padding:16px;margin-bottom:12px; }
.irow { display:flex;gap:8px; }
#ci { flex:1;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:monospace;font-size:13px;padding:10px 14px;outline:none; }
#ci:focus { border-color:var(--grn); }
#ci:disabled { opacity:.5; }
#rb { background:var(--grn);color:#000;border:none;font-weight:bold;font-size:13px;padding:0 20px;cursor:pointer;white-space:nowrap; }
#rb:disabled { opacity:.35;cursor:not-allowed; }
.btog { background:none;border:none;color:var(--tx3);font-size:10px;cursor:pointer;text-decoration:underline;font-family:monospace;margin-top:8px;display:block; }
.barea { display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--bor); }
.barea.open { display:block; }
#bi { width:100%;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:monospace;font-size:12px;padding:8px 12px;min-height:80px;resize:vertical;outline:none;line-height:1.6; }
#ldg { display:none;margin-top:12px;color:var(--tx3);font-size:12px; }
#err { display:none;margin-top:10px;padding:10px;background:rgba(255,82,82,.1);border:1px solid rgba(255,82,82,.3);color:var(--red);font-size:12px;word-break:break-all; }
.tb { display:none;align-items:center;gap:6px;margin-bottom:10px;flex-wrap:wrap; }
.fb { font-size:9px;padding:3px 10px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:monospace;text-transform:uppercase; }
.fb.on { border-color:var(--grn);color:var(--grn); }
.cbtn { margin-left:auto;font-size:10px;padding:5px 12px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:monospace; }
.xbtn { font-size:10px;padding:5px 12px;background:none;border:1px solid rgba(255,82,82,.3);color:var(--red);cursor:pointer;font-family:monospace; }
.card { background:var(--sur);border:1px solid var(--bor);margin-bottom:4px; }
.ctop { display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer; }
.ctop:hover { background:rgba(255,255,255,.02); }
.cname { font-size:15px;font-weight:bold;flex:1; }
.cscore { font-size:20px;font-weight:bold; }
.clbl { font-size:10px;padding:2px 8px;border:1px solid;text-transform:uppercase; }
.cbody { display:none;border-top:1px solid var(--bor); }
.cbody.open { display:flex;flex-wrap:wrap; }
.cleft { flex:1 1 280px;padding:16px;border-right:1px solid var(--bor); }
.cright { flex:1 1 220px;padding:16px;background:var(--sur2); }
.grid { display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:14px; }
.cell { background:var(--bg);border:1px solid var(--bor);padding:6px 8px; }
.ck { font-size:9px;color:var(--tx3);text-transform:uppercase;margin-bottom:2px; }
.cv { font-size:11px; }
.cv a { color:var(--blu);text-decoration:none; }
.sec { font-size:9px;color:var(--tx3);text-transform:uppercase;margin:12px 0 6px; }
.lks { display:flex;flex-wrap:wrap;gap:4px;margin-bottom:12px; }
.lks a { font-size:10px;padding:3px 8px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none; }
.sr { display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--bor);font-size:11px; }
.sy { color:var(--grn);font-weight:bold; }
.sn { color:var(--red);font-weight:bold; }
.su { color:var(--tx3); }
.pb { background:rgba(0,230,118,.07);border:1px solid rgba(0,230,118,.2);padding:12px;margin-top:12px; }
.pb p { font-size:9px;color:var(--grn);text-transform:uppercase;margin-bottom:6px; }
.pb div { font-size:11px;color:#c8ffe0;line-height:1.75;font-style:italic; }
.cact { display:flex;gap:6px;padding:10px 16px;background:var(--bg);border-top:1px solid var(--bor);flex-wrap:wrap; }
.cact button { font-size:10px;padding:5px 10px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:monospace; }
.cact button.g { border-color:rgba(0,230,118,.3);color:var(--grn); }
.empty { text-align:center;padding:60px 20px;color:var(--tx3);font-size:12px;line-height:2; }
</style>
</head>
<body>
<div class="topbar">
  <span class="logo">GTM Scout</span>
  <div class="stats">
    <div><div class="stat-n" id="stt">0</div><div class="stat-l">Total</div></div>
    <div><div class="stat-n" id="sth">0</div><div class="stat-l">Hot Leads</div></div>
  </div>
</div>
<div class="main">
  <div class="panel">
    <div class="irow">
      <input id="ci" type="text" placeholder="Company name, e.g. Privy, Alchemy, EigenLayer...">
      <button id="rb">Research</button>
    </div>
    <div id="ldg">Searching the web for <span id="lname"></span>... <span id="ltimer">0s</span></div>
    <div id="err"></div>
    <div style="display:flex;gap:8px;margin-top:8px">
      <button class="btog" id="btog">+ Bulk research</button>
      <button class="btog" id="itog" style="color:var(--blu)">+ Import JSON</button>
    </div>
    <div class="barea" id="barea">
      <div style="font-size:9px;color:var(--tx3);text-transform:uppercase;margin-bottom:6px">One company per line</div>
      <textarea id="bi" placeholder="Privy&#10;Alchemy&#10;EigenLayer"></textarea>
      <div style="margin-top:8px"><button id="brb" style="background:var(--grn);color:#000;border:none;font-weight:bold;font-size:12px;padding:8px 18px;cursor:pointer;">Research All</button></div>
    </div>
    <div class="barea" id="iarea">
      <div style="font-size:9px;color:var(--blu);text-transform:uppercase;margin-bottom:6px">Paste JSON array or single company JSON</div>
      <textarea id="ii" placeholder='[{"company":"Privy","gtm_label":"Hot Lead",...}, {...}]' style="border-color:rgba(68,138,255,0.3)"></textarea>
      <div id="ierr" style="color:var(--red);font-size:11px;margin-top:4px;display:none"></div>
      <div style="margin-top:8px"><button id="iib" style="background:var(--blu);color:#fff;border:none;font-weight:bold;font-size:12px;padding:8px 18px;cursor:pointer;">Import</button></div>
    </div>
  </div>
  <div class="tb" id="tb">
    <button class="fb on" data-f="all">All</button>
    <button class="fb" data-f="hot">Hot</button>
    <button class="fb" data-f="warm">Warm</button>
    <button class="fb" data-f="cold">Cold</button>
    <button class="cbtn" id="csvbtn">Export CSV</button>
    <button class="xbtn" id="clrbtn">Clear All</button>
  </div>
  <div id="cards"></div>
  <div class="empty" id="empty">Type a company name and hit Research.<br>Results are saved automatically and will be here when you come back.</div>
</div>
<script>
var DB=[];var busy=false;var fil='all';var ti=null;
var SYS='Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, gtm_readiness_score (integer 0-100), gtm_label (exactly "Hot Lead" if 80+, "Warm Lead" if 50-79, "Cold Lead" if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker. Use null for unknown.';
function load(){try{var s=localStorage.getItem('gtm_db');if(s)DB=JSON.parse(s);}catch(e){DB=[];}}
function save(){try{localStorage.setItem('gtm_db',JSON.stringify(DB));}catch(e){}}
window.onload=function(){
  load();renderAll();
  document.getElementById('ci').onkeydown=function(e){if(e.key==='Enter')go();};
  document.getElementById('rb').onclick=go;
  document.getElementById('brb').onclick=bulk;
  document.getElementById('csvbtn').onclick=doCSV;
  document.getElementById('clrbtn').onclick=function(){if(confirm('Clear all saved companies?')){DB=[];save();renderAll();}};
  document.getElementById('btog').onclick=function(){var a=document.getElementById('barea');var o=a.classList.toggle('open');document.getElementById('btog').textContent=o?'- Bulk research':'+ Bulk research';document.getElementById('iarea').classList.remove('open');document.getElementById('itog').textContent='+ Import JSON';};
  document.getElementById('itog').onclick=function(){var a=document.getElementById('iarea');var o=a.classList.toggle('open');document.getElementById('itog').textContent=o?'- Import JSON':'+ Import JSON';document.getElementById('barea').classList.remove('open');document.getElementById('btog').textContent='+ Bulk research';};
  document.getElementById('iib').onclick=function(){
    var raw=document.getElementById('ii').value.trim();
    var err=document.getElementById('ierr');
    err.style.display='none';
    try{
      var clean=raw.replace(/```json/g,'').replace(/```/g,'').trim();
      var start=clean.indexOf('[')>=0&&(clean.indexOf('[')<clean.indexOf('{')||clean.indexOf('{')<0)?clean.indexOf('['):clean.indexOf('{');
      var parsed;
      if(clean.trimStart().startsWith('[')){parsed=JSON.parse(clean);}
      else{var s=clean.indexOf('{'),e=clean.lastIndexOf('}');parsed=[JSON.parse(clean.slice(s,e+1))];}
      if(!Array.isArray(parsed))parsed=[parsed];
      var added=0;
      parsed.forEach(function(r){if(r&&r.company){r._id='id'+Date.now()+Math.random();r._open=true;DB.unshift(r);added++;}});
      if(!added)throw new Error('No valid company objects found');
      save();renderAll();
      document.getElementById('ii').value='';
      document.getElementById('iarea').classList.remove('open');
      document.getElementById('itog').textContent='+ Import JSON';
    }catch(e){err.textContent='Error: '+e.message;err.style.display='block';}
  };
  document.querySelectorAll('.fb').forEach(function(b){b.onclick=function(){fil=b.getAttribute('data-f');document.querySelectorAll('.fb').forEach(function(x){x.classList.remove('on');});b.classList.add('on');renderCards();};});
};
function go(){var v=document.getElementById('ci').value.trim();if(!v||busy)return;document.getElementById('ci').value='';run(v);}
async function bulk(){if(busy)return;var names=document.getElementById('bi').value.trim().split('\n').map(function(s){return s.trim();}).filter(Boolean);if(!names.length)return;document.getElementById('bi').value='';for(var i=0;i<names.length;i++)await run(names[i]);}
async function run(company){
  busy=true;document.getElementById('rb').disabled=true;document.getElementById('ci').disabled=true;
  document.getElementById('err').style.display='none';document.getElementById('lname').textContent=company;document.getElementById('ldg').style.display='block';
  var s=0;ti=setInterval(function(){document.getElementById('ltimer').textContent=(++s)+'s';},1000);
  try{
    var r=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:company,system:SYS})});
    var d=await r.json();
    if(d.error)throw new Error(d.error);
    var t=d.text||'';t=t.replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('{'),b=t.lastIndexOf('}');if(a<0||b<0)throw new Error('No JSON returned');
    var res=JSON.parse(t.slice(a,b+1));res._id='id'+Date.now();res._open=true;DB.unshift(res);save();renderAll();
  }catch(e){var el=document.getElementById('err');el.textContent='Error: '+e.message;el.style.display='block';}
  clearInterval(ti);document.getElementById('ldg').style.display='none';document.getElementById('rb').disabled=false;document.getElementById('ci').disabled=false;busy=false;
}
function sc(n){return n>=80?'#00e676':n>=50?'#ffb300':'#888';}
function su(v){if(!v||v==='null')return '';return String(v).startsWith('http')?v:'https://'+v;}
function renderAll(){document.getElementById('stt').textContent=DB.length;document.getElementById('sth').textContent=DB.filter(function(r){return r.gtm_label==='Hot Lead';}).length;document.getElementById('empty').style.display=DB.length?'none':'block';document.getElementById('tb').style.display=DB.length?'flex':'none';renderCards();}
function renderCards(){
  var shown=fil==='all'?DB:DB.filter(function(r){return r.gtm_label===(fil==='hot'?'Hot Lead':fil==='warm'?'Warm Lead':'Cold Lead');});
  var cont=document.getElementById('cards');cont.innerHTML='';
  shown.forEach(function(r){
    var n=r.gtm_readiness_score||0,c=sc(n),s=r.socials||{},g=r.gtm_signals||{},ff=Array.isArray(r.founders)?r.founders:[],id=r._id,open=r._open,site=su(r.website);
    var card=document.createElement('div');card.className='card';
    var top=document.createElement('div');top.className='ctop';
    top.innerHTML='<span class="cscore" style="color:'+c+'">'+n+'</span><div class="cname">'+(r.company||'')+(site?' <a href="'+site+'" target="_blank" style="font-size:10px;color:#448aff;font-weight:normal;border:1px solid #1d2333;padding:1px 5px;text-decoration:none;margin-left:4px">visit</a>':'')+
      '<div style="font-size:10px;color:#4a5570;margin-top:2px">'+[r.sector,r.funding_amount,r.stage].filter(function(v){return v&&v!=='Unknown';}).join(' &middot; ')+'</div></div>'+
      '<span class="clbl" style="color:'+c+';border-color:'+c+'">'+(r.gtm_label||'')+'</span>';
    top.onclick=function(){r._open=!r._open;save();renderCards();};card.appendChild(top);
    if(open){
      var body=document.createElement('div');body.className='cbody open';
      var left=document.createElement('div');left.className='cleft';
      var pg='<div class="grid">';
      [['Website',r.website,true],['HQ',r.hq],['Founded',r.founded],['Team',r.employee_count],['Stage',r.stage],['Product',r.product_status],['Funding',r.funding_amount],['Investor',r.lead_investor]].forEach(function(x){var u=x[2]?su(x[1]):'';pg+='<div class="cell"><div class="ck">'+x[0]+'</div><div class="cv">';if(u)pg+='<a href="'+u+'" target="_blank">'+String(x[1]).replace(/^https?:\/\//,'')+'</a>';else pg+=(x[1]&&x[1]!=='Unknown')?x[1]:'<span style="color:#4a5570">&mdash;</span>';pg+='</div></div>';});pg+='</div>';
      var lks='<div class="lks">';[[s.twitter?'https://twitter.com/'+String(s.twitter).replace('@',''):'','Twitter'],[s.linkedin,'LinkedIn'],[s.discord,'Discord'],[s.telegram,'Telegram'],[s.github,'GitHub']].forEach(function(x){var u=su(x[0]);if(u)lks+='<a href="'+u+'" target="_blank">'+x[1]+'</a>';});lks+='</div>';
      var fnd='<div style="margin-bottom:12px">';if(ff.length){ff.forEach(function(f){var ini=String(f.name||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('').toUpperCase();fnd+='<div style="display:flex;gap:8px;align-items:center;padding:6px 8px;background:#07090f;border:1px solid #1d2333;margin-bottom:3px"><div style="width:24px;height:24px;border-radius:50%;background:#1d2333;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:bold;color:#00e676;flex-shrink:0">'+ini+'</div><div><div style="font-size:12px;font-weight:500">'+(f.name||'')+'</div><div style="font-size:10px;color:#4a5570">'+(f.role||'')+(f.background?' - '+f.background:'')+'</div></div></div>';});}else fnd+='<div style="font-size:11px;color:#4a5570">Unknown</div>';fnd+='</div>';
      var inv=[r.lead_investor,r.other_investors].filter(function(v){return v&&v!=='null';}).join(', ');
      left.innerHTML='<div class="sec">Profile</div>'+pg+(inv?'<div class="sec">Investors</div><div style="font-size:11px;color:#8492aa;margin-bottom:12px">'+inv+'</div>':'')+'<div class="sec">Socials</div>'+lks+'<div class="sec">Founders</div>'+fnd+'<div class="sec">Community</div><div style="font-size:11px;color:#8492aa;margin-bottom:12px">'+(r.community_size||'Unknown')+'</div><div class="sec">Marketing</div><div style="font-size:11px;color:#8492aa">'+(r.marketing_notes||'&mdash;')+'</div>';
      var right=document.createElement('div');right.className='cright';
      var sigs='<div class="sec" style="margin-top:0">GTM Signals</div>';[['recently_funded','Recently funded'],['no_cmo','No CMO'],['pre_launch_or_early','Pre-launch / early GTM'],['has_product','Has product'],['small_team','Small team'],['marketing_gap_visible','Marketing gap'],['active_community','Active community']].forEach(function(x){var v=g[x[0]],cls=v===true?'sy':v===false?'sn':'su',t=v===true?'Yes':v===false?'No':'?';sigs+='<div class="sr"><span>'+x[1]+'</span><span class="'+cls+'">'+t+'</span></div>';});
      right.innerHTML=sigs+'<div class="sec">Why They Fit</div><div style="font-size:11px;color:#8492aa;line-height:1.7;margin-bottom:12px">'+(r.why_fit||'&mdash;')+'</div><div class="sec">Risks</div><div style="font-size:11px;color:#ffb300;line-height:1.7;margin-bottom:12px">'+(r.risks||'&mdash;')+'</div><div class="sec">Reach Out To</div><div style="font-size:11px;color:#448aff;margin-bottom:12px">'+(r.decision_maker||'&mdash;')+'</div><div class="pb"><p>Pitch Opener</p><div id="pt'+id+'">'+(r.pitch_opener||'&mdash;')+'</div></div>';
      body.appendChild(left);body.appendChild(right);card.appendChild(body);
      var acts=document.createElement('div');acts.className='cact';
      var cp=document.createElement('button');cp.className='g';cp.textContent='Copy Pitch';cp.onclick=function(){var el=document.getElementById('pt'+id);if(el)navigator.clipboard.writeText(el.textContent);cp.textContent='Copied!';setTimeout(function(){cp.textContent='Copy Pitch';},1800);};acts.appendChild(cp);
      if(site){var sb=document.createElement('button');sb.textContent='Visit Site';sb.onclick=function(){window.open(site,'_blank');};acts.appendChild(sb);}
      var liu=su(s.linkedin);if(liu){var lb=document.createElement('button');lb.textContent='LinkedIn';lb.onclick=function(){window.open(liu,'_blank');};acts.appendChild(lb);}
      if(s.twitter&&s.twitter!=='null'){var tb2=document.createElement('button');tb2.textContent='Twitter';tb2.onclick=function(){window.open('https://twitter.com/'+String(s.twitter).replace('@',''),'_blank');};acts.appendChild(tb2);}
      var rm=document.createElement('button');rm.textContent='Remove';rm.style.marginLeft='auto';rm.onclick=function(){DB=DB.filter(function(x){return x._id!==id;});save();renderAll();};acts.appendChild(rm);
      card.appendChild(acts);
    }
    cont.appendChild(card);
  });
}
function doCSV(){
  var h=['Company','Tagline','Website','Sector','HQ','Founded','Stage','Funding','Date','Lead Investor','Other Investors','Employees','Twitter','LinkedIn','Discord','Telegram','GitHub','Founders','Has CMO','Mktg Notes','Product','Community','Score','Label','Funded','No CMO','Pre-launch','Has Product','Small Team','Mktg Gap','Why Fit','Risks','Pitch','Decision Maker'];
  function e(v){var s=String(v==null?'':v).replace(/"/g,'""');return(s.indexOf(',')>=0||s.indexOf('\n')>=0)?'"'+s+'"':s;}
  var rows=DB.map(function(r){var s=r.socials||{},g=r.gtm_signals||{},f=(r.founders||[]).map(function(x){return x.name+' ('+x.role+')';}).join('; ');return[r.company,r.tagline,r.website,r.sector,r.hq,r.founded,r.stage,r.funding_amount,r.funding_date,r.lead_investor,r.other_investors,r.employee_count,s.twitter,s.linkedin,s.discord,s.telegram,s.github,f,r.has_cmo,r.marketing_notes,r.product_status,r.community_size,r.gtm_readiness_score,r.gtm_label,g.recently_funded,g.no_cmo,g.pre_launch_or_early,g.has_product,g.small_team,g.marketing_gap_visible,r.why_fit,r.risks,r.pitch_opener,r.decision_maker].map(e).join(',');});
  var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([[h.join(',')].concat(rows).join('\n')],{type:'text/csv'}));a.download='gtm-leads.csv';a.click();
}
</script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        content = HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path != '/api':
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length))
        except:
            self.respond({'error': 'Invalid JSON body'})
            return

        key = body.get('key', '').strip()
        company = body.get('company', '').strip()
        system = body.get('system', '')

        if not key:
            self.respond({'error': 'Missing API key'})
            return
        if not company:
            self.respond({'error': 'Missing company name'})
            return

        payload = json.dumps({
            'model': 'claude-haiku-4-5-20251001',
            'max_tokens': 1200,
            'system': system,
            'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}],
            'messages': [{'role': 'user', 'content': 'Search the web and research this company thoroughly, then return the JSON profile: "' + company + '". Search for their website, funding, founders, team size, socials (Twitter, LinkedIn, Discord, GitHub), and whether they have a CMO.'}]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': key,
                'anthropic-version': '2023-06-01'
            },
            method='POST'
        )
        try:
            messages = [{'role': 'user', 'content': 'Search the web and research this company thoroughly, then return the JSON profile: "' + company + '". Search for their website, funding, founders, team size, socials (Twitter, LinkedIn, Discord, GitHub), and whether they have a CMO.'}]
            final_text = ''
            for _ in range(10):  # agentic loop for web search
                # Use server-side API key from environment, ignore client-provided key
                actual_key = os.environ.get('ANTHROPIC_API_KEY', key)
                req2 = urllib.request.Request(
                    'https://api.anthropic.com/v1/messages',
                    data=json.dumps({
                        'model': 'claude-haiku-4-5-20251001',
                        'max_tokens': 1200,
                        'system': system,
                        'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}],
                        'messages': messages
                    }).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'x-api-key': actual_key,
                        'anthropic-version': '2023-06-01'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(req2, timeout=90) as resp2:
                    data = json.loads(resp2.read())
                content = data.get('content', [])
                stop_reason = data.get('stop_reason', '')
                # collect any text
                for block in content:
                    if block.get('type') == 'text':
                        final_text = block.get('text', '')
                if stop_reason == 'end_turn':
                    break
                if stop_reason == 'tool_use':
                    # feed tool results back
                    messages.append({'role': 'assistant', 'content': content})
                    tool_results = []
                    for block in content:
                        if block.get('type') == 'tool_use':
                            tool_results.append({
                                'type': 'tool_result',
                                'tool_use_id': block['id'],
                                'content': [{'type': 'text', 'text': 'Search completed.'}]
                            })
                    messages.append({'role': 'user', 'content': tool_results})
                else:
                    break
            self.respond({'text': final_text})
        except urllib.error.HTTPError as e:
            err = e.read().decode('utf-8', errors='replace')
            self.respond({'error': 'API error ' + str(e.code) + ': ' + err[:300]})
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
    url = 'http://localhost:' + str(PORT)
    print('')
    print('  GTM Scout running at ' + url)
    print('  Press Ctrl+C to stop.')
    print('')
    # auto-open removed for web deployment
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)
