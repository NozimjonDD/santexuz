# Ubuntu production deploy

Nginx → Unix socket → Gunicorn → Django; PostgreSQL shu serverda. Namuna Ubuntu **24.04 LTS / Python 3.12+** uchun. Celery, Redis, Docker va frontend build talab qilinmaydi. Quyidagi buyruqlar faqat Ubuntu serverda bajariladi. Bu paket yozish kompyuterida ishga tushirilmadi va hali serverda sinovdan o‘tmadi.

## Birinchi o‘rnatish

Avval o‘zgarishlarni gitga commit/push qiling va serverda ishonchli commitni checkout qiling. Backend papkasiga kiring; barcha quyidagi nisbiy yo‘llar shu papkadan. Bu deploy kodi `sudo` bilan ishlaydi, shuning uchun tekshirilmagan branch yoki begona kodni ishlatmang. Skript SSH orqali ulanmaydi, branch tanlamaydi va `git pull` qilmaydi.

Git checkoutni runtime papkasidan tashqarida, masalan deploy foydalanuvchisining `~/src/` papkasida saqlang. `/srv/santex` faqat ushbu skript boshqaradigan release va persistent fayllar uchun ajratiladi.

Domenning A yozuvi server IP manziliga qarasin. AAAA yozuvi bo‘lsa IPv6 ham shu serverga ishlashi kerak. Tashqi firewall/security groupda SSH kirishini saqlab, 80/443 portlarini oching; 5432 portini internetga ochmang. Namuna mavjud boshqa saytlarni va firewall qoidalarini o‘chirmaydi.

Standart nom `santex`; boshqa nom tanlansa `/etc/santex` o‘rniga o‘z nomingizni yozing va barcha deploy buyruqlariga `--config /etc/<nom>/deploy.ini` ni **subcommanddan oldin** qo‘shing.

The checked-in sample configuration is [`deploy.ini.example`](deploy.ini.example); for this deployment it contains `titan-service.hh-academy.uz` and `titanserviceuz@gmail.com`. Bootstrap renders [`production.env.example`](production.env.example) into `/etc/santex/production.env` and generates the Django, database, and webhook secrets there. No production secret or generated `.env` belongs in Git.

```bash
sudo install -d -m 0750 /etc/santex && sudo install -m 0600 deploy/ubuntu/deploy.ini.example /etc/santex/deploy.ini && sudoedit /etc/santex/deploy.ini && sudo python3 deploy/ubuntu/deploy.py bootstrap
```

Muharrirda `domain` va `certificate_email` ni haqiqiy qiymatlarga almashtiring. `app_name`, `app_user` va `app_root` ni birinchi o‘rnatishdan oldin tanlang; keyin o‘zgartirish alohida ko‘chirishni talab qiladi. `app_root` — `/srv` yoki `/opt` ostidagi alohida papka. Config Gitdan tashqarida va root egasida qoladi.

`bootstrap` kerakli Ubuntu paketlarini o‘rnatadi, login huquqisiz OS foydalanuvchisini, PostgreSQL bazasi/ikki rolini, servislar va vaqtinchalik HTTP saytini yaratadi. Mavjud maxfiy qiymatlarni almashtirmaydi. Mavjud begona baza egasini yoki yuqori ruxsatli DB rolini o‘zlashtirmaydi. Dastlab HTTP faqat sertifikat tekshiruvi uchun ochiq, qolgan so‘rovlar 503 qaytaradi.

```bash
sudoedit /etc/santex/production.env
```

`TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` va haqiqiy OSRM-compatible `ROUTING_BASE_URL` ni kiriting; zarur bo‘lsa `ROUTING_API_KEY`. Qolgan sirlar bootstrapda tasodifiy yaratiladi. Formati `KEY=value`, qo‘shtirnoq, shell expansion yoki teskari slash ishlatmang. Domen, DB va fayl yo‘llari deploy.ini bilan mos turishi tekshiriladi. Runtime `.env` repoga yoki release papkasiga ko‘chirilmaydi.

DNS/firewall va muhit qiymatlari tayyor bo‘lgach:

```bash
sudo python3 deploy/ubuntu/deploy.py release && sudo python3 deploy/ubuntu/deploy.py https && sudo python3 deploy/ubuntu/deploy.py manage configure_telegram_webhook --register && sudo python3 deploy/ubuntu/deploy.py manage createsuperuser
```

`https` ACME webroot orqali sertifikat oladi, Nginx konfiguratsiyasini tekshirib yoqadi, renewal timer va tekshiruvdan keyin Nginx reload qiladigan hookni o‘rnatadi. Bot sozlash buyrug‘i webhook va Mini App menu tugmasini faqat `--register` berilganda o‘zgartiradi; navbatdagi Telegram update’larini tashlab yubormaydi. Oddiy `manage configure_telegram_webhook` faqat holatni o‘qiydi. Telegram tarixiy delivery xatosini saqlasa ogohlantirish chiqadi; yangi `/start` bilan amaldagi yetkazishni tekshiring.

