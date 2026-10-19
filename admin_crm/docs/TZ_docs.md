# Santexnika xizmatlari uchun Telegram Mini App
## Texnik topshiriq (TZ)

**Hujjat holati:** DRAFT — asosiy mahsulot oqimlari kelishilgan; tariflar, katalog tafsilotlari va ayrim huquqiy ma’lumotlar keyin to‘ldiriladi  
**Pilot hudud:** Andijon viloyati, Marhamat tumani  
**Valyuta:** O‘zbekiston so‘mi (UZS)  
**MVP platformalari:** Telegram Mini App va alohida web-admin panel

## 1. Hujjat maqsadi

Ushbu hujjat mijoz, santexnik, santexnika do‘koni va xizmat markazi o‘rtasidagi buyurtma jarayoniga qo‘yiladigan dastlabki biznes va funksional talablarni belgilaydi. Hujjat mavjud g‘oya va foydalanuvchi bilan tasdiqlangan qarorlar asosida tuzilgan. Noma’lum tariflar yoki texnik provayderlar taxmin bilan belgilanmaydi; ular “Ochiq masalalar” bo‘limida qayd etiladi.

`ideas.md` dagi dastlabki g‘oya mahsulotning kelib chiqish manbai hisoblanadi. `smartservices.uz` faqat foydalanuvchi tajribasi uchun kuzatilgan namuna sifatida ishlatildi: hudud tanlash, xizmat/buyurtma sahifalari, profil, tillar, yordam va to‘lov ma’lumotlarini ko‘rsatish. Saytning kodi yoki dizayni ko‘chirilmaydi, ichki ishlashi haqida ko‘rinmagan taxminlar qilinmaydi.

## 2. Mahsulot maqsadi va doirasi

### 2.1. Maqsad

- Mijoz santexnika xizmati bo‘yicha so‘rovni Telegram ichidan yuboradi.
- Xizmat markazi so‘rovni mos santexnikka biriktiradi.
- Santexnik mijoz manzilida ish hajmini aniqlab, xizmat haqi va materiallar ro‘yxatini tuzadi.
- Do‘kon materiallarning mavjudligi, narxi, tayyorlash vaqti va yetkazish qiymatini tasdiqlaydi.
- Mijoz tasdiqlangan smeta, shartnoma, to‘lovlar, buyurtma holati va taxminiy vaqtni ko‘radi.
- Xizmat markazi to‘lovlar, komissiyalar, buyurtmalar va nizolarni boshqaradi.

### 2.2. MVP chegarasi

MVP avval faqat Andijon viloyatining Marhamat tumanida pilot qilinadi. Bitta jismoniy xizmat markazi faoliyat yuritadi. Mahsulot santexnika xizmatlariga qaratiladi.

Mijoz, santexnik va do‘kon Telegram Mini Appdan foydalanadi. Admin va xizmat markazi xodimlari alohida web-admin panelidan foydalanadi.

### 2.3. MVPga kirmaydi

- O‘lchovlardan material miqdorini avtomatik hisoblash.
- Kuryerning xaritadagi jonli joylashuvini ko‘rsatish.
- Mijozdan platforma haqi olish yoki ilova ichida onlayn to‘lov provayderini ulash.
- Santexnik cashback/bonuslari, brend reklamasi va pulli yuqori joylashtirish.
- Santexnikadan tashqari elektrchi, gaz ustasi va boshqa xizmatlarni ishga tushirish.
- Kafolat bo‘yicha alohida ilova ichidagi da’vo jarayoni.

## 3. Foydalanuvchilar va huquqlar

