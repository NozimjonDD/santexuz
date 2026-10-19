# UI va kod optimallashtirishi — 19.10.2026

Mavjud o‘zbekcha, statik CRM va uning biznes qoidalari asosida bajarilgan o‘zgarishlar.

## Interfeys

- Mayda matnlar o‘rniga 12/13/14 px tipografiya shkalasi, bir xil 44 px boshqaruvlar va kattaroq mobil inputlar ishlatiladi.
- Jadval, filtr, sana tanlash, modal va sahifa amallari ekran kengligiga mos joylashadi. Jadvalning sahifalash tugmalari bitta guruhda qoladi.
- Global qidiruv `Ctrl/Command + K`, yuqori/pastga tugmalari va Escape bilan ishlaydi; mobil qidiruv oynasi inputga fokus beradi.
- Lazy sahifa yuklanayotganda yon menyu va toolbar saqlanadi; yuklanish faqat kontent ichida ko‘rsatiladi.
- Ko‘p xizmat yo‘nalishini tanlash oddiy checkboxlar bilan bajariladi. Ctrl bosib turish kerak emas.
- Materiallarda keraksiz Telegram filtri, katalog profillarida esa aloqasiz bo‘sh tablar olib tashlandi.
- Dashboard holat kartalari ochadigan filtrlar ko‘rsatilgan sonlarga mos. Grafik bo‘sh kunlarni ko‘rsatadi, sana labeli oyga mahkamlanmagan, uzoq davr 31 tagacha nuqtaga guruhlanadi.
- Grafik kenglikka mos koordinatalar va label sonini tanlaydi. Y o‘qida takrorlanadigan kasrsiz qiymatlar ko‘rsatilmaydi.

## Kod

- `shared/ui.tsx` barqaror eksport qatlami bo‘lib qoldi. Kichik UI komponentlari, modal, forma va jadval alohida modullarda.
- Forma validatsiyasi mustaqil funksiyaga ajratildi. Raqam tekshiruvidan keyin maxsus biznes validatsiyasi ham ishlaydi.
- Jadval qidirish/saralashi memoize qilindi; bir xil IDli yangi massiv kelishi tanlangan sahifani bekor qilmaydi.
- Bildirishnomalar ma’lumot kontekstidan ajratildi. Toast ochish/yopish butun CRMga yangi kontekst qiymatini yubormaydi; timerlar yopilganda tozalanadi.
- `Intl` formatlagichlar har katak uchun qayta yaratilmaydi. Lokal HTTP namoyishida `randomUUID` yo‘q bo‘lsa demo ID fallback ishlaydi.
- Katalog list/profil/editor/model qatlamlariga ajratildi. Takroriy buyurtma, baho, to‘lov va hamkor qidiruvlari indekslar orqali olinadi.
- Dashboard hisoblari bitta modelda; moliyaviy hisoblashga faqat tegishli buyurtma to‘lovlari beriladi. Ogohlantirishlar muhimligiga ko‘ra saralanadi va daqiqada yangilanadi.
- Mavjud smeta/shartnoma snapshotlari, moliyaviy tasdiqlash va nizo bloklari saqlangan. Dependencylar qo‘shilmagan.

## Tekshiruv chegarasi

Bu kompyuterda faqat fayllar o‘qildi va tahrirlandi. Test, typecheck, build, formatter, server yoki brauzer tekshiruvi ishga tushirilmadi. Tezlik o‘lchanmagan va vizual natija brauzerda tasdiqlanmagan.

Validatsiya, dashboard hisoblari, katalog ma’lumotlari va ID fallback uchun testlar; sahifalash/toast, klaviatura qidiruvi va checkbox tanlovi uchun brauzer ssenariylari yozildi.

**Boshqa kompyuterda**, dependencylar o‘rnatilgan loyiha papkasida:

```bash
npm run check && npm run test:e2e
```

Playwright brauzerlari avval o‘rnatilgan bo‘lishi kerak. So‘ng 390 px, 768 px va 1440 px kengliklarda jadval, grafik va modal ko‘rinishini ko‘ring.
