# Santex — Admin CRM

Marhamat pilotidagi santexnika xizmat markazi uchun o‘zbekcha React admin panel. Talablar: [`docs/reactjs.md`](docs/reactjs.md) va [`docs/TZ_docs.md`](docs/TZ_docs.md).

**Holat:** statik, interaktiv demo. API, login, Telegram, haqiqiy to‘lov, xarita va PDF generator ulanmagan. Production build ham **DEMO** belgisi va mock ma’lumotlar bilan ishlaydi; bu backendli ishlab turgan xizmat emas. Maxfiy yoki haqiqiy mijoz ma’lumotlarini kiritmang. Demo ommaga ochiq bo‘lishi mumkin; unda autentifikatsiya yo‘q. Mini App ekranlari ushbu CRM doirasiga kirmaydi.

## Muhim: bu kompyuterda ishga tushirmang

Bu workspace faqat kod yozish uchun. Dependency o‘rnatish, test, typecheck, build, server va Docker buyruqlari **boshqa kompyuterda** bajariladi. Quyidagi buyruqlar o‘sha kompyuter uchun yozilgan. Ushbu ish davomida ular bajarilmadi; brauzer ko‘rinishi ham tekshirilmadi.

## Ishga tushirish

[Vite talabi](https://vite.dev/guide/)ga mos Node.js **22.12+** (22 LTS tavsiya), npm va zamonaviy brauzer kerak. React versiyalari uchun [rasmiy React hujjati](https://react.dev/versions), marshrutlar uchun [React Router deklarativ rejimi](https://reactrouter.com/start/declarative/installation) asos qilib olindi.

Loyiha papkasida birinchi o‘rnatish va development:

```bash
npm install && npm run dev
```

Manzil: `http://127.0.0.1:5173`. O‘rnatishdan keyin yaratilgan `package-lock.json`ni Gitga qo‘shing. Keyingi o‘rnatishlarda `npm ci` ishlating. Lock fayl bu kod yozish kompyuterida installer ishlatish taqiqlangani uchun generatsiya qilinmagan; soxta lock fayl qo‘shilmagan.

Production fayllarini yaratish va mahalliy ko‘rish:

```bash
npm run check && npm run preview
```

Manzil: `http://127.0.0.1:4173`. `dist/`ni statik serverga joylashtiring. `vite preview` faqat tayyor buildni mahalliy ko‘rish uchun; internetga production server sifatida chiqarmang.

Brauzerda desktop va mobil oqimlarni tekshirish (build avval tayyor bo‘lsin):

```bash
npx playwright install --with-deps chromium webkit && npm run test:e2e
```

## Development va production

| Sozlama | Development | Production |
| --- | --- | --- |
| Buyruq | `npm run dev` | `npm run build` |
| Muhit fayli | `.env.development` | `.env.production` |
| Data | Mock, joriy sessiyada | Mock, joriy sessiyada |
| Ko‘rinadigan belgi | `DEVELOPMENT` | `PRODUCTION · STATIC` |
| Natija | Vite HMR | `dist/`, kichraytirilgan va sahifa bo‘yicha ajratilgan fayllar |

`VITE_*` o‘zgaruvchilar build vaqtida ommaviy JavaScriptga yoziladi. U yerga sir, token yoki parol kiritmang. `VITE_DATA_MODE=mock` mazkur versiyaning yagona qo‘llab-quvvatlanadigan data rejimi; uni o‘zgartirish API ulanishini yaratmaydi.

## Production hosting

`deploy/nginx.conf` ichida SPA history fallback bor: masalan, `/orders/DEMO-1006`ni to‘g‘ridan-to‘g‘ri ochish `index.html`ga qaytariladi. `/assets/` uchun uzoq cache, HTML uchun qayta tekshirish, xavfsizlik sarlavhalari va `/health` yo‘li belgilangan. Ilova domen ildiziga (`/`) joylashtirish uchun sozlangan.

Docker orqali boshqa kompyuterda:

```bash
docker compose up --build -d
```

Manzil: `http://127.0.0.1:8080`. Konteyner unprivileged Nginx, read-only filesystem va vaqtinchalik yoziladigan kataloglar bilan sozlangan. Tashqi serverda TLS terminatsiyasi/reverse proxy alohida o‘rnatiladi. GitHub Actions kodi typecheck, biznes testlari, production build va desktop/mobil Playwright tekshiruvlarini bajarish uchun yozilgan; bu yerda hali bajarilmagan.

### Ubuntu server: `admin.titan-service.hh-academy.uz`

Bu frontend backend API’siga ulanmagan demo holatida qoladi. Unda faqat sun’iy ma’lumotlar bor; haqiqiy mijoz ma’lumotlarini kiritmang va uni amaldagi admin tizimi sifatida ishlatmang. Backend o‘z socketidan foydalanadi, CRM Docker konteyneri esa faqat `127.0.0.1:8081`da tinglaydi.

DNS’da `admin.titan-service.hh-academy.uz` A yozuvi server IP manziliga qaragan, 80/443 portlari ochiq bo‘lishi kerak. Backend Nginx sozlamalariga tegmasdan frontend uchun alohida site sozlanadi. Repo ildizidan (`admin_crm/` papkasining ota papkasidan):

```bash
cd admin_crm && sudo install -d -m 0755 /var/www/letsencrypt && sudo install -m 0644 deploy/nginx-bootstrap.conf /etc/nginx/sites-available/admin-crm && sudo ln -s /etc/nginx/sites-available/admin-crm /etc/nginx/sites-enabled/admin-crm && sudo nginx -t && sudo systemctl reload nginx && sudo certbot certonly --webroot --webroot-path /var/www/letsencrypt --non-interactive --agree-tos --email titanserviceuz@gmail.com --cert-name admin.titan-service.hh-academy.uz --domain admin.titan-service.hh-academy.uz && sudo install -m 0644 deploy/nginx-production.conf /etc/nginx/sites-available/admin-crm && sudo nginx -t && sudo systemctl reload nginx && docker compose up --build -d && curl --fail --silent --show-error https://admin.titan-service.hh-academy.uz/health
```

Docker Compose порт `8081`-ийг зөвхөн localhost-д bind хийдэг; Nginx HTTPS домэйн руу proxy хийнэ. Nginx config нь index-лэлтээс сэргийлэх `X-Robots-Tag` өгдөг ч энэ нь нэвтрэх хамгаалалт биш. Domain өөрчлөгдөх эсвэл certificate renewal тохиргоо нэмэх бол `deploy/nginx-production.conf`-ийг хамт шинэчил.

## Tuzilma

```text
src/
  app/                  # Router, shell, sessiya store, xatolik chegarasi
  data/seed.ts          # Sun’iy Marhamat ma’lumotlari
  domain/               # Turlar va mustaqil biznes qoidalari
  features/
    dashboard/          # KPI, dinamika, holatlar, operatsion navbat
    orders/             # Ro‘yxat, tafsilot, smeta, jarayon, shartnoma
    directory/          # Mijoz/usta/do‘kon/katalog konfiguratsiyalari
    finance/            # To‘lov, tasdiq, kvitansiya, hisob-kitob
    reports/            # Olti hisobot turi va CSV
    management/         # Andozalar, moderatsiya, audit, sozlamalar
  shared/               # Qayta ishlatiladigan UI, format va eksport
  styles.css            # Dizayn tokenlari va responsive uslublar
e2e/                    # Desktop va mobil brauzer ssenariylari
deploy/                 # Statik production server sozlamalari
```

## Demo ma’lumot va qoidalar

- 18 ta `DEMO-*` buyurtma barcha asosiy bosqichlarni namoyish qiladi. Ismlar va `+99800…` telefonlar sun’iy. Dastlabki namunaviy davr: 12–18 oktyabr 2026.
- Saqlash faqat React xotirasida. Sahifalar orasida o‘tish o‘zgarishlarni saqlaydi, to‘liq yangilash esa boshlang‘ich namunaga qaytaradi. Profil menyusida “Demo holatini tiklash” ham bor. Shaxsiy ma’lumotlar localStoragega yozilmaydi.
- `null` narx/stavka “Sozlanmagan”; `0` alohida haqiqiy nol qiymat. Tasdiqlanmagan markaz manzili/telefoni/ish vaqti, standart avans va komissiyalar bo‘sh boshlanadi. Buyurtmalardagi mavjud qiymatlar aniq demo nusxalar.
- Tasdiqlangan smeta va shartnoma matni katalog/andozadan mustaqil. Smeta qayta yuborilganda eski versiya, oldingi tasdiqlangan jami va imzolangan shartnoma nusxasi saqlanadi; yangi mijoz tasdig‘i va imzolar kutiladi.
- Material tayyorlash tasdiqlangan smeta, to‘rt tomon imzosi va yetarli tasdiqlangan avansdan keyin ochiladi. Yetkazish qismlarining soni yetkazish haqini ko‘paytirmaydi.
- Nizo mijoz to‘lovlari va yakuniy hamkor hisob-kitobini bloklaydi. Nizo qarori izoh bilan qayd etiladi. Mijoz ishni demo tasdiqlamaguncha qoldiq qabul qilinmaydi; avans turi bilan ushbu cheklovni chetlab o‘tib bo‘lmaydi.
- Ish/tayyorlash boshlanganidan keyin bekor qilingan buyurtmalarda hamkorning haqiqiy zarari noma’lum: tegishli hamkor qarzi “Sozlanmagan” bo‘ladi. Avansni qaytarish alohida admin qarori bilan qayd etiladi.
- Moliyaviy yozuv avval xodim tasdig‘ini kutadi. Tasdiqlanmagan yozuv tushumga kirmaydi. Takror to‘lov, ortiqcha avans, ortiqcha naqd topshirish va hamkor qarzidan ortiq hisob-kitob tekshiriladi.
- Audit UI’dan tahrirlanmaydi/o‘chirilmaydi. Bu lokal demo; backenddagi o‘zgarmas jurnal yoki haqiqiy akkaunt ruxsati o‘rnini bosmaydi.
- CSV ekrandagi filtrlangan datasetdan olinadi; UTF-8 BOM va formula injectiondan himoya bor. Excel tugmasi hujjatga mos demo xabari beradi, haqiqiy XLSX yaratmaydi.
- PDF/media/xarita uchun aniq belgilangan statik ko‘rinishlar berilgan. Hech bir tugma haqiqiy fayl yuklash, qo‘ng‘iroq, Telegram xabari yoki pul o‘tkazmasini amalga oshirmaydi.

## Backendga o‘tish

`StoreProvider` hozir lokal tranzaksiya chegarasi. DRF ulanayotganda sahifa komponentlarini o‘zgartirmasdan domain turlariga mos repository/query qatlami qo‘shing. Endpointlar ataylab taxmin qilinmagan. Autentifikatsiya, ruxsatlar, server validatsiyasi, status mashinasi, audit, optimistic concurrency/idempotency, fayl va PDF, ETA va bildirishnomalar serverda qayta amalga oshirilishi shart. Frontend qoidalari xavfsizlik chegarasi emas.

Qamrov va qo‘lda tekshirish uchun: [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md).

UI va koddagi optimallashtirishlar: [`docs/OPTIMIZATION.md`](docs/OPTIMIZATION.md).