| Rol | Kirish va asosiy imkoniyatlar |
|---|---|
| Mijoz | Telegram identifikatori bilan Mini Appga kiradi; so‘rov yuboradi, smeta/shartnoma/to‘lov va statuslarni ko‘radi, material qabulini hamda ish yakunini tasdiqlaydi, baho/izoh qoldiradi. |
| Santexnik | Admin yaratgan Telegram akkaunt orqali kiradi; tayinlangan so‘rovni qabul qiladi/rad etadi, tashrif vaqtini va ish ma’lumotlarini kiritadi, material ro‘yxatini tuzadi, ish jadvali/statusini yangilaydi va ish yakunini belgilaydi. |
| Do‘kon | Har bir do‘konga bitta umumiy Telegram akkaunti biriktiriladi; buyurtmani qabul qiladi/rad etadi, material narxi/mavjudligini belgilaydi, tayyorlash vaqti/yetkazish narxini kiritadi va yetkazish statuslarini yangilaydi. |
| Xizmat markazi xodimi/admin | Alohida akkaunt bilan web-admin panelga kiradi. Xizmat markazi xodimlariga to‘liq admin huquqi beriladi; akkauntlar alohida bo‘lgani uchun amallar xodim kesimida qayd etiladi. |

**Ruxsatga oid kelishuv:** do‘kon xodimlari umumiy akkauntdan foydalangani sababli audit jurnalida amal faqat do‘kon akkauntiga bog‘lanadi, alohida xodim aniqlanmaydi. Xizmat markazi xodimlarining muhim amallari o‘zgartirib bo‘lmaydigan audit jurnalida saqlanadi.

Mijozga biriktirilgan santexnikning ismi, surati, tajribasi, xizmat yo‘nalishlari, tasdiqlangan reytingi va telefon raqami ko‘rsatiladi. Santexnikning telefon raqami faqat shu buyurtmaga biriktirilgan mijozga ochiladi. Do‘konning nomi, manzili va tasdiqlangan reytingi ko‘rsatiladi, telefon raqami yashiriladi; do‘kon bilan aloqa xizmat markazi orqali bo‘ladi.

## 4. Umumiy sozlamalar va biznes qoidalari

- Mini App interfeysi o‘zbek, rus va ingliz tillarida bo‘ladi. Foydalanuvchi birinchi kirishda til tanlaydi; xabarnomalar tanlangan tilga mos yuboriladi.
- Pul qiymatlari faqat UZSda yuritiladi. Kiritiladigan narxlar QQSni o‘z ichiga oladi; smetada QQS alohida qator bo‘lmaydi.
- Mijozdan alohida platforma haqi olinmaydi. Platforma daromadi do‘kon va santexnik komissiyalaridan olinadi.
- Xizmat haqi xizmat turi va miqdoriga qarab hisoblanadi: `miqdor × birlik stavkasi`. Stavkalar hudud va xizmat bo‘yicha admin tomonidan belgilanadi.
- Shoshilinch chaqiruv haqi oddiy ish haqiga qo‘shimcha alohida qat’iy summadir. Stavka hudud/xizmat bo‘yicha admin tomonidan sozlanadi.
- Narxlar yoki katalog yangilanishi faqat yangi smetalarga qo‘llanadi. Tasdiqlangan buyurtma narxi saqlanadi. Material tayyorlashdan oldin smetadagi har qanday o‘zgarish mijoz tomonidan qayta tasdiqlanishi kerak; shartnoma va avans farqi ham yangilanadi.
- Komissiya stavkasi do‘kon va santexnik uchun alohida, hamkor kesimida sozlanadi; admin standart stavka ham belgilashi mumkin. Do‘kon komissiyasi materiallar summasidan, santexnik komissiyasi xizmat haqidan hisoblanadi.
- Komissiya va hamkorlarga to‘lanadigan sof summa faqat admin panelida ko‘rinadi. Hamkorlarga yakuniy to‘lov summasi bildiriladi.

## 5. Xizmatlar va mahsulotlar katalogi

### 5.1. Xizmatlar katalogi

