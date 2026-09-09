// Exercise the actual browser script with a small DOM adapter; no dependencies.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
class Element {
  constructor(tag='div') {this.tagName=tag;this.children=[];this.events={};this.dataset={};this.className='';this.textContent='';this.value='';this.classList={contains:c=>this.className.split(' ').includes(c),toggle:()=>{}};}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  setAttribute(k,v){this[k]=v;}
  addEventListener(k,fn){this.events[k]=fn;}
  closest(){return this;}
  after(){}
}
const ids={};for(const id of ['rows','count','page','prev','next','empty','reset','search'])ids[id]=new Element();
const filters=['all','D','C','B','A','N'].map(t=>{const e=new Element('button');e.dataset.tier=t;e.className='chip';return e;});
const data=JSON.parse(fs.readFileSync(__dirname+'/dist/catalog.json','utf8'));
const context={document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag),querySelectorAll:()=>filters},history:{replaceState(){}},location:{search:'',pathname:'/study/'},URLSearchParams,fetch:async()=>({ok:true,json:async()=>data})};
vm.runInNewContext(fs.readFileSync(__dirname+'/app.js','utf8'),context);
setImmediate(()=>{
  assert.equal(ids.rows.children.length,50);
  assert.match(ids.count.textContent,/3,006/);
  filters.find(e=>e.dataset.tier==='D').events.click();
  assert.equal(ids.rows.children.length,49);
  assert(ids.rows.children.every(r=>r.className==='tier-D'));
  filters[0].events.click();
  ids.search.events.input({target:{value:'retroarch'}});
  assert.equal(ids.rows.children.length,1);
  assert.equal(ids.rows.children[0].children[0].children[0].textContent,'RetroArch');
  assert.equal(ids.rows.children[0].children[4].children[0].href,'records/R0001.html');
  ids.search.events.input({target:{value:'<script>no such project</script>'}});
  assert.equal(ids.rows.children.length,0);assert.equal(ids.empty.hidden,false);
  ids.reset.events.click();assert.equal(ids.rows.children.length,50);
  ids.next.events.click();assert.equal(ids.page.textContent,'Page 2 of 61');
  ids.prev.events.click();assert.equal(ids.page.textContent,'Page 1 of 61');
  console.log('Search, tier filtering, detail links, pagination, and empty state passed.');
});
