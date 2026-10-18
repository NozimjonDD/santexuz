# Santexnika Telegram Mini App uchun TZ hujjati rejasi

> Tarixiy TZ rejasi. Foydalanuvchining keyingi topshirig‘i asosida backend kodi ham yozildi. Joriy amalga oshirish holati: [implementation_plan.md](implementation_plan.md); texnik kontrakt: [API.md](API.md); test holati: [verification.md](verification.md).

## Muammo va yondashuv

`TZ_docs.md` dagi g‘oya santexnik, mijoz, do‘kon va yetkazib berishni birlashtiradigan Telegram Mini App haqida. Professional texnik topshiriqni birdan taxminlar bilan to‘ldirmasdan, foydalanuvchi bilan o‘zbek tilida bosqichma-bosqich aniqlashtirib tuzamiz. Avval MVP aniq belgilanadi; kengaytirilgan platforma imkoniyatlari keyingi bosqichlar sifatida ajratiladi.

## Hozirgi holat va manbalar

- `ideas.md` hozircha “ready to TZ plan” degan qisqa eslatmadan iborat.
- `TZ_docs.md` esa bo‘sh emas: unda asosiy g‘oya, uch tomonlama model, material kalkulyatori, buyurtma, yetkazish va monetizatsiya haqidagi dastlabki matn hamda Gemini havolasi bor. Shu sababli mavjud matn o‘chirilmaydi; keyin tartiblanib, yetishmayotgan qarorlar savollar orqali to‘ldiriladi.
- Kod bazasidagi `main.py` faqat umumiy Python boshlang‘ich namunasi; tayyor Mini App funksiyalari yoki arxitekturasi hozircha ko‘rinmaydi. TZ mavjud kodga mos deb taxmin qilinmaydi.
- `smartservices.uz` ochiq sahifasi va uning yuklangan front-end modullari onboarding/hudud tanlash, buyurtma va xizmat sahifalari, profil, til/ko‘rinish sozlamalari, yordam, hamkorlik, ommaviy oferta va Click/Paynet to‘lov sahifalariga oid ko‘rsatkichlarni berdi. Bu faqat UX namunasi sifatida ko‘riladi; ko‘rinmagan backend mantiqi yoki amaliy xulq taxmin qilinmaydi.
- Gemini havolasi umumiy kirish sahifasiga yo‘naltirildi; havola ortidagi to‘liq suhbatni o‘qib bo‘lmadi. `TZ_docs.md` dagi ko‘chirilgan matn hozircha asosiy g‘oya manbai.

## TZ hujjati uchun dastlabki mundarija

1. Hujjat maqsadi, mahsulot doirasi va atamalar.
2. Muammo, maqsadli foydalanuvchilar va qiymat taklifi.
3. Rollar va ruxsatlar: mijoz, santexnik, do‘konning umumiy akkaunti, xizmat markazi xodimi/admin.
4. Foydalanuvchi yo‘llari va buyurtma hayot sikli.
5. Xizmatlar katalogi, ish narxlari va hudud bo‘yicha mavjudlik.
6. O‘lchov kiritish, material sarfini hisoblash, formulalar, zaxira va qo‘lda tuzatish.
7. Smeta, material va xizmat narxining shaffof ko‘rinishi; narxni tasdiqlash va o‘zgarishlar.
8. Do‘konga buyurtma uzatish, tovar mavjudligi, tayyorlash, yetkazish, ETA va holat bildirishnomalari.
9. Mijoz manzili/lokatsiyasi, aloqa ma’lumotlari, maxfiylik va rozilik.
10. To‘lov, bekor qilish, qaytarish, nizolar va yordam jarayoni.
11. MVP talablari va qabul mezonlari; keyingi bosqichlar uchun alohida roadmap.
12. Integratsiyalar, ma’lumotlar va hisobotlar, xavfsizlik, audit va nosozlik holatlari.
13. Monetizatsiya, cheklovlar, taxminlar va ochiq savollar.

## Bajarish bosqichlari