Mijoz hududini/manzilini ko‘rsatgach, shu hudud uchun xizmatlar va birlik narxlarini ko‘radi. Yakuniy smeta santexnik ko‘rigi va miqdorlarni kiritgach shakllanadi. Katalogni admin boshqaradi. Xizmat turi, o‘lchov birligi, hududiy tarif, shoshilinch tarif va kafolat muddati sozlanadi.

Quyidagi jadval faqat foydalanuvchi bilan ma’qullangan boshlang‘ich namuna; aniq xizmatlar, birliklar va narxlar keyin tasdiqlanadi.

| Guruh | Namunaviy xizmat | Birlik |
|---|---|---|
| Ta’mirlash | Kran/aralashtirgichni ta’mirlash | dona |
| Ta’mirlash | Suv sizib chiqishini bartaraf etish | nuqta |
| Ta’mirlash | Kanalizatsiya tiqilishini ochish | holat |
| O‘rnatish/almashtirish | Kran/aralashtirgich o‘rnatish | dona |
| O‘rnatish/almashtirish | Rakovina o‘rnatish | dona |
| O‘rnatish/almashtirish | Unitaz o‘rnatish | dona |
| O‘rnatish/almashtirish | Dush komplekti o‘rnatish | dona |
| O‘rnatish/almashtirish | Suv isitgich (boyler) o‘rnatish | dona |
| Quvur/kanalizatsiya | Suv quvurini yotqizish yoki almashtirish | metr |
| Quvur/kanalizatsiya | Kanalizatsiya quvurini yotqizish yoki almashtirish | metr |
| Isitish tizimi | Radiator o‘rnatish/almashtirish | dona |
| Isitish tizimi | Isitish quvurini o‘rnatish/almashtirish | metr |

### 5.2. Materiallar katalogi

MVPda material sarfi avtomatik hisoblanmaydi. Santexnik mahsulotni admin yuritadigan katalogdan qidiradi yoki nomi erkin kiritiladigan qator qo‘shadi. Erkin qator uchun nom, miqdor va o‘lchov birligi majburiy; marka/izoh ixtiyoriy. Do‘kon buyurtma bo‘yicha narx va mavjudlikni belgilaydi.

Quyidagi guruhlar katalog uchun namuna; diametr, marka, model va yakuniy nomenklatura foydalanuvchi/do‘kon bilan keyin tasdiqlanadi.

| Guruh | Namunaviy mahsulotlar | Aniqlashtiriladigan xususiyatlar |
|---|---|---|
| Suv quvurlari | PPR, metall-plastik yoki tasdiqlangan boshqa quvur | Material, diametr, uzunlik birligi, marka |
| Quvur fitinglari | Mufta, tirsak, troynik, o‘tish/adaptor | Diametr, rezba/o‘lcham, material, dona |
| Berkitish va nazorat | Sharli kran, qaytish klapani, filtr | Diametr, ulanish turi, marka, dona |
| Kran va jihozlar | Kran/aralashtirgich, dush komplekti, rakovina, sifon | Marka/model, komplekt tarkibi, dona yoki komplekt |
| Kanalizatsiya | Quvur, tirsak, troynik, manjet | Diametr, uzunlik/birlik, material |
| Isitish | Radiator, radiator krani, isitish quvuri, kronshteyn | O‘lcham/quvvat/diametr, material, dona/metr/komplekt |
| Sarf materiallari | FUM lenta, zichlagich, xomut, mahkamlash buyumlari | Qadoq/birlik va o‘lcham |

## 6. Asosiy foydalanuvchi oqimi

