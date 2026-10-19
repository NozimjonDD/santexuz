/* Verification machine only: node --test scripts/miniapp_session.test.mjs */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const source=await readFile(new URL('../static/miniapp/automatic-session.js',import.meta.url),'utf8');
const {createAutomaticSession}=await import(`data:text/javascript;charset=utf-8,${encodeURIComponent(source)}`);
const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return {promise,resolve,reject};};

test('parallel protected actions share one silent authentication and apply one identity',async()=>{
 let authenticated=false,calls=0;const applied=[],response=deferred();
 const session=createAutomaticSession({hasSession:()=>authenticated,canAuthenticate:()=>true,
  authenticate:()=>{calls++;return response.promise;},onAuthenticated:user=>{authenticated=true;applied.push(user);}});
 const first=session.ensure(),second=session.ensure();await Promise.resolve();
 assert.equal(calls,1);response.resolve({id:7});
 assert.deepEqual(await Promise.all([first,second]),[true,true]);assert.deepEqual(applied,[{id:7}]);
 assert.equal(await session.ensure(),true);assert.equal(calls,1);
});

test('public browsing never invents an identity when no trusted authentication context exists',async()=>{
 let available=false,calls=0;
 const session=createAutomaticSession({hasSession:()=>false,canAuthenticate:()=>available,
  authenticate:async()=>{calls++;return {id:3};},onAuthenticated:()=>{}});
 assert.equal(await session.ensure(),false);assert.equal(calls,0);
 available=true;assert.equal(await session.ensure(),true);assert.equal(calls,1);
});

test('a failed bootstrap does not loop on every render; an explicit refresh can retry',async()=>{
 let calls=0;
 const session=createAutomaticSession({hasSession:()=>false,canAuthenticate:()=>true,
  authenticate:async()=>{if(++calls===1)throw new Error('unavailable');return {id:2};},onAuthenticated:()=>{}});
 assert.equal(await session.ensure(),false);assert.equal(await session.ensure(),false);assert.equal(calls,1);
 assert.equal(await session.ensure({retry:true}),true);assert.equal(calls,2);
});

test('logout or design preview prevents an earlier response from restoring the old identity',async()=>{
 const response=deferred(),applied=[];let calls=0;
 const session=createAutomaticSession({hasSession:()=>false,canAuthenticate:()=>true,
  authenticate:()=>++calls===1?response.promise:Promise.resolve({id:'new'}),onAuthenticated:user=>applied.push(user)});
 const previous=session.ensure();await Promise.resolve();session.reset();
 assert.equal(await session.ensure(),true);response.resolve({id:'old'});
 assert.equal(await previous,false);assert.deepEqual(applied,[{id:'new'}]);
});

test('a late failure from a discarded bootstrap cannot poison a newer attempt',async()=>{
 const response=deferred();let calls=0;
 const session=createAutomaticSession({hasSession:()=>false,canAuthenticate:()=>true,
  authenticate:()=>++calls===1?response.promise:Promise.resolve({id:'new'}),onAuthenticated:()=>{}});
 const previous=session.ensure();await Promise.resolve();session.reset();
 assert.equal(await session.ensure(),true);response.reject(new Error('old failure'));
 assert.equal(await previous,false);assert.equal(await session.ensure(),true);assert.equal(calls,3);
});
