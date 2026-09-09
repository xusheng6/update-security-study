'use strict';
const state = { records: [], tier: 'all', query: '', page: 1 };
const size = 50;
const $ = id => document.getElementById(id);
function textElement(tag, text, className) {
  const el = document.createElement(tag); el.textContent = text;
  if (className) el.className = className;
  return el;
}
function render() {
  const query = state.query.trim().toLocaleLowerCase();
  const matches = state.records.filter(r => (state.tier === 'all' || r.historical_tier === state.tier) &&
    [r.name,r.category,r.description,r.channel,r.id,r.review_status].join(' ').toLocaleLowerCase().includes(query));
  const pages = Math.max(1, Math.ceil(matches.length / size));
  state.page = Math.max(1, Math.min(state.page, pages));
  const body = $('rows'); body.replaceChildren();
  for (const r of matches.slice((state.page - 1) * size, state.page * size)) {
    const tr = document.createElement('tr'); tr.className = 'tier-' + r.historical_tier;
    const name = document.createElement('td');
    const project = textElement(r.project_url ? 'a' : 'span', r.name, 'project');
    if (r.project_url) { project.href = r.project_url; project.target = '_blank'; project.rel = 'noopener noreferrer'; }
    name.append(project, textElement('span',r.category,'category'));
    const tier = document.createElement('td'); tier.append(textElement('span','● ' + r.historical_tier,'badge tier-' + r.historical_tier));
    const channel = textElement('td',r.channel);
    const review = document.createElement('td'); review.append(textElement('span',r.review_status,'review-status'));
    const finding = document.createElement('td');
    const link = textElement('a','Read finding →','finding-link'); link.href = 'records/' + r.id + '.html'; link.setAttribute('aria-label','Read finding for ' + r.name);
    finding.append(link); tr.append(name,tier,channel,review,finding); body.append(tr);
  }
  $('count').textContent = matches.length.toLocaleString() + ' matching · ' + state.records.length.toLocaleString() + ' total';
  $('page').textContent = 'Page ' + state.page + ' of ' + pages;
  $('prev').disabled = state.page === 1; $('next').disabled = state.page === pages;
  $('empty').hidden = matches.length !== 0;
  document.querySelectorAll('[data-tier]').forEach(b => { const selected = b.dataset.tier === state.tier; b.setAttribute('aria-pressed',String(selected)); if (b.classList.contains('chip')) b.classList.toggle('selected',selected); });
  const params = new URLSearchParams();
  if(state.tier !== 'all') params.set('tier',state.tier);
  if(state.query) params.set('q',state.query);
  if(state.page > 1) params.set('page',String(state.page));
  history.replaceState(null,'',location.pathname + (params.size ? '?' + params : ''));
}
document.querySelectorAll('[data-tier]').forEach(b => b.addEventListener('click',() => {state.tier=b.dataset.tier;state.page=1;render();}));
$('search').addEventListener('input',e => {state.query=e.target.value;state.page=1;render();});
$('prev').addEventListener('click',() => {state.page--;render();});
$('next').addEventListener('click',() => {state.page++;render();});
$('reset').addEventListener('click',() => {state.query='';state.tier='all';state.page=1;$('search').value='';render();});
fetch('catalog.json').then(r => {if(!r.ok) throw new Error('Catalog unavailable');return r.json();}).then(records => {
  state.records=records; const params=new URLSearchParams(location.search);
  const tier=params.get('tier');if(['A','B','C','D','N'].includes(tier))state.tier=tier;
  state.query=params.get('q')||'';state.page=Math.max(1,parseInt(params.get('page'),10)||1);
  $('search').value=state.query;render();
}).catch(() => {$('count').textContent='The catalog could not be loaded. Reload this page or use the project directory.'; const a=textElement('a','Browse all records');a.href='directory.html';$('rows').closest('.table-wrap').after(a);});