1. Mijoz bot orqali Mini Appni ochadi, tilni tanlaydi va Telegram identifikatori bilan kiradi.
2. Mijoz Telegram raqamini ulashadi, manzil matnini kiritadi va xaritada nuqta tanlaydi. Xizmat guruhini belgilaydi; muammo izohi hamda surat/video ixtiyoriy.
3. So‘rov yuborishdan oldin mijoz telefon, manzil va ilova qilingan media buyurtmada qatnashuvchilarga ko‘rsatilishiga aniq rozilik beradi. Ma’lumotlar faqat shu buyurtma doirasida ishlatiladi.
4. Mijoz shoshilinchlikni belgilashi mumkin. Xizmat markazi ish vaqtidagina shoshilinch so‘rov qabul qilinadi; admin shoshilinch belgini tasdiqlaydi. Shoshilinch tarif oddiy ish haqiga alohida qo‘shiladi.
5. Admin so‘rovni hudud va xizmat turiga mos santexniklar ro‘yxatidan qo‘lda tanlaydi. MVPda pilot hudud Marhamat tumani. Admin sozlaydigan santexnik javob muddati mavjud; muddat o‘tsa admin xabardor qilinadi, avtomatik qayta tayinlash bo‘lmaydi.
6. Santexnik so‘rovni qabul qiladi yoki rad etadi. Rad etilganda admin boshqa ustani tanlaydi. Mijozga santexnik qabul qilgandan keyingina Telegram xabari yuboriladi.
7. Santexnik mijoz bilan bevosita telefon orqali bog‘lanib, bepul ko‘rik vaqtini kelishadi. Santexnik vaqtni Mini Appga kiritadi; mijozning alohida tasdig‘i shart emas. Santexnik mijoz manziliga borib, ish hajmi/o‘lchovlarni mijoz bilan birga kiritadi.
8. Tizim birlik stavkalari asosida xizmat haqini hisoblaydi. Santexnik materiallar va miqdorlarni qo‘lda kiritadi. Mijoz smetani qabul qilmasa sababini ixtiyoriy yozadi; admin buyurtmani yopadi yoki boshqa ustaga qayta biriktiradi. O‘sha santexnik rad qilingan smetani tahrirlab qayta yubormaydi.
9. Materiallar ro‘yxati tayyor bo‘lgach, admin ro‘yxatdagi barcha do‘konlardan istalganini qo‘lda tanlab buyurtmani biriktiradi; do‘konlar ro‘yxati hudud bo‘yicha filtrlanmaydi. Har bir buyurtmani bitta do‘kon bajaradi.
10. Do‘kon buyurtmani qabul qiladi yoki rad etish sababini kiritadi. Rad etilsa admin boshqa do‘konga o‘tkazadi. Do‘kon uchun alohida javob muddati/avtomatik qayta yuborish yo‘q.
11. Do‘kon har bir material bo‘yicha narx va mavjudlikni ko‘rsatadi. Mahsulot yo‘q bo‘lsa, kelishilgan vaqt ichida olib kelish yoki muqobil mahsulot taklif qilish mumkin. Muqobil va narx o‘zgarishlari mijozga qayta tasdiqlatiladi.
12. Do‘kon har bir buyurtma uchun yetkazish haqini va qo‘lda kiritilgan tayyorlash vaqtini beradi. Yo‘l vaqti xarita/yo‘l hisoblash integratsiyasidan olinadi. Mijozga taxminiy jami yetkazish vaqti ko‘rsatiladi; ETA o‘zgarsa Telegram va Mini Appda xabar beriladi. Xarita provayderi keyin tanlanadi.
13. Mijoz smetada materiallar, santexnik haqi, yetkazish va shoshilinch chaqiruv haqini alohida ko‘radi. Platforma haqi 0 ko‘rsatiladi. Barcha narxlar QQS bilan; yakuniy jami UZSda beriladi. Mijoz tasdiqlamaguncha do‘kon tayyorlashni boshlamaydi.
14. Smeta tasdiqlangach PDF shartnoma tayyorlanadi. Mijoz xizmat markaziga kelib yoki santexnik orqali manzilda qog‘oz nusxani imzolashi mumkin. Shartnomaga mijoz, santexnik, do‘kon vakili va xizmat markazi vakili imzo chekadi. Manzilda imzolangan nusxani santexnik xizmat markaziga olib borib qolgan imzolarni yig‘adi; xizmat markazi xodimi tizimda “imzolandi” deb belgilaydi. Hujjat nusxasini fayl qilib yuklash majburiy emas.
15. Shartnoma imzolanib, admin sozlagan avans (foiz yoki qat’iy summa) to‘langach, do‘kon tayyorlashni boshlaydi. Markazda naqd/karta-terminal; mijoz manzilida santexnik naqd yoki karta-terminal orqali qabul qilib tizimda qayd etadi. Tizim mijozga raqamli to‘lov tasdig‘i yuboradi; fiskal chek terminal/kassadan beriladi.
16. Do‘kon o‘z yetkazish xizmati bilan olib boradi. Kuryerga alohida akkaunt berilmaydi; do‘kon xodimi “tayyorlanmoqda”, “yo‘lga chiqdi”, “yetkazildi” holatlarini yangilaydi. Jonli lokatsiya MVPda yo‘q. Buyurtma bir necha qisman yetkazishga bo‘linishi mumkin; har birining statusi va ETA alohida, ammo yetkazish haqi bir marta olinadi.
17. Mijoz materiallarni olganini Mini Appda tasdiqlaydi. Noto‘g‘ri/zararlangan mahsulot bo‘lsa foto va izoh bilan admin/do‘konga xabar yuboradi.
18. Shartnomada santexnik taxminiy ish boshlanish/tugash vaqtini kiritadi. O‘zgarish bo‘lsa sabab va yangi taxminni kiritib, mijozga xabar beradi. Ish tugagach santexnik ixtiyoriy surat ilova qilib “bajarildi” deb belgilaydi; mijoz Mini Appda tasdiqlaydi.
19. Mijoz ishni tasdiqlagach qoldiq to‘lov amalga oshiriladi va buyurtma yopiladi. Mijoz tasdiqlamasa, admin nizo bo‘yicha qaror qilguncha qoldiq to‘lov va hamkorlar bilan yakuniy hisob-kitob bloklanadi. Nizo qarori tizimdan tashqarida kelishiladi; admin buyurtmada izoh qayd etadi.
20. Buyurtma yakunlangach mijoz santexnik va do‘konga baho hamda ixtiyoriy izoh beradi. Admin tekshirganidan keyin baholar umumiy profil va reytingda ko‘rinadi.

