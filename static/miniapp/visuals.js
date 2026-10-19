/* Local photography is illustrative. Partner identities always come from the API. */
import {escape as e, icon} from './ui.js';
import {localized, t} from './i18n.js';

const heroImage = new URL('./images/plumbing-hero.png', import.meta.url).href;

export function serviceVisual(group = {}) {
 const value = [group?.code, group?.name, group?.name_ru, group?.name_en].filter(Boolean).join(' ').toLowerCase();
 // Use stable meaning, not list position: API ordering and languages may change.
 if (/heating|isitish|radiat|отоп|радиатор|boyler|boiler|qozon/.test(value)) return {scene:'heating',icon:'heat'};
 if (/pipe|drain|quvur|kanal|канал|труб|tiqilish|sifon|siphon/.test(value)) return {scene:'pipes',icon:'pipe'};
 if (/install|o[‘’ʻʼ']?rnat|almasht|установ|замен|sink|rakov|раков|dush|shower/.test(value)) return {scene:'installation',icon:'tap'};
 return {scene:'repair',icon:'tool'};
}

export function servicePhoto(group) {
 const {scene,icon: symbol} = serviceVisual(group);
 return `<span class="category-photo service-scene service-scene--${scene}" aria-hidden="true"><span class="category-icon">${icon(symbol)}</span></span>`;
}

export function serviceCategory(group) {
 return `<a class="category" href="#services/${Number(group.id)}">
  ${servicePhoto(group)}
  <span class="category-body"><span class="category-title">${e(localized(group))}</span><span class="category-arrow" aria-hidden="true">${icon('chevron')}</span></span>
 </a>`;
}

export function heroPhotography(source = heroImage) {
 return `<div class="hero-visual" aria-hidden="true">
  <img class="hero-photo" src="${e(source)}" width="1536" height="1024" alt="" decoding="async" fetchpriority="high" data-image-fallback>
  <span class="hero-photo-caption">${icon('tool')}<span>${e(t('freeInspection'))}</span></span>
 </div>`;
}

export function personAvatar(person) {
 const initials = String(person?.name || '').trim().split(/\s+/u).filter(Boolean).slice(0,2).map(part=>Array.from(part)[0]).join('').toLocaleUpperCase();
 return `<span class="avatar avatar-frame" aria-hidden="true"><span class="avatar-initials">${e(initials || 'S')}</span>${person?.photo?`<img class="avatar-photo" src="${e(person.photo)}" alt="" width="64" height="64" loading="lazy" decoding="async" referrerpolicy="no-referrer" data-image-fallback>`:''}</span>`;
}