1. Yuqoridagi boshlang‘ich mundarijani va Smart Services’dan mos UX namunalarini tasdiqlash.
2. Mahsulot doirasi, hudud, foydalanuvchi rollari va MVPdagi eng muhim natijalarni ketma-ket savollar bilan aniqlash.
3. Xizmatlar/materiallar hisob-kitobi va narx shaffofligi bo‘yicha qoidalarni, misollar bilan, aniqlashtirish.
4. Buyurtma, do‘kon, tayyorlash/yetkazish va mijozga xabar berish oqimini, istisnolarini ham qo‘shib, aniqlashtirish.
5. To‘lov, bekor qilish, rozilik/maxfiylik, administrator va biznes qoidalarini aniqlashtirish.
6. Qarorlarni MVP talablari va keyingi bosqichlar talablariga ajratib, `TZ_docs.md` ni o‘zbek tilida tartibli TZ hujjatiga aylantirish.
7. Hujjatdagi qarama-qarshiliklar, ochiq masalalar va har bir MVP talabi uchun tekshiriladigan qabul mezonlarini yakuniy ko‘rib chiqish.

## Muhim qarorlar va eslatmalar

- Foydalanuvchi MVP talablarini to‘liq, kelajakdagi imkoniyatlarni esa alohida keyingi bosqichlar sifatida ko‘rsatishni tasdiqladi.
- Hududiy reja: avval Andijon viloyati, Marhamat tumanida pilot; keyin boshqa hududlarga kengaytirish.
- Mijoz uchun Mini App ichida smeta, buyurtma holati va yetkazish vaqtini ko‘radigan alohida sahifa bo‘ladi.
- Dastlab mijoz Mini App orqali so‘rov yuboradi; administrator uni santexnikka qo‘lda biriktiradi. Biriktirilgach, santexnik mijoz bilan birga ish turi va o‘lchamlarni kiritib buyurtmani shakllantiradi.
- Mijozning boshlang‘ich so‘rovida telefon raqami, kerakli xizmat turi va manzil/lokatsiya majburiy bo‘ladi.
- Telefon raqami mijoz Telegramdagi telefon raqamini ulashish tugmasi orqali tasdiqlab yuboradi.
- Manzil xaritada nuqta tanlash va matnli manzil kiritish bilan beriladi.
- Dastlabki so‘rovda to‘rtta xizmat guruhi bo‘ladi: ta’mirlash, yangi o‘rnatish/almashtirish, quvur va kanalizatsiya, isitish tizimi. Aniq xizmatlar katalogi keyin to‘ldiriladi.
- Santexnik biriktirilgan so‘rovni qabul qilishi yoki rad etishi mumkin; rad etilganda admin boshqa santexnikka qo‘lda biriktiradi.
- Mijozga santexnik so‘rovni qabul qilgandan keyingina Telegram xabari va Mini App holati orqali xabar beriladi.
- MVPda material sarfi avtomatik hisoblanmaydi: materiallar ro‘yxati va miqdorini santexnik qo‘lda kiritadi. Xizmat narxi alohida hisoblanadi.
- Xizmat haqi xizmat turi va o‘lchov miqdoriga qarab (masalan, nuqta, metr yoki m²) hisoblanadi.
- Admin xizmat katalogida xizmat stavkasi va o‘lchov birligini belgilaydi; santexnik tegishli miqdorni kiritadi.
- Xizmat stavkalari hududga qarab alohida sozlanishi mumkin.
- Admin xizmat yoki mahsulot narxini o‘zgartirsa, bu faqat yangi smetalarga qo‘llanadi; avval tasdiqlangan buyurtma narxi saqlanadi.
- Komissiya stavkalari do‘kon/santexnik hamkor kesimida individual sozlanadi; admin umumiy standart stavka ham belgilashi mumkin.
- Ish tugagach santexnik bajarilgan deb belgilaydi; mijoz tasdiqlaydi, qoldiq to‘lov amalga oshiriladi va buyurtma yopiladi.
- Mijoz ishni tasdiqlamasa, nizo bo‘yicha admin qaror qilguncha qoldiq to‘lov va hamkorlar bilan yakuniy hisob-kitob bloklanadi.
- Do‘kon xodimi santexnik kiritgan har bir material uchun narx va mavjudlikni tasdiqlaydi; mijozga tasdiqlangan smeta ko‘rsatiladi.
- Material hozir mavjud bo‘lmasa, do‘kon uni kelishilgan muddat ichida olib kelish vaqtini ko‘rsatishi yoki muqobil mahsulot taklif qilishi mumkin; mijoz tasdig‘idan keyin smeta yangilanadi.
- Yetkazish ETA hisobida do‘kon tayyorlash vaqtini qo‘lda kiritadi, yo‘l vaqti xarita integratsiyasidan avtomatik olinadi; mijozga jami taxminiy muddat ko‘rsatiladi.
- Mijoz buyurtma holati o‘zgarganda Telegram bot xabari hamda Mini Appdagi holatlar orqali xabardor qilinadi.
- To‘lov oluvchi platforma/operator kompaniya bo‘ladi; kompaniya tushumdan do‘kon va santexnik bilan hisob-kitob qiladi.
- Shartnoma ikki yo‘l bilan tuziladi: mijoz xizmat markaziga keladi yoki santexnik mijoz manzilida rasmiylashtiradi. PDF qog‘ozda imzolanadi; mijoz, santexnik, do‘kon vakili va xizmat markazi vakili imzo chekadi.
- Mijoz manzilida shartnoma qilinganda santexnik hujjatni xizmat markaziga olib borib qolgan imzolarni yig‘adi; xodim tizimda imzolanganini belgilaydi, fayl yuklash talab qilinmaydi.
- To‘lov UZSda, naqd yoki karta terminali orqali: shartnomada admin belgilaydigan avans, ish tasdiqlangach qoldiq. Markazdagi rasmiy fiskal chek kassadan/terminaldan; tizim qo‘shimcha kvitansiya beradi.
- Xizmat markazida naqd pul va bank kartasi/terminal orqali to‘lov qabul qilinadi.
- Shartnoma tuzilganda avans olinadi; qolgan summa ish yakunlangach to‘lanadi.
- Avans miqdori admin belgilaydigan foiz yoki qat’iy summa bo‘ladi va buyurtmada alohida ko‘rsatiladi.
- Santexnik ish tugaganini belgilaydi, mijoz Mini Appda tasdiqlaydi; nizo chiqsa admin ko‘rib chiqadi.
- Mijoz ish boshlanishidan oldin bekor qilsa avans to‘liq qaytariladi; do‘kon material tayyorlashni boshlashi yoki santexnik ishni boshlashidan qaysi biri avval sodir bo‘lsa, o‘sha paytdan keyin avans qaytarilmaydi.
- Kompaniya, do‘kon yoki santexnik sabab buyurtma bajarilmasa, avansni qaytarish bo‘yicha admin har bir holatni alohida ko‘rib hal qiladi.
- Buyurtmadagi materiallar ro‘yxati tayyor bo‘lgach, admin buyurtmani do‘konga qo‘lda biriktiradi.
- Do‘kon buyurtmani qabul qilishi yoki sababini ko‘rsatib rad etishi mumkin; rad etilsa admin boshqa do‘konga qo‘lda biriktiradi.
- Materiallarni buyurtmani qabul qilgan do‘kon o‘z kuryeri/yetkazish xizmati bilan yetkazadi.
- Santexnik va do‘kon akkauntlarini admin qo‘lda yaratib, kirish ma’lumotlarini beradi.
- Admin santexnikni qo‘lda tanlaydi; tanlash ro‘yxati so‘rov hududi va xizmat turiga mos santexniklarni ko‘rsatadi.
- Admin do‘konni qo‘lda biriktiradi va ro‘yxatda hududdan qat’i nazar barcha do‘konlarni ko‘radi.
- Santexnik materiallarni mahsulot katalogidan tanlaydi, zarur bo‘lsa nomi erkin kiritiladigan qator qo‘shadi.
- Umumiy mahsulot katalogini admin yuritadi; do‘konlar buyurtma kelganda narx va mavjudlikni tasdiqlaydi.
- Do‘kon tasdiqlagan yakuniy smeta mijoz tomonidan Mini Appda tasdiqlanmaguncha material tayyorlash boshlanmaydi.
- Oqim: mijoz yakuniy smetani tasdiqlaydi, shartnoma tuziladi va qog‘ozda imzolanadi, avans to‘lanadi, shundan keyin do‘kon tayyorlashni boshlaydi.
- Shartnomada to‘rt tomon imzo chekadi: mijoz, santexnik, do‘kon vakili va xizmat markazi vakili. Santexnik manzilida tuzilganda masofadagi vakillarning qog‘oz imzosini qanday olish masalasi ochiq.
- Mijoz manzilida tuzilgan shartnomada santexnik qog‘oz hujjatni xizmat markaziga olib boradi va to‘rt tomon imzosini yig‘adi.
- Imzolangan shartnomada xizmat markazi xodimi tizimda “imzolandi” deb belgilaydi; hujjat faylini yuklash talab qilinmaydi.
- Santexnik mijoz manzilida naqd pul yoki karta terminali orqali to‘lov qabul qilishi va uni tizimda qayd etishi mumkin.
- Platforma daromadi do‘kon va santexnikdan buyurtma summasiga nisbatan foizli komissiya olish orqali shakllanadi.
- Do‘kon va santexnik uchun alohida komissiya foizlari admin tomonidan sozlanadi.
- Do‘kon komissiyasi materiallar summasidan, santexnik komissiyasi xizmat haqidan hisoblanadi.
- Mijoz buyurtmani yakunlagani tasdiqlangach, admin do‘kon va santexnikka qolgan summani qo‘lda o‘tkazadi.
- Komissiya hisob-kitobi va hamkorlarga to‘lanadigan sof summani faqat admin ko‘radi; hamkorlarga yakuniy to‘lov summasi beriladi.
- Mijoz smetada materiallar, santexnik xizmat haqi, yetkazish va platforma haqi alohida ko‘radi. Mijozdan alohida platforma haqi olinmaydi; platforma daromadi do‘kon/santexnik komissiyasidan.
- Yetkazish narxini do‘kon har bir buyurtmada belgilaydi; mijoz smetani tasdiqlaydi.
- Mijoz Telegram botdan Mini Appni ochadi va Telegram identifikatori bilan kiradi; telefon raqamini alohida ulashadi.
- Santexnik va do‘konlar ham Telegram orqali kiradi; admin ularning Telegram akkauntini tegishli rol/hududga biriktiradi.
- Do‘kon material tayyorlashni boshlamaguncha narxni o‘zgartirishi mumkin; har qanday o‘zgarishda mijoz qayta tasdiqlaydi va shartnoma/avansdagi farq yangilanadi.
- MVP interfeysi o‘zbek, rus va ingliz tillarini qo‘llab-quvvatlaydi.
- Narxlar va shartnoma summalari faqat o‘zbek so‘mida (UZS) yuritiladi.
- Buyurtma tugagach, mijoz santexnik va do‘konga baho hamda ixtiyoriy izoh qoldiradi.
- Baholar/izohlar admin tekshirganidan keyin hamma mijozlarga ochiq profil va reytingda ko‘rinadi.
- Santexnik cashback/bonuslari hamda do‘kon/brend reklamasi MVPga kirmaydi; keyingi bosqichlar roadmapiga kiritiladi.
- Admin boshqaruvi alohida web-panelda bo‘ladi; mijoz, santexnik va do‘kon Telegram Mini Appdan foydalanadi.
- Xizmat markazi xodimlari ham to‘liq admin huquqiga ega bo‘ladi; muhim amallarni o‘zgartirib bo‘lmaydigan audit jurnalida qayd etish talab qilinadi.
- Mijozga Mini App/Telegram botda yordam tugmasi va xizmat markazi telefon raqami ko‘rsatiladi.
- Yetkazishda MVP status va taxminiy yetib borish vaqti bilan cheklanadi; kuryerning jonli lokatsiyasini kuzatish keyingi bosqichga qoladi.
- Mijoz ko‘radigan statuslar: so‘rov yuborildi, santexnik biriktirildi/qabul qildi, smeta tayyor/tasdiqlandi, shartnoma/avans, do‘kon tayyorlayapti, kuryer yo‘lda, material yetkazildi, ish boshlandi, yakunlandi.
- Mijoz dastlabki so‘rovda muammoning surat yoki videosini ixtiyoriy ilova qila oladi.
- So‘rovdan oldin telefon, manzil va ilova qilingan media fayllar buyurtma ishtirokchilariga berilishiga aniq rozilik olinadi; ma’lumotlar faqat shu buyurtma ishtirokchilariga ko‘rsatiladi.
- ETA o‘zgarganda mijozga Mini App va Telegram orqali yangilangan vaqt haqida darhol xabar beriladi.
- Mini App o‘zbek, rus va ingliz tillarida bo‘ladi; foydalanuvchi birinchi kirishda tilni tanlaydi.
- Do‘kon xodimi kuryerning alohida akkauntisiz “yo‘lga chiqdi/yetkazildi” statuslarini yangilaydi.
- Mijoz materiallar yetkazilganini tasdiqlaydi; muammo bo‘lsa foto va izoh bilan admin/do‘konga yuboradi.
- Bitta buyurtma bir necha marta yetkazilishi mumkin; har bir yetkazishning o‘z ETA va statusi bo‘ladi.
- Bir buyurtmada qisman yetkazishlar bo‘lsa ham, mijozdan faqat bir marta yetkazish haqi olinadi; keyingi safarlar qo‘shimcha haq olmaydi.
- Har bir buyurtmani bitta do‘kon bajaradi; bajara olmasa admin uni boshqa do‘konga o‘tkazadi.
- Pilot hudud: Andijon viloyati, Marhamat tumani. Keyin boshqa hududlarga kengaytiriladi.
- Dastlab xizmat ko‘rsatish faqat Marhamat tumanida bo‘ladi.
- Marhamat pilotida bitta jismoniy xizmat markazi bo‘ladi.
- Mini Appda xizmat markazining manzili, telefoni va ish vaqti ko‘rsatiladi; admin ularni boshqaradi.
- Mijoz xizmat markaziga shartnoma uchun ish vaqtida oldindan yozilmasdan boradi; Mini Appda navbat bron qilish bo‘lmaydi.
- Mijoz santexnikning ismi/fotosi, tajribasi, xizmat yo‘nalishlari va admin tasdiqlagan reytingini ko‘radi; shaxsiy telefon raqami yashiriladi.
- Mijoz tanlangan do‘konning nomi, manzili va admin tasdiqlagan reytingini ko‘radi.
- Biriktirilgan mijoz santexnikning telefon raqamini ko‘rib, bevosita qo‘ng‘iroq qila oladi; boshqa mijozlarga raqam ko‘rsatilmaydi.
- Santexnik ish yakunlanganda ixtiyoriy yakuniy surat ilova qiladi; mijoz uni ko‘rib ishni tasdiqlaydi.
- Kafolat xizmat turiga qarab farq qiladi va xizmat katalogida ko‘rsatiladi.
- Kafolat davridagi muammo bo‘yicha mijoz xizmat markaziga telefon qiladi; ilovada alohida kafolat da’vosi ochilmaydi.
- Dastlabki so‘rovda xizmat guruhi tanlanadi, muammo izohi ixtiyoriy bo‘ladi; mijoz foto/video ham ilova qilishi mumkin.
- Santexnik uchun admin sozlaydigan qabul muddati bo‘ladi; javob muddati o‘tsa admin ogohlantiriladi va qayta biriktirishni o‘zi hal qiladi.
- Do‘kon uchun alohida qabul muddati talab qilinmaydi.
- Admin panelda buyurtma kesimida to‘lovlar, avans/qoldiq, komissiya, hamkorlarga o‘tkazmalar va qarzdorlik hisobotlari bo‘ladi.
- Admin moliyaviy hisobotlarni Excel/CSV formatida eksport qila oladi.
- Admin panelda PDF shartnoma matni/andozasi tahrirlanadi.
- Shartnoma andozalari versiyalanadi; imzolangan buyurtmaning shartnoma nusxasi keyin o‘zgarmaydi.
- Har bir avans/yakuniy to‘lovdan keyin mijozga to‘lov turi, summa, sana va qabul qiluvchini ko‘rsatuvchi raqamli kvitansiya yuboriladi.
- Tizimdagi kvitansiya to‘lov tasdig‘i bo‘ladi; rasmiy fiskal chekni xizmat markazi kassasi yoki terminal beradi.
- Santexnik yig‘gan naqd pulni topshirganda xizmat markazi/admin xodimi qabul qilinganini tizimda tasdiqlaydi.
- Buyurtma yakunlangach kompaniya hamkorlar bilan naqd hisob-kitob qiladi; xizmat markazi xodimi tizimda berilgan summani tasdiqlaydi.
- Mijozga tanlangan do‘kon nomi, manzili va reytingi ko‘rinadi, lekin do‘kon telefon raqami yashiriladi; aloqa xizmat markazi orqali.
- Erkin matnda qo‘shilgan material uchun nom, miqdor va o‘lchov birligi majburiy; izoh yoki marka ixtiyoriy.
- Narxlar QQS bilan kiritiladi; smetada QQS alohida qator bo‘lib ajratilmaydi.
- Shartnoma PDF o‘zbek, rus yoki ingliz tilida, mijoz tanlagan tilga muvofiq yaratiladi; har bir tildagi andoza admin tomonidan boshqariladi va versiyalanadi.
- Huquqiy farq yuz bersa, o‘zbekcha shartnoma matni ustuvor; ruscha va inglizcha matnlar tarjima nusxalari.
- Santexnik mijoz manziliga borib ko‘zdan kechiradi va ish/o‘lchov ma’lumotlarini mijoz bilan birga Mini Appda kiritadi.
- Smeta/shartnomadan oldingi ko‘rik bepul; xizmat haqi faqat kelishuv tasdiqlangach olinadi.
- Mijoz smetani qabul qilmasa, buyurtmani yopish huquqi adminning o‘zida qoladi.
- Mijoz smetani rad etib ixtiyoriy sabab yuborishi mumkin; admin buyurtmani yopadi yoki qayta ko‘rib chiqish uchun yo‘naltiradi.
- Smeta rad etilgach, o‘sha santexnik uni qayta tahrirlamaydi; admin buyurtmani yopadi yoki boshqa ustaga beradi.
- Ko‘rik tashrifining vaqti mijoz va santexnik telefon orqali kelishiladi; kelishilgan vaqt/status Mini Appda qayd etiladi.
- Santexnik telefon orqali kelishilgan ko‘rik vaqtini Mini Appga kiritadi; mijozning alohida tasdig‘i talab qilinmaydi.
- Santexnik shartnomada ishning taxminiy boshlanish/tugash muddatini kiritadi; mijoz statuslar orqali ko‘radi.
- Ish jadvali o‘zgarsa, santexnik sabab va yangi taxminiy muddatni kiritadi; mijozga Telegram va Mini Appda xabar beriladi.
- Mijoz xizmat katalogi va birlik narxlarini oldindan ko‘radi; yakuniy smeta santexnik ko‘rik va miqdorlarni kiritgandan keyin shakllanadi.
- Katalog narxlari mijoz kiritgan manzil/hududga mos stavkadan ko‘rsatiladi.
- Dastlabki xizmat nomlari, o‘lchov birliklari va tariflarni foydalanuvchi beradi; TZda tartiblanib, aniqlashtiriladi.
- Foydalanuvchi ro‘yxat tayyor bo‘lmagani uchun ko‘rib chiqish va tuzatish uchun namunaviy xizmatlar katalogi tayyorlanadi.
- Dastlabki material katalogi va o‘lchov birliklarini foydalanuvchi beradi; TZda tartiblanib, aniqlashtiriladi.
- Avtomatik material hisoblagich MVPdan keyingi bosqichga qo‘yiladi va ish turi/o‘lchov normativlariga tayanadi.
- Keyingi bosqichdagi avtomatik hisoblash formulalarini admin tasdiqlaydi.
- Keyingi bosqichlarda elektrchi, gaz ustasi va boshqa uy-ta’mirlash xizmatlarini qo‘shish imkoniyati ko‘riladi.