## 7. Buyurtma holatlari va xabarnomalar

Mijozga ko‘rinadigan asosiy ketma-ketlik:

`So‘rov yuborildi → santexnik biriktirildi/qabul qildi → ko‘rik vaqti belgilandi → smeta tayyor → smeta tasdiqlandi → shartnoma/avans → do‘kon tayyorlayapti → kuryer yo‘lda → material yetkazildi → ish boshlandi → santexnik yakunladi → mijoz tasdiqladi/to‘lov → yopildi`

Bekor qilingan, rad etilgan, qayta biriktirilgan, qisman yetkazilgan va nizo holatlari ham alohida qayd qilinadi. Muhim holat o‘zgarishlari Mini Appda ko‘rinadi va mijozga bot orqali xabar qilinadi. Xabar matni tanlangan tilga mos bo‘ladi.

## 8. To‘lovlar, komissiyalar va bekor qilish

### 8.1. To‘lov va hisob-kitob

- Mijoz shartnoma paytida admin belgilaydigan foiz yoki qat’iy summadagi avansni to‘laydi; qoldiq ish tasdiqlangach to‘lanadi.
- Markazda naqd yoki bank kartasi/terminal; mijoz manzilida santexnik naqd yoki terminal orqali qabul qiladi.
- Santexnik yig‘gan naqd pulni kompaniyaga topshirganda xizmat markazi xodimi tizimda qabul qilinganini tasdiqlaydi.
- Xizmat markazidagi rasmiy kassa/fiskal chek terminal yoki kassadan beriladi. Mini Appdagi kvitansiya esa to‘lov turi, summa, sana va qabul qiluvchini ko‘rsatuvchi ichki tasdiqdir; fiskal chek o‘rnini bosmaydi.
- Buyurtma mijoz tomonidan yakunlangach kompaniya do‘kon va santexnik bilan naqd hisob-kitob qiladi. Admin to‘lov summasi/sanasini qayd etadi, xizmat markazi xodimi berilgan summani tasdiqlaydi.
- Admin hisobotida buyurtma kesimida mijoz to‘lovi, avans/qoldiq, komissiyalar, hamkorlarga berilgan summa va qarzdorlik ko‘rsatiladi; Excel/CSV eksport mavjud.

