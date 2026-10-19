/* Verification machine only: node --test scripts/miniapp_visuals.test.mjs */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

// Match the existing bundler-free tests; resolve nested modules without a package install.
const folder=new URL('../static/miniapp/',import.meta.url);
const moduleURL=source=>`data:text/javascript;charset=utf-8,${encodeURIComponent(source)}`;
const translations=moduleURL(await readFile(new URL('i18n.js',folder),'utf8'));
const ui=moduleURL((await readFile(new URL('ui.js',folder),'utf8')).replace("from './i18n.js'",`from ${JSON.stringify(translations)}`));
const source=(await readFile(new URL('visuals.js',folder),'utf8'))
 .replace("from './ui.js'",`from ${JSON.stringify(ui)}`)
 .replace("from './i18n.js'",`from ${JSON.stringify(translations)}`)
 .replace('import.meta.url',JSON.stringify(new URL('visuals.js',folder).href));
const {serviceVisual,serviceCategory,personAvatar,heroPhotography}=await import(moduleURL(source));

test('service photos follow meaning when translated groups arrive in different orders',()=>{
 const groups=[
  {id:4,code:'heating',name:'Isitish tizimi'},
  {id:2,name:'O‘rnatish/almashtirish',name_ru:'Установка / замена'},
  {id:3,code:'pipes-drainage',name_ru:'Трубы и канализация'},
  {id:1,code:'repair',name:'Ta’mirlash'},
 ];
 const expected=new Map([[4,'heating'],[2,'installation'],[3,'pipes'],[1,'repair']]);
 for(const group of [...groups,...groups.toReversed()])assert.equal(serviceVisual(group).scene,expected.get(group.id));
 assert.equal(serviceVisual({name:'Радиаторы и отопление'}).icon,'heat');
 assert.equal(serviceVisual(null).scene,'repair');
});

test('long catalog names are preserved and untrusted text cannot become card markup',()=>{
 const name='O‘rnatish/almashtirish — '+ 'uzun_nom_'.repeat(25) + '<img src=x onerror="alert(1)">';
 const html=serviceCategory({id:12,name});
 assert.ok(html.includes('href="#services/12"'));
 assert.ok(html.includes('uzun_nom_'.repeat(25)));
 assert.ok(html.includes('&lt;img src=x onerror=&quot;alert(1)&quot;&gt;'));
 assert.ok(!html.includes('<img src=x'));
 assert.ok(!html.includes('style='));
});

test('partner fallback uses their own initials and photo attributes remain escaped',()=>{
 const initial=personAvatar({name:'Azizbek Karimov'});
 assert.ok(initial.includes('>AK</span>'));
 assert.ok(!initial.includes('<img'));
 const actual=personAvatar({name:'Ali Valiyev',photo:'/private-photo/1/?label="portrait"&size=64'});
 assert.ok(actual.includes('src="/private-photo/1/?label=&quot;portrait&quot;&amp;size=64"'));
 assert.ok(actual.includes('loading="lazy"'));
 assert.ok(actual.includes('data-image-fallback'));
 assert.ok(!actual.includes('onerror='));
 assert.ok(!initial.includes('plumbing-hero'));
});

test('local photo assets are valid PNGs and the atlas divides into equal square quadrants',async()=>{
 for(const name of ['plumbing-hero.png','service-scenes.png']){
  const data=await readFile(new URL(`images/${name}`,folder));
  assert.deepEqual(data.subarray(0,8),Buffer.from([137,80,78,71,13,10,26,10]));
  const width=data.readUInt32BE(16),height=data.readUInt32BE(20);
  assert.ok(width>=1024&&height>=1024);
  if(name==='service-scenes.png'){assert.equal(width,height);assert.equal(width%2,0);}
 }
 const html=heroPhotography();
 assert.ok(html.includes('images/plumbing-hero.png'));
 assert.ok(html.includes('fetchpriority="high"'));
 assert.ok(!html.includes('https://images.'));
 const selected=heroPhotography('/asset-prefix/miniapp/images/plumbing-hero.webp?label="hero"&v=2');
 assert.ok(selected.includes('src="/asset-prefix/miniapp/images/plumbing-hero.webp?label=&quot;hero&quot;&amp;v=2"'));
 assert.ok(!selected.includes('images/plumbing-hero.png'));
});
