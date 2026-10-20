import { expect, test } from '@playwright/test';

test('JSON yuklash xatosi ko‘rinadi va qayta urinish ma’lumotlarni tiklaydi', async ({ page }) => {
  await page.route('**/mock/database.json', route => route.fulfill({ status: 503, contentType: 'application/json', body: '{}' }));
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Ma’lumotni yuklab bo‘lmadi' })).toBeVisible();
  await page.unroute('**/mock/database.json');
  await page.getByRole('button', { name: 'Qayta urinish' }).click();
  await expect(page.getByRole('heading', { name: 'Bosh sahifa', exact: true, level: 1 })).toBeVisible();
});

test('barcha asosiy sahifalar to‘g‘ridan-to‘g‘ri ochiladi', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  const routes: Record<string, string> = {
    dashboard: 'Bosh sahifa', orders: 'Buyurtmalar', customers: 'Mijozlar', plumbers: 'Santexniklar', shops: 'Do‘konlar',
    'catalog/services': 'Xizmatlar katalogi', 'catalog/materials': 'Materiallar', finance: 'Moliya', reports: 'Hisobotlar',
    contracts: 'Shartnomalar', reviews: 'Reytinglar', audit: 'Audit jurnali', settings: 'Sozlamalar',
  };
  for (const [route, heading] of Object.entries(routes)) {
    await page.goto(`/${route}`);
    await expect(page.getByRole('heading', { name: heading, exact: true, level: 1 })).toBeVisible();
    await expect(page.locator('.demo-banner')).toContainText('Namoyish muhiti');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    expect(overflow).toBe(false);
  }
  expect(errors).toEqual([]);
});

test('qidirish, bo‘sh holat va sahifalash ishlaydi', async ({ page }) => {
  await page.goto('/orders');
  await page.getByRole('button', { name: 'Keyingi sahifa' }).click();
  await expect(page.getByRole('button', { name: 'Oldingi sahifa' })).toBeEnabled();
  const search = page.getByRole('searchbox', { name: 'Qidirish', exact: true });
  await search.fill('DEMO-1006');
  await expect(page.locator('tbody tr')).toHaveCount(1);
  await expect(page.locator('tbody')).toContainText('DEMO-1006');
  await search.fill('mavjud-emas-000');
  await expect(page.getByText('Natija topilmadi', { exact: true })).toBeVisible();
});

test('yangi santexnik formasi o‘zbekcha validatsiya qiladi', async ({ page }) => {
  await page.goto('/plumbers');
  await page.getByRole('button', { name: 'Yangi santexnik' }).click();
  await page.getByRole('button', { name: 'Saqlash', exact: true }).click();
  await expect(page.getByText('Bu maydonni to‘ldiring.').first()).toBeVisible();
  await page.getByLabel('Ism-familiya').fill('Demo yangi usta');
  await page.getByLabel('Telefon (+998)').fill('123');
  await page.getByRole('button', { name: 'Saqlash', exact: true }).click();
  await expect(page.getByText('Telefonni +998 va 9 ta raqam bilan kiriting.')).toBeVisible();
});

test('nizo va buyurtma bo‘limlari ochiladi', async ({ page }) => {
  await page.goto('/orders/DEMO-1006');
  await expect(page.getByText('Ochiq nizo: qoldiq to‘lov va hamkorlarning yakuniy hisob-kitobi bloklangan.')).toBeVisible();
  for (const name of ['Smeta va materiallar', 'Jarayon', 'Shartnoma', 'To‘lov va hisob-kitob', 'Nizo va baho', 'Audit']) {
    await page.getByRole('button', { name, exact: true }).click();
    await expect(page.locator('h1')).toHaveText('DEMO-1006');
  }
});

test('modal Escape bilan yopilib fokusni qaytaradi', async ({ page }) => {
  await page.goto('/catalog/materials');
  const trigger = page.getByRole('button', { name: 'Yangi material' });
  await trigger.click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(trigger).toBeFocused();
});

test('filtrlangan hisobot haqiqiy CSV yuklaydi', async ({ page }) => {
  await page.goto('/reports');
  await page.getByRole('searchbox', { name: 'Qidirish', exact: true }).fill('DEMO-1006');
  await expect(page.locator('tbody tr')).toHaveCount(1);
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'CSV eksport', exact: true }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('hisobot-orders-DEMO.csv');
});

