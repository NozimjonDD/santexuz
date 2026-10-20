# Santex — Admin CRM

Marhamat pilotidagi santexnika xizmat markazi uchun o‘zbekcha React admin panel. Talablar: [`docs/reactjs.md`](docs/reactjs.md) va [`docs/TZ_docs.md`](docs/TZ_docs.md).

**Holat:** ikkita ma’lumot manbasi bor: `PUBLIC_API_MOCK=True` — statik JSON bilan interaktiv demo; `False` — `PUBLIC_API_BASE_URL` orqali real API ma’lumotlarini ko‘rish. APIga yozish commandlari, login ekrani, Telegram, haqiqiy to‘lov, xarita va PDF generator hali ulanmagan. Standart muhitlar mock rejimda; bu to‘liq backendli production CRM emas. Ommaviy demo JSONga haqiqiy mijoz ma’lumotlarini yozmang. Mini App ekranlari ushbu CRM doirasiga kirmaydi.

## Muhim: bu kompyuterda ishga tushirmang

Bu workspace faqat kod yozish uchun. Dependency o‘rnatish, test, typecheck, build va server buyruqlari **boshqa kompyuterda** bajariladi. Quyidagi buyruqlar o‘sha kompyuter uchun yozilgan. Ushbu ish davomida ular bajarilmadi; brauzer ko‘rinishi ham tekshirilmadi.

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
| Standart data | JSON mock, joriy sessiyada | JSON mock, joriy sessiyada |
| Ko‘rinadigan belgi | `DEVELOPMENT · MOCK JSON` | `PRODUCTION · MOCK JSON` |
| Natija | Vite HMR | `dist/`, kichraytirilgan va sahifa bo‘yicha ajratilgan fayllar |

### JSON mock yoki real API

`.env.development` / `.env.production`dagi public sozlamalar:

```dotenv
PUBLIC_API_MOCK=True
PUBLIC_API_BASE_URL=/api/v1/admin/
```