### 8.2. Bekor qilish va nizolar

- Mijoz do‘kon material tayyorlashni boshlashidan hamda santexnik ishni boshlashidan avval bekor qilsa, avans to‘liq qaytariladi.
- Ushbu ikki hodisadan qaysi biri avval sodir bo‘lsa, undan keyin avans qaytarilmaydi.
- Kompaniya/do‘kon/santexnik sabab buyurtma bajarilmasa, avansni qaytarish masalasini admin alohida ko‘rib hal qiladi.
- Mijoz ish natijasiga e’tiroz bildirsa, qolgan to‘lov va hamkorlar bilan yakuniy hisob-kitob nizo hal bo‘lguncha bloklanadi. Admin qarorni tizimdan tashqarida kelishib, izoh qayd etadi.
- Bekor qilish va qaytarish shartlarini ishga tushirishdan oldin yurist bilan tekshirish zarur.

## 9. Xizmat markazi va admin panel

Admin/web-panelda quyidagilar boshqariladi:

- Buyurtmalar navbati, hudud/xizmat bo‘yicha santexnik tanlash, qayta biriktirish va do‘kon tayinlash.
- Pilot hudud, santexnik xizmat yo‘nalishlari, profil va akkauntlarni yaratish/ulash.
- Xizmat guruhlari, xizmat nomlari, birliklar, hududiy narxlar va kafolat muddati.
- Material katalogi; shoshilinch xizmat stavkalari; avans va har bir hamkor komissiyasi.
- Shartnoma andozalari va tillar bo‘yicha matn. Andozalar versiyalanadi; imzolangan shartnoma nusxasi o‘zgarmaydi. O‘zbekcha matn huquqiy jihatdan ustuvor, ruscha/inglizcha matnlar tarjimadir.
- Buyurtma/tasdiqlash/to‘lov/nizo/reyting jarayonlari; xizmat markazi manzili, telefoni va ish vaqti.
- Buyurtma bo‘yicha moliyaviy hisobotlar, CSV/XLSX eksporti va o‘zgartirib bo‘lmaydigan audit jurnali.

Marhamat pilotida bitta jismoniy markaz bor. Mijoz shartnoma uchun markazga ish vaqtida oldindan yozilmasdan boradi; navbat band qilish MVPda yo‘q. Markazning manzili, telefoni va ish vaqti Mini Appda ko‘rsatiladi. Mijozga yordam tugmasi va markaz telefoni beriladi.

## 10. Maxfiylik va xavfsizlik

- Mijoz so‘rov yuborishdan oldin telefon, manzil va ilova qilingan media buyurtma ishtirokchilariga berilishiga aniq rozilik beradi.
- Mijoz ma’lumotlari faqat buyurtmani bajarish uchun zarur bo‘lgan mijoz, tayinlangan santexnik, do‘kon va xizmat markazi rollariga ko‘rsatiladi.
- Telegram identifikatori akkauntni bog‘lash uchun, mijoz ulashgan telefon esa aloqa uchun ishlatiladi.
- Har bir xizmat markazi xodimining alohida akkaunti va admin huquqi bo‘ladi. Yuqori huquqli amallar (narx, komissiya, to‘lov, buyurtma, akkaunt) audit jurnalida kim va qachon bajargani bilan qayd etiladi.
- Do‘kon umumiy akkaunt ishlatgani sababli xodimlar kesimida izchillik/audit mavjud bo‘lmaydi.
- Media saqlash muddati, shaxsiy ma’lumotlarni o‘chirish va mahalliy qonunchilikka muvofiqlik ishga tushirishdan oldin alohida belgilanadi.

