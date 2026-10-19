/* Silent identity bootstrap. The server still validates every credential. */
export function createAutomaticSession({hasSession, canAuthenticate, authenticate, onAuthenticated}) {
 let pending = null, failure = null, generation = 0;
 async function ensure({retry = false} = {}) {
  if (hasSession()) return true;
  if (!canAuthenticate()) return false;
  if (retry) failure = null;
  if (failure) return false;
  if (!pending) {
   const attempt = {generation, promise:null};
   attempt.promise = Promise.resolve().then(authenticate).then(payload => {
    if (attempt.generation !== generation) return false;
    onAuthenticated(payload);
    return true;
   }).catch(error => {
    if (attempt.generation === generation) failure = error;
    return false;
   }).finally(() => { if (pending === attempt) pending = null; });
   pending = attempt;
  }
  return pending.promise;
 }
 return {
  ensure,
  reset() { generation++; pending = null; failure = null; },
 };
}