test('qator menyusi mos santexnik tayinlash oynasiga olib boradi', async ({ page }) => {
  await page.goto('/orders');
  await page.getByRole('searchbox', { name: 'Qidirish', exact: true }).fill('DEMO-1001');
  await page.getByLabel('DEMO-1001 amallari').click();
  await page.getByRole('link', { name: 'Santexnik tayinlash', exact: true }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Santexnik tayinlash / qayta tayinlash' })).toBeVisible();
  await expect(page.getByLabel('Mos santexnik')).toBeVisible();
});

test('imzo, avans yozuvi va xodim tasdig‘idan keyingina tayyorlash ochiladi', async ({ page }) => {
  await page.goto('/orders/DEMO-1004');
  const next = page.getByRole('button', { name: 'Demo bosqichni qayd etish' });
  await expect(next).toBeDisabled();
  await page.getByRole('button', { name: 'Shartnoma', exact: true }).click();
  await page.getByRole('button', { name: 'Imzolandi deb qayd etish' }).click();
  const checkboxes = page.getByRole('dialog').getByRole('checkbox');
  for (let i = 0; i < 4; i++) await checkboxes.nth(i).check();
  await page.getByRole('button', { name: 'Saqlash', exact: true }).click();
  await page.getByRole('button', { name: 'Tasdiqlash', exact: true }).click();
  await expect(next).toBeDisabled();
  await page.getByRole('button', { name: 'To‘lov va hisob-kitob', exact: true }).click();
  await page.getByRole('button', { name: 'To‘lov qayd etish', exact: true }).click();
  await page.getByLabel('Summa (UZS)').fill('79500');
  await page.getByLabel('Qabul qiluvchi / hamkor nomi').fill('Demo markaz');
  await page.getByLabel('Izoh / asos').fill('Avans uchun demo yozuv');
  await page.getByRole('button', { name: 'Yozuvni tekshirish' }).click();
  await page.getByRole('button', { name: 'Demo yozuv yaratish', exact: true }).click();
  await expect(next).toBeDisabled();
  await page.getByRole('button', { name: /xodim tasdig‘i/ }).click();
  await page.getByRole('button', { name: 'Tasdiqlash', exact: true }).click();
  await expect(next).toBeEnabled();
  await next.click();
  await page.getByRole('button', { name: 'Tasdiqlash', exact: true }).click();
  await expect(page.locator('.page-header .badge')).toContainText('Do‘kon tayyorlayapti');
});

test('CSV toastidan keyin jadval tanlangan sahifada qoladi', async ({ page }) => {
  await page.goto('/orders');
  await page.getByRole('button', { name: 'Keyingi sahifa' }).click();
  await expect(page.locator('.table-page-indicator')).toHaveText('2 / 2');
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'CSV eksport', exact: true }).click();
  await download;
  await expect(page.locator('.table-page-indicator')).toHaveText('2 / 2');
});

test('global qidiruv klaviatura bilan buyurtmaga olib boradi', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Bosh sahifa', exact: true, level: 1 })).toBeVisible();
  if ((page.viewportSize()?.width ?? 1440) <= 760) await page.getByRole('button', { name: 'Global qidiruvni ochish' }).click();
  else await page.keyboard.press('Control+k');
  const search = page.getByRole('searchbox', { name: 'Global qidiruv', exact: true });
  await expect(search).toBeFocused();
  await search.fill('DEMO-1006');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'DEMO-1006', exact: true, level: 1 })).toBeVisible();
});

test('xizmat yo‘nalishlarini checkbox bilan tanlash mumkin', async ({ page }) => {
  await page.goto('/plumbers');
  await page.getByRole('button', { name: 'Yangi santexnik' }).click();
  const choices = page.getByRole('group', { name: 'Xizmat yo‘nalishlari' });
  await choices.getByRole('checkbox', { name: 'Ta’mirlash', exact: true }).check();
  await choices.getByRole('checkbox', { name: 'Isitish tizimi', exact: true }).check();
  await expect(choices.getByRole('checkbox', { name: 'Ta’mirlash', exact: true })).toBeChecked();
  await expect(choices.getByRole('checkbox', { name: 'Isitish tizimi', exact: true })).toBeChecked();
});
