# Mini App UI: berilgan dizaynning implementatsiyasi

## Manba va holat

Foydalanuvchi bergan “Santexnika Mini App — Mobile screens by role.html” ichidagi 44 ekran va `TZ_docs.md` asosida yozildi. HTML fayl ichidagi sahifa arxivlari faqat matn/aktiv sifatida o‘qildi; ularning JavaScript kodi bajarilmadi va loyihaga olib kirilmadi. Dizaynning ko‘k palitrasi, Manrope shrifti, yumaloq kartalari, aniq smeta va pastki navigatsiyasi saqlandi. Shrift fayllari berilgan arxivdan mahalliy aktiv sifatida olindi; litsenziya `static/miniapp/fonts/OFL.txt` ichida.

UI yozilgan bosqichda dastur ishga tushirilmadi. Keyingi 2026-10-18 tekshiruvida foydalanuvchining aniq ko‘rsatmasi bilan backend tekshiruvlari bajarildi: 68 test o‘tdi, 2 ta PostgreSQL testi SQLite sabab o‘tkazib yuborildi. Frontend Node testlari, piksel mosligi va haqiqiy Telegram qurilmasi hali tekshirilmagan; tafsilot `verification.md` da. Berilgan PDF qayta generatsiya qilinmadi; dastur uchun Django HTML/CSS/JS yozildi.

## Fayllar

- `templates/8mobile/base-common.html`: metadata, Telegram SDK, mahalliy CSS va ES modul.
- `templates/8mobile/home.html`: semantik shell, til, navigatsiya, main, dialog va holat xabarlari.
- `static/miniapp/app.js`: ekran marshrutlari, rolga mos amallar, forma boshqaruvi.
- `static/miniapp/api.js`: xotiradagi JWT, yagona parallel refresh, timeout/abort, JSON/xato, multipart va sahifalash.
- `static/miniapp/ui.js`: escaped HTML, ikonka va umumiy komponentlar.
- `static/miniapp/i18n.js`: UZ/RU/EN matnlar, UZS, Asia/Tashkent sanalari.
- `static/miniapp/demo.js`: faqat lokal namoyish uchun xayoliy ma’lumotlar, bazaga yozmaydi.
- `static/miniapp/fonts.css` va `fonts/`: mahalliy Manrope; tashqi font/CDN talab qilinmaydi.

Framework, npm to‘plami yoki frontend build talab qilinmaydi. Productionda Django static fayllari odatiy `collectstatic`/web-server jarayoni bilan tarqatiladi. `.gitignore` ichida loyiha Mini App aktivlari va domen migratsiyalari uchun istisnolar qo‘shildi; generatsiya qilingan boshqa staticlar chiqarib tashlanadi.

## Ekranlar xaritasi

Bir xil jarayondagi ekranlar buyurtma tafsiloti va vazifaga mos dialoglarga birlashtirildi. Alohida chizilgan har bir ekran uchun takroriy template yaratilmaydi.

| Berilgan ekran | Implementatsiyadagi manzil yoki amal |
|---|---|
| Til tanlash | `#welcome`; sarlavhadagi UZ/RU/EN |
| Onboarding 1, 2, 3 | `#onboarding/1`, `/2`, `/3` |
| Telefon va hudud | `#profile`, kontakt ulashish, `#request` hudud/manzil |
| Mijoz asosiy | `#home`: xizmat qidirish, so‘rov, xizmat guruhlari, faol buyurtma, ustalar, markaz |
| Barcha xizmatlar | `#services`: hududiy narx, qidiruv, guruhlar |
| Ta’mirlash, o‘rnatish/almashtirish, quvur, isitish | `#services/{group_id}`; guruh katalogdan olinadi |
| Xizmat | Katalog kartasi: birlik stavkasi, kafolat va so‘rov amali |
| Yangi so‘rov | `#request`: tafsilot va tekshirish bosqichi, lokatsiya, media, rozilik |
| Buyurtmalarim | `#orders`, `#orders/active`, `#orders/history`; backend filtri sahifalashdan oldin |
| Buyurtma va usta | `#order/{id}`: haqiqiy holat, jadval, biriktirilgan ishtirokchilar |
| Smeta, smeta o‘zgardi | Shu buyurtmaning immutable Quote versiyasi; tasdiqlash/rad etish dialogi |
| Shartnoma va avans | Joriy va oldingi shartnomalar, private PDF, imzo, to‘lov yozuvlari |
| Yetkazish | Har bir qism tarkibi, status/ETA, mijozning qabul qilishi |
| Muammo xabari, nizo | Muammo formasi, ixtiyoriy media, nizo va admin qarori |
| Ish yakuni | Usta yakunlashi, mijoz qabul qilishi, alohida usta/do‘kon baholari |
| Bekor qilish | Sabab va qaytarish sharti bilan tasdiqlash dialogi |
| Yordam | `#help`: haqiqiy markaz manzili, telefon, ish vaqti, to‘lov va qaytarish izohi |
| Profil | `#profile`: ism/familiya/til; telefon serverda tasdiqlanadi |
| Bo‘sh holat, xato holati | Ro‘yxat/katalog bo‘shligi, API xatosi/qayta urinish, offline banner |
| Usta asosiy, so‘rovlar, so‘rov | Rolga mos `#home`, `#orders`, `#order/{id}`, qabul/rad |
| Ko‘rik va ish hajmi, materiallar | Ko‘rik, xizmat miqdorlari, katalog yoki erkin material qatorlari |
| Ish jarayoni, naqd/terminal qabul | Boshlash/yakunlash, media, idempotency kalitli to‘lov formasi |
| Ish jadvali | `#schedule` va buyurtmadagi jadvalni yangilash, sabab |
| Do‘kon asosiy, buyurtmalar, buyurtma | Rolga mos `#home`, `#orders`, `#order/{id}` |
| Rad etish sababi | Majburiy sabab bilan do‘kon javobi |
| Narx va mavjudlik | Material narxi/mavjudligi/muqobil/supply vaqti, tayyorlash va yetkazish haqi |
| Tayyorlash va yetkazish | Boshlash to‘siqlari, qisman yetkazish miqdorlari |
| Do‘kon yetkazish | `#deliveries`, har bir qismning ketma-ket holati va ETA |
| Usta/do‘kon profil | `#profile`; roli haqiqiy JWT akkauntidan olinadi |

