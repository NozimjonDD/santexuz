# React CRM — amalga oshirilgan qamrov

Bu fayl `reactjs.md` va `TZ_docs.md`ni almashtirmaydi. Hujjatlardagi admin CRM doirasi bajarilgan; Mini App va Django backend ushbu topshiriqqa kiritilmagan.

| Talab | Yo‘l / amalga oshirilishi |
| --- | --- |
| KPI, sana filtri, navbat, grafik, moliyaviy xulosa | `/dashboard`, filtrlarga o‘tuvchi kartalar |
| Buyurtma qidirish, status/tab, sana, hamkor, guruh, shoshilinch, to‘lov filtrlari, sort, sahifalash | `/orders` |
| Admin yangi so‘rovi, mijoz roziligi | `/orders?new=1` |
| Umumiy ma’lumot, manzil, telefon, media/xarita placeholder, izoh | `/orders/:id` — Umumiy |
| Mos santexnikni qo‘lda tanlash, barcha hududlardagi do‘konlar | Buyurtma yuqori amallari; holat bo‘yicha bloklar |
| Smeta, birlik stavkalari, erkin material, katalogdan qo‘shish, muqobil izohi, mavjudlik | Smeta va materiallar |
| Tasdiqlangan snapshot, yangi versiya, jami/farq/avans farqi, demo mijoz tasdig‘i | Smeta va materiallar |
| Ko‘rik, ish boshlanish/tugash, do‘kon tayyorlash muddati, sabab, timeline | Jarayon |
| Qisman yetkazish, har qism status/ETA | Jarayon; umumiy yetkazish haqi o‘zgarmaydi |
| Andoza/tildan nusxa, to‘rt imzo, xodim/vaqt, statik PDF preview | Shartnoma |
| Avans/qoldiq, ikki bosqichli moliyaviy tasdiq, ichki kvitansiya | To‘lov va hisob-kitob; `/finance` |
| Santexnik naqd topshirishi va hamkorlarga sof hisob-kitob | `/finance?tab=cash`, `/finance?tab=partners` |
| Nizo, yakuniy to‘lov bloklari, qaror va izoh, avans qaytarish qarori | Nizo va baho; moliyaviy qoidalar |
| Mijoz material/ish qabulini demo qilish | Nizo va baho |
| Mijoz profili, buyurtma/to‘lov tarixi, rozilik/audit | `/customers`, `/customers/:id` |
| Santexnik profili, yo‘nalishlar, hudud, tajriba, faol/Telegram holati, komissiya | `/plumbers`, `/plumbers/:id` |
| Do‘kon profili, umumiy akkaunt, admin kontakti, holat, komissiya | `/shops`, `/shops/:id` |
| Xizmat UZ/RU/EN nomlari, birlik/tarif/shoshilinch haq/kafolat/ko‘rinish | `/catalog/services` |
| Material guruh/marka/diametr/birlik, alohida umumiy narxsiz | `/catalog/materials` |
| Oltita hisobot turi, filtrlangan haqiqiy CSV, Excel demo xabari | `/reports` |
| Andozalar, yangi versiya, qoralama/preview/faollashtirish/arxiv | `/contracts` |
| Tekshirish/ko‘rsatish/yashirish, moderatsiya auditga yozilishi | `/reviews` |
| Sana/akkaunt/amal/obyekt/qidiruv, oldingi/yangi qiymatlar | `/audit` |
| Pilot hudud, markaz, ish vaqti, javob muddati, avans, komissiyalar, bildirishnoma | `/settings` |
| Global qidirish, navbat bildirishnomalari, profil/demo reset, mobile drawer | AppShell |
| Native dialog fokus ushlash/qaytarish/Escape, label/xato/status matnlari | Shared UI |
| Development/production alohida muhitlar, route splitting, SPA hosting | Vite, `.env.*`, Nginx, Docker, CI |

## Boshqa kompyuterda tekshirish

Bu kompyuterda installer, test, typecheck, build, dev server yoki brauzer QA ishga tushirilmadi. Kod faqat o‘qish orqali ko‘rib chiqildi. Tayyor build, screenshot va o‘tgan test natijasi hozircha yo‘q.

Loyiha papkasida:

```bash
npm install && npm run check && npx playwright install --with-deps chromium webkit && npm run test:e2e && npm run preview
```

Birlamchi `npm install`dan keyin `package-lock.json`ni commit qiling. Keyingi sikllarda `npm ci` ishlating.

Brauzerda 390px, 768px va 1440px kenglikda jadvallar, mobil menyu va modal klaviatura navigatsiyasini ko‘ring. Asosiy moliyaviy/smeta qoidalari Vitestda, marshrutlar, qidirish/sahifalash, validatsiya, modal va CSV oqimlari Playwright ssenariylarida yozilgan.

## Statik bosqich chegaralari

Real login, API, Telegram tasdig‘i/xabari, xarita/yo‘l ETA, rasm yuklash, PDF generator, XLSX eksport, haqiqiy to‘lov yoki fiskal chek yo‘q. UI bularni haqiqiy bajarilgandek ko‘rsatmaydi. Standart tariflar, markaz ma’lumotlari, huquqiy matn va shaxsiy ma’lumot saqlash siyosati biznes tomonidan tasdiqlanishi kerak. Production hosting sozlamalari demo frontendni berish uchun tayyorlangan; serverli CRMning ishga tushirilganini anglatmaydi.
