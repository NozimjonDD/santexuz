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
- `static/miniapp/refresh.css`: minimal uslub, glass aksentlar, uzun matn va kichik ekran qoidalari.
- `static/miniapp/visuals.js`: xizmat ma’nosiga mos rasm/ikonka, hero fotosi, hamkorning o‘z surati yoki bosh harflari.
- `static/miniapp/images/`: mahalliy foto uslubidagi hero va to‘rt xizmat uchun umumiy atlas; [manba va promptlar](../static/miniapp/images/README.md).
- `scripts/prepare_miniapp_images.py`: boshqa kompyuterda yengil WebP nusxalarini yaratish; `apps/common/miniapp_assets.py` tayyor nusxa bo‘lmasa PNG tanlaydi.
- `static/miniapp/fonts.css` va `fonts/`: mahalliy Manrope; tashqi font/CDN talab qilinmaydi.

Framework, npm to‘plami yoki frontend build talab qilinmaydi. Productionda Django static fayllari odatiy `collectstatic`/web-server jarayoni bilan tarqatiladi. `.gitignore` ichida loyiha Mini App aktivlari va domen migratsiyalari uchun istisnolar qo‘shildi; generatsiya qilingan boshqa staticlar chiqarib tashlanadi.

## 2026-10-19: Glassmorphism + minimal UI

30–40% — vizual yo‘nalish ulushi: shaffof/xiralashgan header, qidiruv, hero matn paneli va pastki navigatsiya. Oddiy matn, smeta, moliya va formalar ko‘proq yopiq, toza fonda qoladi. Bu raqam matn opacity qiymati emas; barcha yozuvlar to‘liq xira. Glass fonlarning yengil shaffofligi, nozik chegaralar, yumshoq soyalar va lokal fotografiya ko‘k rangli mavjud brend bilan birlashtirildi. `backdrop-filter` bo‘lmagan webview’da yopiq fon chiqadi; reduced transparency/motion va forced-colors uchun alohida qoidalar bor.

| Avvalgi muammo | O‘zgarish |
| --- | --- |
| “O‘rnatish/almashtirish” karta chegarasidan chiqardi | Grid/flex elementlarida `min-inline-size:0`, sarlavhada normal wrap va `overflow-wrap:anywhere`; balandlik matnga mos, satrlarni kesish yo‘q |
| Xizmat rasmi/ikonkasi ro‘yxat indeksiga bog‘liq edi | `code` va uch tildagi nomdan semantik heating/installation/pipes/repair tanlanadi |
| Faqat piktogrammali bir xil xizmat kartalari | Foto atlas, alohida o‘qiladigan nom paneli va ikonka; bir atlas so‘rovi kartalar orasida bo‘lishiladi |
| Uzun narx/status/manzil bilan tor qatorlar | Moslashuvchan key-value grid, tugmalar wrap, tor ekranda bir ustun va uzun matn uchun o‘rash |
| Singan yoki bo‘sh hamkor rasmi | API rasmi asinxron/lazy yuklanadi; xatoda o‘z bosh harflari chiqadi |
| Profil bitta uzun karta va forma ko‘rinishida edi | Ism/rol/telefon holati, tahrirlash va yordam alohida; 850px dan ikki ustun, mobil ekranda bir ustun |
| Qorong‘i rejimda och ko‘k tugmalardagi oq belgilar | Brand ustidagi yozuvlar `--button-text` dan olinadi; yakunlangan timeline belgisi ham dark fonga mos |
| Katta shrift yoki tarjimada navigatsiya balandligi ortishi | Pastki bo‘shliq, sticky hisob va toast joyi navigatsiyaning haqiqiy balandligidan olinadi; `ResizeObserver` bilan yangilanadi |

Hero, xizmatlar va profil sahifasi yangilandi. Profilning asosiy amali — saqlash; tasdiqlanmagan telefon holatida mavjud kontakt ulashish va yangilash amallari bor. Ism/familiya/til API maydonlari saqlandi. Yangi matnlar UZ/RU/EN uchun qo‘shildi. Asosiy so‘rov tugmasi, shoshilinch chaqiruv, rol amallari va API shartnomasi saqlandi. Generatsiya qilingan usta tasviri faqat bezak: haqiqiy hamkor sifatida ko‘rsatilmaydi.

PNG manbalar ishlaydi. Mobil tarmoq uchun boshqa kompyuterda `python scripts/prepare_miniapp_images.py` mavjud Pillow bilan hero 960×640 va atlas 1024×1024 WebP nusxalarini tayyorlaydi; manbalar o‘zgartirilmaydi. Django developmentda mavjud nusxani, productionda `collectstatic` orqali tarqatishga tayyor nusxani tanlaydi. Hali tayyorlanmagan faylga havola chiqarilmaydi. Hajm tejalishi haqiqiy kodlashdan so‘ng buyruq natijasida ko‘rinadi; bu kompyuterda kodlash bajarilmadi.

`scripts/miniapp_visuals.test.mjs` xizmatni tartib/tilga bog‘lamaslik, uzun/zararli nomlarni xavfsiz chiqarish, haqiqiy avatar/bosh harf tanlash va aktivlar formati uchun testlarni beradi. Umumiy frontend parse tekshiruvi `visuals.js` ni ham qamraydi. Bu yangi testlar **bajarilmagan**. Bu bosqichda ilova, brauzer, build yoki dev server ishga tushirilmadi.

Boshqa kompyuterda tayyor Python muhiti va Node.js 22+ bilan:

```bash
python scripts/prepare_miniapp_images.py && python manage.py test apps.common.test_miniapp_assets --settings=project_backend.settings.test --noinput && node --test scripts/miniapp_api.test.mjs scripts/miniapp_visuals.test.mjs
```

Qo‘lda ko‘ring: 320/360/390/650/768/850/1280px, UZ/RU/EN, 200% matn, Telegram light/dark; kategoriya uzun nomlari, ism/manzil, katta pul summasi, status, profilni saqlash, forma/dialog va pastki navigatsiya. Glass qo‘llanmaydigan holat va rasm 404 bo‘lganda ham tekshiring. Productionda tasvir tayyorlash `collectstatic` dan oldin bajariladi. Source ko‘rigi ekrandagi natija tasdiqlangani degani emas.

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