- `True`: `public/mock/database.json` HTTP orqali yuklanadi. Barcha namunaviy qiymatlar JSONda; qayta ishlatiladigan default/snapshot havolalarini `src/data/mock.ts` mustaqil UI nusxalariga ochadi. Tahrirlar faqat joriy sessiyada; reset JSONni qayta yuklaydi.
- `False`: base URLga `customers/`, `plumbers/`, `shops/`, `services/`, `materials/`, `orders/`, `payments/`, `reviews/`, `contract-templates/`, `audit-events/`, `settings/` qo‘shib GET yuboriladi. Ro‘yxat massiv yoki DRF `{ "results": [], "next": null }` bo‘lishi mumkin; keyingi sahifalar ham olinadi. Hozirgi compatibility DTO `src/domain/types.ts` shaklida, camelCase va numeric pul qiymatlari bilan bo‘lishi kerak. Batafsil kontrakt: [`instruction_api.md` §17](instruction_api.md#17-public_api_mock-va-public_api_base_url--joriy-ulanish).
- API rejimi **faqat ko‘rish uchun**: lokal demo mutation/reset va saqlash tugmalari bloklanadi. Server ma’lumotlari demo seed bilan almashtirilmaydi. Xato, noto‘g‘ri JSON, yetishmayotgan maydon yoki ruxsat muammosi qayta urinish oynasida ko‘rsatiladi.

Real API namunasi (`.env.production.local`ga yozish mumkin):

```dotenv
PUBLIC_API_MOCK=False
PUBLIC_API_BASE_URL=https://api.example.com/api/v1/admin/
```

`True`/`False` katta-kichik harfdan qat’i nazar o‘qiladi; `yes`, `1` yoki bo‘sh qiymat xato. Sozlama umuman berilmasa mock rejimi olinadi. `False` uchun base URL majburiy; HTTP(S) yoki `/` bilan boshlanadigan yo‘l qabul qilinadi.

Vite public o‘zgaruvchilarni [build vaqtida joylaydi](https://vite.dev/guide/env-and-mode). Developmentda env o‘zgarsa serverni qayta boshlang, productionda qayta build/deploy qiling — bular boshqa kompyuterda bajariladi. `VITE_*` va `PUBLIC_API_*` ichiga sir/parol/token yozmang. `.env.example` namuna sifatida berilgan; eski `VITE_DATA_MODE` ishlatilmaydi.

Real backend session cookie va ruxsatni o‘zi ta’minlaydi. Tashqi origin uchun backend credentialed CORSni va hosting CSPdagi `connect-src`ni aniq API originiga moslash kerak. `/api/` manzili shu domen ostida bo‘lsa Nginx uni backendga proxy qilishi kerak; SPA HTML fallback API emas. Backend host/porti hali berilmagani sabab proxy taxmin bilan qo‘shilmadi.

## Production hosting

`deploy/nginx-production.conf` ichida SPA history fallback bor: masalan, `/orders/DEMO-1006`ni to‘g‘ridan-to‘g‘ri ochish `index.html`ga qaytariladi. `/assets/` uchun uzoq cache, HTML uchun qayta tekshirish, xavfsizlik sarlavhalari va `/health` yo‘li belgilangan. Ilova domen ildiziga (`/`) joylashtirish uchun sozlangan. Production frontend statik fayllar sifatida Nginx orqali tarqatiladi; Docker ishlatilmaydi.

GitHub Actions kodi typecheck, biznes testlari, production build va desktop/mobil Playwright tekshiruvlarini bajarish uchun yozilgan; bu yerda hali bajarilmagan.

### Ubuntu server: `titan-crm.hh-academy.uz`

Standart konfiguratsiyada frontend JSON demo holatida qoladi. Real rejim yoqilsa backend DTOlari, sessiya, CORS/CSP yoki `/api/` proxy alohida moslanishi kerak. Nginx build qilingan statik fayllarni `/var/www/titan-crm/current` dan to‘g‘ridan-to‘g‘ri xizmat qiladi; mavjud sozlama faqat frontend hostingidir.

DNS’da `titan-crm.hh-academy.uz` A yozuvi server IP manziliga qaragan, 80/443 portlari ochiq bo‘lishi kerak. Backend Nginx sozlamalariga tegmasdan frontend uchun alohida site sozlanadi. Repo ildizidan (`admin_crm/` papkasining ota papkasidan):

```bash
cd admin_crm && npm ci && npm run build
```

TLS sertifikatini olishdan oldin HTTP bootstrap site’ni yoqing:

```bash
sudo install -d -m 0755 /var/www/letsencrypt /var/www/titan-crm/releases && sudo install -m 0644 deploy/nginx-bootstrap.conf /etc/nginx/sites-available/titan-crm && sudo ln -s /etc/nginx/sites-available/titan-crm /etc/nginx/sites-enabled/titan-crm && sudo nginx -t && sudo systemctl reload nginx
```

TLS sertifikatini olgach, Nginx production sozlamasini yoqing va static fayllarni joylang:

```bash
sudo certbot certonly --webroot --webroot-path /var/www/letsencrypt --non-interactive --agree-tos --email titanserviceuz@gmail.com --cert-name titan-crm.hh-academy.uz --domain titan-crm.hh-academy.uz && sudo install -m 0644 deploy/nginx-production.conf /etc/nginx/sites-available/titan-crm && sudo nginx -t && sudo systemctl reload nginx && sudo bash deploy/deploy-static.sh && curl --fail --silent --show-error https://titan-crm.hh-academy.uz/health
```

Keyingi frontend versiyasini joylash uchun `npm ci && npm run build && sudo bash deploy/deploy-static.sh` bajaring. Deploy skripti yangi build uchun alohida release papkasini yaratib, `current` symlinkini atomik almashtiradi; Nginx’ni qayta ishga tushirish yoki port sozlash talab qilinmaydi. Nginx qidiruv tizimlariga indekslamaslik headerini yuboradi, lekin bu kirish himoyasi emas.

## Tuzilma

```text
src/
  app/                  # Router, shell, sessiya store, xatolik chegarasi
  data/                 # Public config, HTTP, JSON/API loader, validation, mock adapter
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
public/mock/database.json # Sun’iy Marhamat ma’lumotlarining yagona manbasi
deploy/                 # Statik production server sozlamalari
```

## Demo ma’lumot va qoidalar

- 18 ta `DEMO-*` buyurtma barcha asosiy bosqichlarni namoyish qiladi. Ismlar va `+99800…` telefonlar sun’iy. Dastlabki namunaviy davr: 12–18 oktyabr 2026.
- Mock rejimida saqlash faqat React xotirasida. Sahifalar orasida o‘tish o‘zgarishlarni saqlaydi, to‘liq yangilash esa JSONni qayta yuklaydi. Profil menyusida “Demo holatini tiklash” bor. API rejimida profil menyusi serverdan qayta yuklashni taklif qiladi. Shaxsiy ma’lumotlar localStoragega yozilmaydi.
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

Backend uchun TZ bilan moslik tahlili, demo cheklovlari va taklif etilgan API kontrakti: [`instruction_api.md`](instruction_api.md). §17 hozirgi GET connector talabini belgilaydi; qolgan biznes commandlari va backend implementatsiyasi hali tayyor emas.

`StoreProvider` hozir lokal tranzaksiya chegarasi. DRF ulanayotganda repository/query va DTO adapter qatlami qo‘shiladi; demo amallari haqiqiy rol commandlariga almashtiriladi. Autentifikatsiya, ruxsatlar, server validatsiyasi, status mashinasi, audit, optimistic concurrency/idempotency, fayl va PDF, ETA va bildirishnomalar serverda amalga oshirilishi shart. Frontend qoidalari xavfsizlik chegarasi emas.

Qamrov va qo‘lda tekshirish uchun: [`docs/IMPLEMENTATION.md`](docs/IMPLEMENTATION.md).

UI va koddagi optimallashtirishlar: [`docs/OPTIMIZATION.md`](docs/OPTIMIZATION.md).
