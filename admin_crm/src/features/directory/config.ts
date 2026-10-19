import { categories, type EntityCollection } from '../../domain/types';
import type { DirectoryField } from './model';

const phone: DirectoryField = { name: 'phone', label: 'Telefon (+998)', type: 'tel', required: true, hint: 'Faqat sun’iy namuna raqam kiriting.' };
const active: DirectoryField = { name: 'isActive', label: 'Faol', type: 'checkbox' };
const telegram: DirectoryField = { name: 'telegramId', label: 'Telegram identifikatori', hint: 'Faqat demo bog‘lanish. Telegramda tekshirilmaydi.' };
const commission: DirectoryField = { name: 'commission', label: 'Individual komissiya (%)', type: 'number', min: 0, max: 100, hint: 'Bo‘sh bo‘lsa standart stavka. U ham yo‘q bo‘lsa — sozlanmagan.' };
const district: DirectoryField = { name: 'district', label: 'Hudud', type: 'select', required: true, options: ['Marhamat', 'Andijon shahri', 'Asaka'] };
export interface DirectoryConfig { title: string; description: string; singular: string; prefix: string; fields: DirectoryField[]; initial: Record<string, string | boolean | string[]> }
export const directoryConfig: Record<EntityCollection, DirectoryConfig> = {
  customers: { title: 'Mijozlar', description: 'Mijoz aloqalari, roziliklar va buyurtma tarixi.', singular: 'mijoz', prefix: 'C', initial: { consent: false }, fields: [
    { name: 'name', label: 'Ism-familiya', required: true }, phone, telegram, { name: 'notes', label: 'Admin izohi', type: 'textarea' },
    { name: 'consent', label: 'Namuna kontakt ma’lumotlarini qayta ishlashga rozilik qayd etildi', type: 'checkbox', required: true, full: true },
  ] },
  plumbers: { title: 'Santexniklar', description: 'Ustalar, xizmat yo‘nalishlari va ish yuklamasi.', singular: 'santexnik', prefix: 'P', initial: { isActive: true, district: 'Marhamat', categories: [], experience: '0' }, fields: [
    { name: 'name', label: 'Ism-familiya', required: true }, phone, telegram, { name: 'photo', label: 'Profil rasmi tavsifi', hint: 'Statik bosqichda faqat fayl nomi/tavsifi. Tashqi rasm yuklanmaydi.' },
    { name: 'experience', label: 'Tajriba (yil)', type: 'number', max: 70, required: true }, district,
    { name: 'categories', label: 'Xizmat yo‘nalishlari', type: 'multiselect', required: true, options: [...categories], hint: 'Bir nechta yo‘nalishni belgilang.' },
    commission, { name: 'notes', label: 'Ichki admin yozuvi', type: 'textarea' }, active,
  ] },
  shops: { title: 'Do‘konlar', description: 'Material hamkorlari va umumiy Telegram akkauntlari.', singular: 'do‘kon', prefix: 'SH', initial: { isActive: true, district: 'Marhamat' }, fields: [
    { name: 'name', label: 'Do‘kon nomi', required: true }, { name: 'contactName', label: 'Yuridik / aloqa nomi' }, { name: 'address', label: 'Manzil', required: true, full: true }, district, phone,
    { ...telegram, label: 'Umumiy Telegram akkaunt identifikatori' }, commission, { name: 'description', label: 'Tavsif', type: 'textarea' }, active,
  ] },
  services: { title: 'Xizmatlar katalogi', description: 'Marhamat tariflari, birliklar va kafolat shartlari.', singular: 'xizmat', prefix: 'S', initial: { isActive: true, visible: true, unit: 'dona' }, fields: [
    { name: 'name', label: 'Xizmat nomi (UZ)', required: true, full: true }, { name: 'nameRu', label: 'Ruscha tarjima' }, { name: 'nameEn', label: 'Inglizcha tarjima' },
    { name: 'category', label: 'Xizmat guruhi', type: 'select', required: true, options: [...categories] }, { name: 'unit', label: 'O‘lchov birligi', required: true, hint: 'dona, nuqta, holat, metr, m² yoki boshqa birlik' },
    { name: 'areaRate', label: 'Marhamat birlik tarifi (UZS)', type: 'number', min: 1, hint: 'Noma’lum bo‘lsa bo‘sh qoldiring. Nol tarif qabul qilinmaydi.' },
    { name: 'emergencyFee', label: 'Shoshilinch qo‘shimcha haq (UZS)', type: 'number', min: 0 }, { name: 'warranty', label: 'Kafolat muddati', hint: 'Masalan: 30 kun. Noma’lum bo‘lsa bo‘sh.' },
    { name: 'description', label: 'Tavsif', type: 'textarea' }, active, { name: 'visible', label: 'Mijoz katalogida ko‘rsatish', type: 'checkbox' },
  ] },
  materials: { title: 'Materiallar', description: 'Mahsulot nomenklaturasi. Narx buyurtma bo‘yicha do‘konda belgilanadi.', singular: 'material', prefix: 'M', initial: { isActive: true, unit: 'dona' }, fields: [
    { name: 'name', label: 'Mahsulot nomi', required: true, full: true }, { name: 'category', label: 'Guruh', type: 'select', required: true, options: ['Suv quvurlari', 'Quvur fitinglari', 'Berkitish va nazorat', 'Kran va jihozlar', 'Kanalizatsiya', 'Isitish', 'Sarf materiallari'] },
    { name: 'brand', label: 'Marka / model' }, { name: 'size', label: 'Diametr / o‘lcham' }, { name: 'unit', label: 'O‘lchov birligi', required: true }, { name: 'description', label: 'Tavsif', type: 'textarea' }, active,
  ] },
};