## 11. Texnologik stek va arxitektura

- **Backend:** Python va Django.
- **REST API:** Django REST Framework (DRF) asosida; mijoz/santexnik/do‘kon Mini Appi hamda admin CRM backend ma’lumotlari bilan REST API orqali ishlaydi.
- **Mini App frontend:** HTML, Django Templates va frontend uchun zarur CSS/JavaScript. Mini App sahifalarini Django template orqali render qilish ko‘zda tutiladi.
- **Admin CRM:** ReactJS asosida alohida web-ilova; backend bilan DRF REST API orqali bog‘lanadi.
- **Telegram:** bot Mini Appni ochish va Telegram xabarnomalarini yuborish uchun ishlatiladi. Foydalanuvchi identifikatorini server tomonda tekshirish usuli texnik loyihalashda belgilanadi.
- Barcha biznes qoidalari, narx/komissiya hisoblari, ruxsat tekshiruvlari va ma’lumotlarga kirish backendda bajariladi; foydalanuvchi interfeysidan kelgan qiymatlar server tekshiruvisiz ishonchli deb qabul qilinmaydi.
- Ma’lumotlar bazasi, hosting, media saqlash xizmati, React/Django versiyalari va API versiyalash usuli keyingi texnik loyihalashda tanlanadi. Bu qarorlar mazkur TZda hozircha ochiq.

## 12. Integratsiyalar va texnik chegaralar

- Telegram Bot/Mini App: kirish, bot orqali xabarnoma va Mini Appga yo‘naltirish.
- Xarita/yo‘l vaqti: manzil nuqtasi va yo‘l ETA uchun provayder tanlanadi. Provayder, API narxi, qamrovi va maxfiylik shartlari keyin baholanadi. Yo‘l ETA taxminiy; kuryerni jonli kuzatish emas.
- Onlayn to‘lov provayderi MVPda ulanmaydi. Naqd/karta-terminal to‘lovlari foydalanuvchilar tomonidan tizimda qayd etiladi; fiskal chek tashqi kassa/terminaldan.
- Texnik stek yuqoridagi 11-bo‘limda belgilanadi; ma’lumotlar bazasi va hosting alohida texnik loyihalash bosqichida tanlanadi.

## 13. MVP qabul mezonlari

