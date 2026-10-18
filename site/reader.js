(() => {
  const get = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const set = (key,val) => { try { localStorage.setItem(key,val); } catch {} };
  let size = Math.max(17, Math.min(25, Number(get('ms-font')) || 20));
  const applySize = () => { document.documentElement.style.setProperty('--reading-size',size+'px'); set('ms-font',size); document.querySelector('#smaller').disabled=size<=17; document.querySelector('#larger').disabled=size>=25; };
  applySize();
  document.querySelector('#smaller').onclick = () => { size=Math.max(17,size-1);applySize(); };
  document.querySelector('#larger').onclick = () => { size=Math.min(25,size+1);applySize(); };
  const theme=document.querySelector('#theme');
  const applyTheme=dark => { document.body.classList.toggle('dark',dark);theme.setAttribute('aria-pressed',String(dark));theme.setAttribute('aria-label',dark?'Attiva lettura chiara':'Attiva lettura scura');set('ms-dark',dark?'1':'0'); };
  applyTheme(get('ms-dark')==='1');theme.onclick=()=>applyTheme(!document.body.classList.contains('dark'));
  document.querySelector('#top').onclick=()=>window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  const toggle=document.querySelector('.index-toggle');
  toggle.onclick=()=>{ const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));document.querySelector('.reader-index').classList.toggle('open',open); };
  const links=[...document.querySelectorAll('#chapter-links a')];
  for(const a of links) a.addEventListener('click',()=>{toggle.setAttribute('aria-expanded','false');document.querySelector('.reader-index').classList.remove('open');});
  const last=get('ms-hydesville-chapter');const resume=document.querySelector('#resume');
  if(last && document.getElementById(last)){resume.href='#'+last;resume.hidden=false;}
  const sections=[...document.querySelectorAll('.chapter')];
  let queued=false;
  function update(){
    queued=false;const total=document.documentElement.scrollHeight-innerHeight;
    document.querySelector('#progress').style.width=(total>0?scrollY/total*100:0)+'%';
    let current=null;for(const s of sections){if(s.getBoundingClientRect().top<180)current=s;else break;}
    for(const a of links){const active=current && a.hash==='#'+current.id;a.classList.toggle('active',!!active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}
    if(current)set('ms-hydesville-chapter',current.id);
  }
  addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(update);}},{passive:true});
  addEventListener('resize',update);update();
})();