Botda `/start` → o‘z kontaktini ulashish → Mini Appni ochish. Admin orqali xizmat markazi, haqiqiy narxlar, hamkorlar va uz/ru/en yuridik shartnoma andozalarini kiriting. `seed_pilot` faqat hudud va xizmat guruhlarini yaratadi.

## Fayllar va ruxsatlar

| Yo‘l (standart) | Vazifa |
| --- | --- |
| `/etc/santex/deploy.ini` | Root egasidagi domen va joylashuv konfiguratsiyasi |
| `/etc/santex/production.env` | `root:santex`, 0640; runtime sirlar va DML baza akkaunti |
| `/etc/santex/migration.env` | `root:root`, 0600; faqat deploy vaqtida alohida migratsiya akkaunti |
| `/srv/santex/releases/<vaqt>-<commit>/` | Root egasidagi o‘zgarmas kod va har release uchun alohida virtual muhit |
| `/srv/santex/current`, `previous` | Faol va oldingi sog‘lom release havolalari |
| `/srv/santex/shared/private/` | Ilova foydalanuvchisigagina ochiq yuklamalar, PDFlar; 0700/0600 |
| `/srv/santex/shared/static/` | Nginx uchun statik fayllar; 0755/0644 |
| `/var/backups/santex/<UTC-vaqt>/` | Faqat root o‘qiydigan DB va private fayl zaxirasi |
| `/run/santex-gunicorn.sock` | Faqat ilova/Nginx foydalanuvchilariga ochiq socket |

Runtime DB roli jadval egasi emas, `CREATE`, `TRUNCATE`, superuser va migrator a’zoligi berilmaydi; Django migratsiya tarixiga yozish ham yopiq. Migratsiyalar alohida DDL akkaunti hamda alohida `santex_migrate` OS foydalanuvchisi bilan bajariladi; runtime foydalanuvchisi uning process muhitini o‘qiy olmaydi. Audit va moliyaviy jurnallarning DB triggerlari saqlanadi. Production umumiy DB cache ishlatadi; `createcachetable` release jarayonining bir qismi. Shu orqali throttle holati workerlar orasida bo‘lishiladi; DRF throttling qat’iy atomik rate limiter emas.

Production loglari journald orqali yig‘iladi. Nginx/Gunicorn access loglariga query string yozilmaydi. Nginxda ochiq `/media`, `/private-media`, `/storage` yo‘llari yo‘q; buyurtma fayli faqat ruxsat tekshiradigan API orqali beriladi. Telegram Web frame ochilishi uchun Mini Appning o‘z CSP qoidasi saqlanadi. CDN yoki qo‘shimcha proxy qo‘shilsa IP/HTTPS ishonch chegarasini alohida moslang; namuna bitta Nginx proxy uchun.

Muddati tugagan staff sessiyalari va JWT blacklist yozuvlarini muntazam tozalang (masalan, serverning mavjud maintenance schedulerida har kuni). Buning uchun `manage clearsessions` va `manage flushexpiredtokens` buyruqlari bor; bu namuna ularni alohida timerga avtomatik qo‘shmaydi.

## Keyingi release

Serverdagi checkoutga tekshirilgan commit kelganidan keyin:

```bash
git pull --ff-only && sudo python3 deploy/ubuntu/deploy.py release && sudo python3 deploy/ubuntu/deploy.py status
```

`release` faqat commit qilingan backendni Git archive bilan chiqaradi; backendda dirty/untracked fayl bo‘lsa to‘xtaydi. Ixtiyoriy `release --ref <commit-yoki-tag>` shu repo ichidagi aniq refni oladi. Deployment shablonlari checkoutdagi versiyadan olinadi, shuning uchun odatda kerakli commitni checkout qilib `release` ishlating.

Yangi virtual muhitda paketlar root huquqisiz o‘rnatiladi, keyin release root egasiga o‘tkaziladi. Django production security check va model/migratsiya mosligi tekshiriladi. Sayt maintenance rejimiga o‘tadi, yozuvchi servislar to‘xtaydi, DB/private zaxira olinadi, migratsiyalar/cache/pilot/static tayyorlanadi va havola almashtiriladi. Socket orqali readiness 200 bo‘lgach sayt va timerlar ochiladi. Bu jarayonda qisqa uzilish bor.

`requirements/production.txt` hozir versiya oraliqlarini ishlatadi; har release ichida `requirements.resolved.txt` haqiqiy o‘rnatilgan versiyalarni saqlaydi. Yangi release boshqa versiya tanlashi mumkin. Paket yangilanishlarini avval stagingda tekshiring; oldingi release o‘z virtual muhitini saqlaydi. Avtomatik release/zaxira o‘chirish yo‘q.