1. Mijoz Telegram Mini Appda tilni tanlaydi, telefonini Telegram orqali ulashadi, xizmat guruhini va xaritadagi nuqtani/manzilni kiritadi; roziliksiz so‘rov yubora olmaydi.
2. Yangi so‘rov admin panelida ko‘rinadi. Admin mos santexnikni qo‘lda tayinlay oladi; u qabul yoki rad qiladi. Javob muddati tugaganda admin ogohlantirish oladi, avtomatik tayinlash bo‘lmaydi.
3. Mijozga santexnik qabul qilgandan keyin xabar boradi va tayinlangan santexnik telefoni ko‘rinadi; boshqa santexnik/do‘kon kontaktlari ochilmaydi.
4. Santexnik ko‘rik vaqtini, ish turini va miqdorlarni kiritadi. Xizmat haqi hududiy birlik stavkasi bo‘yicha to‘g‘ri hisoblanadi. Materiallar avtomatik hisoblanmaydi.
5. Admin buyurtmani bitta do‘konga tayinlaydi. Do‘kon narx/mavjudlikni tasdiqlaydi yoki sabab bilan rad etadi. Mijoz tasdiqlamagan yakuniy smeta va avanssiz do‘kon tayyorlashni boshlay olmaydi.
6. Smeta material, xizmat haqi, yetkazish va shoshilinch haqni alohida, platforma haqini nol, jami summani UZSda ko‘rsatadi. Smeta o‘zgarsa mijoz qayta tasdiqlaydi.
7. To‘rt tomon imzolagan shartnoma holati tizimda qayd etiladi; shartnoma tili tanlanadi, andoza versiyasi va imzolangan buyurtma tarixi saqlanadi.
8. Avans/qoldiq to‘lov, ichki kvitansiya, santexnik naqd pulini topshirish va kompaniyaning hamkorlarga naqd hisob-kitobi rollar bo‘yicha qayd etiladi.
9. Do‘kon tayyorlash vaqtini kiritadi, yo‘l ETA xarita integratsiyasidan olinadi. Status/ETA o‘zgarishlari mijozga Mini App va Telegramda xabar qilinadi. Qisman yetkazishlar alohida status/ETA bilan ishlaydi, yetkazish haqi bir marta olinadi.
10. Mijoz material qabulini va ish yakunini tasdiqlaydi; muammo bo‘lsa rasm/izoh yuboradi. Nizo holatida qoldiq hisob-kitob admin qarorigacha bloklanadi.
11. Bajarilgan buyurtmadan keyin reyting/izoh olinadi va admin moderatsiyasidan keyingina ommaga ko‘rsatiladi.
12. Admin moliyaviy hisobotni buyurtma, to‘lov, komissiya va qoldiq kesimida ko‘rib, CSV/XLSXga eksport qila oladi; muhim amallar auditda qayd etiladi.

## 14. Keyingi bosqichlar

- O‘lcham/normativlarga asoslangan avtomatik material kalkulyatori. Formulalarni admin tasdiqlaydi.
- Kuryer jonli lokatsiyasi.
- Santexnik cashback/bonuslari, do‘kon va brend reklamasi, premium joylashtirish.
- Marhamat pilotidan keyin boshqa hududlarga kengayish.
- Elektrchi, gaz ustasi va boshqa uy-ta’mirlash yo‘nalishlari.

## 15. Ochiq masalalar

1. Marhamat uchun aniq xizmat katalogi, o‘lchov birliklari va tariflar. Hozirgi xizmatlar jadvali tasdiqlangan boshlang‘ich namuna, yakuniy narxlar emas.
2. Material katalogidagi aniq nomlar, marka/model, diametr/o‘lcham va birliklar.
3. Shoshilinch chaqiruv haqi, avans miqdori va do‘kon/santexnik komissiyalarining aniq stavkalari.
4. Xizmat markazining aniq manzili, telefoni va ish vaqti; do‘kon va santexniklarning pilot akkauntlari.
5. Xarita/yo‘l ETA provayderi, narxi va manzil ma’lumotlarini qayta ishlash shartlari.
6. Shartnoma andozasining yuridik matni, to‘rt tomon imzo tartibi, bekor qilish/qaytarish shartlari va QQS/fiskal chek jarayoni yurist/buxgalter tomonidan tekshirilishi.
7. Media va shaxsiy ma’lumotlarni saqlash/o‘chirish muddati hamda ishga tushirishdan oldingi mahalliy qonunchilik tekshiruvi.
8. Foydalanuvchi xizmatlar va materiallar namunaviy jadvallarini haqiqiy Marhamat katalogi bilan to‘ldiradi yoki tuzatadi.

## 16. Biznes manbasi

Asosiy g‘oya `ideas.md` faylida saqlanadi. Ushbu TZ undagi avtomatik hisob-kitob, mijoz–santexnik–do‘kon oqimi, shaffof narx, tayyorlash va yetkazish vaqtini ko‘rsatish hamda komissiya modelini qamrab oladi. Avtomatik kalkulyator, bonus/reklama kabi xususiyatlar foydalanuvchi tanloviga ko‘ra MVPdan keyingi bosqichga o‘tkazildi.