## Xizmatlar katalogi uchun dastlabki namuna

Foydalanuvchi dastlabki guruh va xizmatlar namunasini mos deb topdi; tariflar keyin belgilanadi. Quyidagi birliklar hali aniq xizmatlar bilan birga tekshiriladi.

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

## Materiallar katalogi uchun dastlabki namuna

Foydalanuvchi guruhlar qamrovini mos deb topdi; aniq diametr/o‘lchamlar, marka va katalog birliklari keyin foydalanuvchi/do‘kon bilan tasdiqlanadi. Narx va mavjudlik buyurtma bo‘yicha do‘kon tomonidan kiritiladi.

| Guruh | Namunaviy mahsulotlar | Katalogda aniqlashtiriladigan xususiyatlar |
|---|---|---|
| Suv quvurlari | PPR, metall-plastik yoki boshqa tasdiqlangan quvur | Material, diametr, uzunlik birligi, marka |
| Quvur fitinglari | Mufta, tirsak, troynik, o‘tish/adaptor | Diametr, rezba/o‘lcham, material, dona |
| Berkitish va nazorat | Sharli kran, qaytish klapani, filtr | Diametr, ulanish turi, marka, dona |
| Kran va jihozlar | Kran/aralashtirgich, dush komplekti, rakovina, sifon | Marka/model, ulanish/komplekt tarkibi, dona yoki komplekt |
| Kanalizatsiya | Kanalizatsiya quvuri, tirsak, troynik, manjet | Diametr, uzunlik/birlik, material |
| Isitish | Radiator, radiator krani, isitish quvuri, kronshteyn | O‘lcham/quvvat/diametr, material, dona/metr/komplekt |
| Sarf materiallari | FUM lenta, zichlagich, xomut, mahkamlash buyumlari | Qadoq/birlik va o‘lcham |
- MVPda “shoshilinch” santexnika so‘rovi bo‘ladi va unga alohida tarif qo‘llanadi.
- Shoshilinch xizmat tarifi admin tomonidan hudud va xizmat turi bo‘yicha alohida qat’iy narx sifatida belgilanadi.
- Shoshilinch so‘rovda santexnik qabul qilgach taxminiy kelish vaqtini belgilaydi; mijozga bu kafolatlangan emasligi ko‘rsatiladi.
- Shoshilinch chaqiruv haqi oddiy xizmat haqiga qo‘shimcha alohida qat’iy summa bo‘ladi.
- Mijoz so‘rovda shoshilinchlikni belgilaydi; admin santexnikka biriktirishdan oldin tasdiqlaydi.
- Shoshilinch xizmat faqat xizmat markazining ish vaqtida ishlaydi.
- Har bir do‘kon uchun xodimlar foydalanadigan bitta umumiy Telegram akkaunti bo‘ladi.
- Xizmat markazi xodimlarining har biri alohida Telegram akkauntida to‘liq admin rolida ishlaydi; audit amallari shaxsga bog‘lanadi.
- Do‘konning umumiy akkauntidagi audit amallari xodim kesimida emas, do‘kon akkaunti bo‘yicha yuritiladi.
- Hozircha bu ish faqat TZ hujjatini rejalash va yozishga qaratilgan; ilova kodini amalga oshirish ushbu doiraga kirmaydi.
- Ochiq qolgan ma’lumotlar: pilot xizmat tariflari va katalogning yakuniy tarkibi; materiallarning aniq nomi/markasi/diametri; avans, shoshilinch xizmat va individual komissiya stavkalari; xizmat markazining aloqa ma’lumotlari; xarita ETA provayderi; shartnoma va soliq siyosatini yurist/buxgalter bilan yakuniy tekshirish. Noma’lum qiymatlar TZda sozlanadigan yoki keyin tasdiqlanadigan ma’lumot sifatida ko‘rsatiladi.
- `smartservices.uz` dan dizayn yoki kod ko‘chirilmaydi; faqat mahsulotga mos kelishi mumkin bo‘lgan UX g‘oyalari alohida muhokama qilinadi.