Production `.env` yoki bazasi bilan `scripts/verify.sh` ishlatmang: u migratsiya/seed bajaradi. API va frontend testlarini alohida PostgreSQL sinov bazasi, DDL/CREATEDB huquqli **test** foydalanuvchisi va tayyor virtual muhitli boshqa kompyuter/stagingda bajaring:

```bash
bash scripts/verify.sh && node --test scripts/miniapp_api.test.mjs
```

Productiondagi test o‘rniga release security/consistency/readiness tekshiruvlarini bajaradi. Bu biznes oqimlarining to‘liq acceptance testi o‘rnini bosmaydi.

## Xato va rollback

Xato maintenance bosqichidan keyin yuz bersa, sayt 503 holatida qoladi. `maintenance.flag` ni qo‘lda o‘chirishdan oldin sababni tuzating; release’ni qayta bajarish mumkin. Loglar:

```bash
sudo journalctl -u santex.service -u santex-notifications.service -u santex-deadlines.service -u santex-backup.service --since '-30 min' --no-pager
```

Faqat oldingi kod yangi DB sxemasi bilan mos bo‘lsa:

```bash
sudo python3 deploy/ubuntu/deploy.py rollback && sudo python3 deploy/ubuntu/deploy.py status
```

Rollback oldingi sog‘lom release kodini va statik fayllarni faollashtiradi; DBni avtomatik orqaga ko‘chirmaydi. Readiness faqat DB/cache ulanishini tekshiradi — biznes mosligini stagingda tasdiqlash kerak. Birinchi release muvaffaqiyatsiz bo‘lsa hali oldingi sog‘lom release yo‘q: sababni tuzatib `release` ni qaytaring. Sxema o‘zgarishlarini bosqichma-bosqich, oldingi kodga mos tarzda chiqaring.

## Zaxira va tiklash

Har release oldidan va har kuni **02:30 UTC (+ tasodifiy 15 daqiqagacha)** `database.dump`, `private.tar.gz`, metadata olinadi. Faqat `COMPLETE` fayli bor katalog yakunlangan zaxira hisoblanadi. Qo‘lda:

```bash
sudo python3 deploy/ubuntu/deploy.py backup
```

Zaxiralar shifrlangan tashqi saqlashga ko‘chirilishi kerak. Bu serverdagi nusxaning o‘zi server yo‘qolishidan himoya qilmaydi. Disk hajmi va saqlash muddatini kuzating; ishlatilayotgan release yoki yagona yaxshi zaxirani o‘chirmang. Sirlarni (`/etc/santex`) alohida shifrlangan nusxada saqlang; ular DB/private arxivga qo‘shilmaydi.

Tiklashni avval alohida serverda mashq qiling. `pg_restore` ni bo‘sh yangi bazaga, migrator egasi bilan bajaring; `--disable-triggers` ishlatmang. Django data-only yuklash o‘rniga to‘liq custom dumpdagi data-before-trigger tartibi immutable jurnallarni tiklashga imkon beradi. Private arxivni alohida papkaga ochib, ilova egasini va 0700/0600 ruxsatlarni tiklang. So‘ng shu backup metadatadagi commitni ishga tushirib, runtime grantlarini qayta qo‘llang va API biznes testlarini bajaring. Amaldagi bazani ustidan avtomatik yozish bu namuna tomonidan bajarilmaydi.

## Serverdagi qabul tekshiruvi

```bash
python3 -m unittest discover -s deploy/ubuntu -p 'test_*.py' && sudo nginx -t && sudo systemd-analyze verify /etc/systemd/system/santex.service /etc/systemd/system/santex.socket /etc/systemd/system/santex-notifications.service /etc/systemd/system/santex-deadlines.service /etc/systemd/system/santex-backup.service && sudo certbot renew --dry-run && sudo python3 deploy/ubuntu/deploy.py status
```

`https://<domen>/health/live/` DBga murojaatsiz 200 qaytaradi; `/health/ready/` DB/cache ishlamasa tafsilotlarsiz 503 qaytaradi. Telegramda kontakt/login, barcha rol oqimlari, o‘zbekcha/ruscha PDF va begona akkauntning yopiq faylga kirishi qo‘lda tekshiriladi. HTTPS, haqiqiy Telegram/routing, PostgreSQL va restore jarayoni bu yozish kompyuterida bajarilmadi.

Deployment unit testlari maxfiy qiymatlarni shell sifatida talqin qilmaslik, fayl ruxsatlari, eksportdan keyingi kod o‘qilishi, tashqi symlinklarga tegmaslik va readiness xatosida maintenance saqlanishini tekshiradi. Tashqi buyruqlar va `chown` mock qilingan, shu sabab bu testlar root huquqini talab qilmaydi. Ular ham hali bajarilmagan.

Asoslar: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [Gunicorn + Nginx/systemd](https://gunicorn.org/deploy/), [Certbot webroot](https://eff-certbot.readthedocs.io/en/stable/using.html#webroot).