## TZ qoidalari

- Narx ko‘rikdan oldin yakuniy deb ko‘rsatilmaydi. Katalog birlik stavkasi va immutable smeta alohida.
- Material, ish, yetkazish, shoshilinch haq va platforma haqi alohida ko‘rinadi. QQS alohida qo‘shilmaydi.
- Smeta tasdig‘ida aniq versiya yuboriladi. Qayta narxlashda mijoz qayta tasdiqlaydi.
- Imzo, avans, material qabul qilish va holat to‘siqlarini backend tekshiradi. Brauzerdagi rol yoki tugma huquq bermaydi.
- Naqd/terminal to‘lovi qayd etiladi; ichki tasdiq fiskal chek deb ko‘rsatilmaydi. Onlayn to‘lov yo‘q.
- Do‘kon telefoni chiqarilmaydi. Usta telefoni faqat API ruxsat bergan tayinlangan buyurtmada chiqadi.
- Lokatsiya brauzer ruxsati bilan olinadi yoki koordinata kiritiladi. Interaktiv xaritada nuqta tanlash uchun mahsulotda xarita provayderini tanlash ochiq qolmoqda; soxta xarita qo‘shilmadi.
- Jonli kuryer xaritasi yoki material miqdorini avtomatik hisoblash qo‘shilmadi.
- Baho tekshiruvga yuborilgan deb ko‘rsatiladi; hali tekshirilmagan baho ommaviy reytingga kiritilmaydi.
- Admin ish oqimlari avvalgi alohida CRM/API doirasida qoladi.

## Adaptivlik va foydalanish

Mobil bir ustun; 650px dan katalog to‘rt ustun, buyurtma asosiy kontent va yon ustunga ajraladi. 320px da formalar bir ustunga tushadi. Ekran balandligi mahkamlanmagan, uzun matnlar o‘raladi. Pastki navigatsiya 4 yoki 5 bo‘lim, tugmalar kamida 44–48px, inputlar 16px. Dialog balandligi viewportga mos va o‘raladi. Klaviatura fokusi, skip-link, label/legend, aria-live, reduced-motion va offline/loading/error holatlari mavjud.

Telegramda safeAreaInset/contentSafeAreaInset va ularning hodisalari, themeChanged, BackButton ishlatiladi. Qorong‘i mavzuda sirt, matn va tugma kontrasti uchun alohida tokenlar bor. Rasmiy texnik manba: [Telegram Mini Apps](https://core.telegram.org/bots/webapps), Parallel Search orqali o‘qildi.

## Lokal ko‘rish

Faqat DEBUG + DEV_LOCAL_LOGIN + loopback host/ulanishda tepada ikki tugma bor:

- **Sinov akkaunti**: avvalgi CSRF himoyali development login. Faqat mijoz; yuborilgan so‘rov bazaga yoziladi.
- **Dizaynni ko‘rish**: namunaviy UI. Rolni Mijoz/Usta/Do‘kon qilib almashtirish mumkin. Doim ko‘rinadigan namoyish belgisi bor; hech bir yozish amali bajarilmaydi. Smeta va manzillar haqiqiy ma’lumot emas.

Production HTMLda bu tugmalar va rol tanlash yo‘q. Demo fixture fayli statik aktiv, hech qanday maxfiy ma’lumot yo‘q; u haqiqiy API huquqini bermaydi. Tokenlar localStorage/sessionStoragega yozilmaydi. Faqat til/onboarding afzalligi lokal saqlanadi.

## Reviewda birga tuzatilganlar

Moliyaviy eksport avval har buyurtmada alohida agregat/quote so‘rovlari va barcha qatorlarni xotiraga yig‘ardi. Endi annotatsiyalangan hisob + 200 qatorli prefetch, oqimli CSV va vaqtinchalik faylli write-only XLSX ishlatiladi. JSON shakli saqlandi. Audit eksportga ruxsat/so‘rov berilganini qayd etadi; mijoz yuklab bo‘lganini tasdiqlamaydi. Katta hisobotlar uchun CSV/XLSX ishlating: JSON hali barcha qatorlarni bitta javobga yig‘adi.

O‘chirilgan katalog obyektlarini staff serializer munosabatlari orqali qayta bog‘lash bloklandi; ommaviy usta profilida o‘chirilgan hudud/xizmatlar yashiriladi. Mavjud bo‘lmagan yoki o‘chirilgan akkaunt refreshi rad etiladi; fixture yuklashda Consumer signalining yozishi o‘tkazib yuboriladi.

## Boshqa kompyuterda

Tayyor Python virtual muhit, `.env`, test bazasi ruxsati va Node.js 22+ bilan backend papkasida:

```bash
bash scripts/verify.sh && node --test scripts/miniapp_api.test.mjs
```

Qo‘lda: development serverdagi Mini Appni 320/390/768/1280px kenglikda uch tilda va uch rolda ko‘ring; haqiqiy Telegramda telefon, klaviatura, safe area, qorong‘i mavzu, back button va to‘liq buyurtma oqimini tekshiring.
