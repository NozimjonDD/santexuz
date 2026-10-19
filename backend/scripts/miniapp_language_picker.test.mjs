/* Verification machine only: node --test scripts/miniapp_language_picker.test.mjs */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const source=await readFile(new URL('../static/miniapp/language-picker.js',import.meta.url),'utf8');
const {createLanguagePicker}=await import(`data:text/javascript;charset=utf-8,${encodeURIComponent(source)}`);
const labels={language:'Til',chooseLanguage:'Qulay tilni tanlang'};
const flush=()=>new Promise(resolve=>setImmediate(resolve));

// Only model the controller's DOM boundary; native focus/tab order and layout
// still need verification in a real browser on the other machine.
class Element extends EventTarget {
 constructor(doc,parent=null){super();this.ownerDocument=doc;this.parent=parent;this.attributes=new Map();this.dataset={};this.nodes={};this.tabIndex=-1;}
 setAttribute(name,value){this.attributes.set(name,String(value));}
 getAttribute(name){return this.attributes.get(name) ?? null;}
 removeAttribute(name){this.attributes.delete(name);}
 querySelector(selector){return this.nodes[selector];}
 querySelectorAll(){return this.items;}
 contains(node){for(let item=node;item;item=item.parent)if(item===this)return true;return false;}
 closest(){for(let item=this;item;item=item.parent)if(item.getAttribute?.('role')==='menuitemradio')return item;return null;}
 focus(){this.ownerDocument.activeElement=this;}
}
function event(node,type,properties={}){
 const value=new Event(type,{cancelable:true});
 for(const [name,entry] of Object.entries(properties))Object.defineProperty(value,name,{value:entry});
 node.dispatchEvent(value);return value;
}
function fixture(onSelect=()=>{},onError=()=>{}){
 const doc=new EventTarget(),root=new Element(doc);
 const trigger=new Element(doc,root),code=new Element(doc,trigger),popover=new Element(doc,root);
 const menu=new Element(doc,popover),title=new Element(doc,popover);
 root.nodes={'#language':trigger,'#language-code':code,'#language-popover':popover,'#language-menu':menu,'#language-menu-title':title};
 popover.hidden=true;
 const items=[['uz','O‘zbekcha'],['ru','Русский'],['en','English']].map(([language,name])=>{
  const item=new Element(doc,menu),text=new Element(doc,item);
  item.dataset.language=language;item.setAttribute('role','menuitemradio');item.setAttribute('aria-checked',String(language==='uz'));
  text.textContent=name;item.nodes['.language-name']=text;return item;
 });
 menu.items=items;
 const picker=createLanguagePicker(root,{onSelect,onError});
 picker.update('uz',labels);trigger.focus();
 return {doc,root,trigger,code,popover,menu,title,items,picker};
}

test('selected language is announced, opening focuses it, arrow keys wrap and Escape restores focus',()=>{
 const f=fixture();f.picker.update('ru',{language:'Язык',chooseLanguage:'Выберите удобный язык'});
 assert.equal(f.code.textContent,'RU');assert.equal(f.trigger.getAttribute('aria-label'),'Язык: Русский');
 assert.equal(f.items[1].getAttribute('aria-checked'),'true');assert.equal(f.items[0].getAttribute('aria-checked'),'false');
 event(f.trigger,'keydown',{key:'ArrowDown'});
 assert.equal(f.popover.hidden,false);assert.equal(f.doc.activeElement,f.items[1]);
 event(f.menu,'keydown',{key:'End'});assert.equal(f.doc.activeElement,f.items[2]);
 event(f.menu,'keydown',{key:'ArrowDown'});assert.equal(f.doc.activeElement,f.items[0]);
 event(f.menu,'keydown',{key:'ArrowUp'});assert.equal(f.doc.activeElement,f.items[2]);
 event(f.menu,'keydown',{key:'Home'});assert.equal(f.doc.activeElement,f.items[0]);
 event(f.menu,'keydown',{key:'Escape'});
 assert.equal(f.trigger.getAttribute('aria-expanded'),'false');assert.equal(f.popover.hidden,true);
 assert.equal(f.doc.activeElement,f.trigger);assert.ok(f.items.every(item=>item.tabIndex===-1));
});

test('trigger click can close an open menu; Tab, outside pointer and outside focus dismiss it',()=>{
 const f=fixture();event(f.trigger,'click');
 event(f.root,'focusout',{relatedTarget:f.trigger});event(f.trigger,'click');
 assert.equal(f.popover.hidden,true);
 event(f.trigger,'click');
 const tab=event(f.menu,'keydown',{key:'Tab'});
 assert.equal(tab.defaultPrevented,false);assert.equal(f.popover.hidden,true);
 event(f.trigger,'click');
 const outside=new Element(f.doc);event(f.doc,'pointerdown',{target:outside});
 assert.equal(f.popover.hidden,true);
 event(f.trigger,'click');event(f.root,'focusout',{relatedTarget:outside});
 assert.equal(f.popover.hidden,true);
});

test('current choice makes no request; a new choice is submitted once and busy state blocks reopening',async()=>{
 let release,calls=0;
 const pending=new Promise(resolve=>{release=resolve;});
 const f=fixture(language=>{calls++;f.picker.update(language,labels);return pending;});
 event(f.trigger,'click');event(f.menu,'click',{target:f.items[0]});await flush();
 assert.equal(calls,0);assert.equal(f.popover.hidden,true);
 event(f.trigger,'click');event(f.menu,'click',{target:f.items[2].nodes['.language-name']});
 assert.equal(calls,1);assert.equal(f.code.textContent,'EN');assert.equal(f.doc.activeElement,f.trigger);
 assert.equal(f.trigger.getAttribute('aria-busy'),'true');assert.equal(f.trigger.getAttribute('aria-disabled'),'true');
 event(f.trigger,'click');event(f.menu,'click',{target:f.items[1]});
 assert.equal(f.popover.hidden,true);assert.equal(calls,1);
 release();await flush();
 assert.equal(f.trigger.getAttribute('aria-busy'),null);assert.equal(f.trigger.getAttribute('aria-disabled'),null);
 event(f.trigger,'click');assert.equal(f.doc.activeElement,f.items[2]);
});

test('a failed language callback reports the error and always unlocks the control',async()=>{
 const errors=[],failure=new Error('save failed');
 const f=fixture(async()=>{throw failure;},error=>errors.push(error));
 event(f.trigger,'click');event(f.menu,'click',{target:f.items[1]});await flush();
 assert.deepEqual(errors,[failure]);assert.equal(f.trigger.getAttribute('aria-disabled'),null);
 event(f.trigger,'click');assert.equal(f.popover.hidden,false);
});
