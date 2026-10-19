/* Run on the verification machine: node --test scripts/miniapp_api.test.mjs */
import test, {beforeEach, afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';

const source=await readFile(new URL('../static/miniapp/api.js',import.meta.url),'utf8');
const {Api,ApiError}=await import(`data:text/javascript;charset=utf-8,${encodeURIComponent(source)}`);
const originalFetch=globalThis.fetch;
const originalDocument=globalThis.document;
const originalLocation=globalThis.location;
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}});
test('every frontend module parses without a bundler',async()=>{
 for(const name of ['api','app','demo','i18n','ui','visuals']){
  const source=await readFile(new URL(`../static/miniapp/${name}.js`,import.meta.url),'utf8');
  const result=spawnSync(process.execPath,['--input-type=module','--check'],{input:source,encoding:'utf8'});
  assert.equal(result.status,0,`${name}.js: ${result.stderr}`);
 }
});
beforeEach(()=>{
 globalThis.location={origin:'http://localhost:8000'};
 globalThis.document={querySelector:()=>({value:'masked-csrf-token'})};
});
afterEach(()=>{globalThis.fetch=originalFetch;globalThis.document=originalDocument;globalThis.location=originalLocation;});

test('concurrent unauthorized requests share a single rotating refresh token',async()=>{
 const api=new Api();api.setSession({access:'expired',refresh:'refresh-1'});
 let renewals=0;let successful=0;
 globalThis.fetch=async(url,options)=>{
  if(url.pathname.endsWith('/refresh/')){renewals++;assert.deepEqual(JSON.parse(options.body),{refresh:'refresh-1'});assert.equal(options.headers.Authorization,undefined);return json({access:'valid',refresh:'refresh-2'});}
  if(options.headers.Authorization==='Bearer expired')return json({detail:'Expired'},401);
  assert.equal(options.headers.Authorization,'Bearer valid');successful++;return json({id:successful});
 };
 const results=await Promise.all([api.request('auth/me/'),api.request('site/orders/'),api.request('auth/notifications/')]);
 assert.equal(renewals,1);assert.equal(successful,3);assert.equal(results.length,3);
});

test('a delayed old-token 401 retries the newer access token without rotating twice',async()=>{
 const api=new Api();api.setSession({access:'expired',refresh:'refresh-1'});
 let release;const delayed=new Promise(resolve=>{release=resolve;});let renewals=0;
 globalThis.fetch=async(url,options)=>{
  if(url.pathname.endsWith('/refresh/')){renewals++;return json({access:'valid',refresh:'refresh-2'});}
  if(options.headers.Authorization==='Bearer expired'){
   if(url.pathname.includes('notifications'))await delayed;
   return json({},401);
  }
  return json({ok:true});
 };
 const late=api.request('auth/notifications/');await api.request('auth/me/');release();await late;
 assert.equal(renewals,1);
});

test('empty service center and 204 responses are accepted, empty required JSON is rejected',async()=>{
 const api=new Api();
 globalThis.fetch=async()=>new Response(null,{status:200});
 assert.equal(await api.request('common/service-center/'),null);
 await assert.rejects(api.request('site/orders/'),error=>error instanceof ApiError&&error.message==='invalidResponse');
 globalThis.fetch=async()=>new Response(null,{status:204});
 assert.equal(await api.request('auth/logout/',{method:'POST',data:{}}),null);
});

test('refresh rejection clears the session and never retries a mutation anonymously',async()=>{
 const api=new Api();api.setSession({access:'expired',refresh:'bad'});let calls=0;
 globalThis.fetch=async()=>{calls++;return json({detail:'Invalid token'},401);};
 await assert.rejects(api.request('site/orders/1/payments/',{method:'POST',data:{amount:'1'}}));
 assert.equal(calls,2);assert.equal(api.authenticated,false);
});

test('server validation fields and multipart payloads survive the client boundary',async()=>{
 const api=new Api();const form=new FormData();form.append('purpose','issue');
 globalThis.fetch=async(url,options)=>{assert.equal(options.body,form);assert.equal(options.headers['Content-Type'],undefined);assert.equal(options.headers['X-CSRFToken'],'masked-csrf-token');return json({file:['Invalid format']},400);};
 await assert.rejects(api.request('site/orders/1/attachments/',{method:'POST',data:form}),error=>error.status===400&&error.message==='file: Invalid format');
});

test('pagination keeps all catalog pages and rejects paths outside the API boundary',async()=>{
 const api=new Api();let calls=0;
 globalThis.fetch=async url=>{calls++;return url.search?json({results:[{id:2}],next:null}):json({results:[{id:1}],next:'http://localhost:8000/api/v1/common/services/?page=2'});};
 assert.deepEqual(await api.all('common/services/'),[{id:1},{id:2}]);assert.equal(calls,2);
 await assert.rejects(api.request('/api/v1/../../admin/'),/Invalid API URL/);
});

test('a caller abort propagates instead of being presented as a server error',async()=>{
 const api=new Api();const controller=new AbortController();controller.abort();
 globalThis.fetch=async(url,options)=>{options.signal.throwIfAborted();};
 await assert.rejects(api.request('site/orders/',{signal:controller.signal}),error=>error.name==='AbortError');
});

test('an old renewal cannot restore a cleared session or overwrite a new login',async()=>{
 const api=new Api();api.setSession({access:'old',refresh:'old-refresh'});
 let release;let started;const waiting=new Promise(resolve=>{release=resolve;});const renewing=new Promise(resolve=>{started=resolve;});
 globalThis.fetch=async(url,options)=>{
  if(url.pathname.endsWith('/refresh/')){started();await waiting;return json({access:'stale',refresh:'stale-refresh'});}
  if(options.headers.Authorization==='Bearer old')return json({},401);
  assert.equal(options.headers.Authorization,'Bearer new');return json({id:2});
 };
 const previous=api.request('auth/me/');
 const rejected=assert.rejects(previous,error=>error.status===401);
 await renewing;api.clear();api.setSession({access:'new',refresh:'new-refresh'});release();await rejected;
 assert.equal(api.authenticated,true);assert.deepEqual(await api.request('auth/me/'),{id:2});
});
