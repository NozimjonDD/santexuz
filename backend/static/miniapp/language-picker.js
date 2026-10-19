/* A menu-button controller; language persistence belongs to the application. */
export function createLanguagePicker(root, {onSelect, onError = () => {}}) {
 const doc = root.ownerDocument;
 const trigger = root.querySelector('#language');
 const code = root.querySelector('#language-code');
 const popover = root.querySelector('#language-popover');
 const menu = root.querySelector('#language-menu');
 const title = root.querySelector('#language-menu-title');
 const items = [...menu.querySelectorAll('[role="menuitemradio"]')];
 let current = items.find(item => item.getAttribute('aria-checked') === 'true')?.dataset.language || 'uz';
 let busy = false;

 function focusItem(index) {
  const item = items[(index + items.length) % items.length];
  items.forEach(option => { option.tabIndex = option === item ? 0 : -1; });
  item.focus({preventScroll:true});
 }
 function close(restoreFocus = false) {
  popover.hidden = true;
  trigger.setAttribute('aria-expanded', 'false');
  items.forEach(item => { item.tabIndex = -1; });
  if (restoreFocus) trigger.focus({preventScroll:true});
 }
 function open(last = false) {
  if (busy) return;
  popover.hidden = false;
  trigger.setAttribute('aria-expanded', 'true');
  focusItem(last ? items.length - 1 : Math.max(0, items.findIndex(item => item.dataset.language === current)));
 }
 function update(language, labels) {
  const selected = items.find(item => item.dataset.language === language) || items[0];
  current = selected.dataset.language;
  code.textContent = current.toUpperCase();
  trigger.setAttribute('aria-label', `${labels.language}: ${selected.querySelector('.language-name').textContent}`);
  title.textContent = labels.chooseLanguage;
  items.forEach(item => { item.setAttribute('aria-checked', String(item === selected)); });
 }

 trigger.addEventListener('click', () => { if (popover.hidden) open(); else close(); });
 trigger.addEventListener('keydown', event => {
  if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
   event.preventDefault();
   open(event.key === 'ArrowUp');
  } else if (event.key === 'Escape' && !popover.hidden) {
   event.preventDefault();
   close(true);
  }
 });
 menu.addEventListener('keydown', event => {
  const index = items.indexOf(doc.activeElement);
  if (event.key === 'Escape') {
   event.preventDefault();
   close(true);
  } else if (event.key === 'Tab') {
   // Resume the normal tab order from the trigger; do not trap focus in the menu.
   close(true);
  } else if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
   event.preventDefault();
   focusItem(event.key === 'Home' ? 0 : event.key === 'End' ? items.length - 1 : index + (event.key === 'ArrowDown' ? 1 : -1));
  }
 });
 menu.addEventListener('click', async event => {
  const item = event.target.closest('[role="menuitemradio"]');
  if (!items.includes(item) || busy) return;
  event.preventDefault();
  close(true);
  if (item.dataset.language === current) return;
  busy = true;
  trigger.setAttribute('aria-busy', 'true');
  trigger.setAttribute('aria-disabled', 'true');
  try { await onSelect(item.dataset.language); }
  catch (error) { onError(error); }
  finally {
   busy = false;
   trigger.removeAttribute('aria-busy');
   trigger.removeAttribute('aria-disabled');
  }
 });
 doc.addEventListener('pointerdown', event => { if (!root.contains(event.target)) close(); });
 root.addEventListener('focusout', event => { if (!popover.hidden && !root.contains(event.relatedTarget)) close(); });
 return {update, close};
}
