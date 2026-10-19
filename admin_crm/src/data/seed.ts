import { categories, type Database, type Estimate, type Order, type OrderStatus, type Service } from '../domain/types';

const at = (day: number, hour = 10) => `2026-10-${String(day).padStart(2, '0')}T${String(hour).padStart(2, '0')}:00:00+05:00`;
const contractText = `NAMUNAVIY SHARTNOMA — YURIDIK HUJJAT EMAS\n\n1. Tomonlar: mijoz, tayinlangan santexnik, do‘kon vakili va xizmat markazi vakili.\n2. Ish hajmi va barcha summalar buyurtmada tasdiqlangan smeta nusxasiga muvofiq. Narxlar QQS bilan. Platforma haqi: 0 so‘m.\n3. Material tayyorlash to‘rt tomon imzosi va belgilangan avansdan keyin boshlanadi.\n4. Ish mijoz tomonidan qabul qilingach qoldiq to‘lanadi. Nizo bo‘lsa yakuniy hisob-kitob to‘xtatiladi.\n5. Bekor qilish va qaytarish shartlari ishga tushirishdan oldin yurist tomonidan tasdiqlanishi kerak.\n\nO‘zbekcha matn ustuvor. Ushbu matn faqat interfeys namoyishi uchun.`;
const serviceNames = [
  'Aralashtirgichni ta’mirlash', 'Suv sizishini bartaraf etish', 'Kanalizatsiya tiqilishini ochish',
  'Aralashtirgich o‘rnatish', 'Rakovina o‘rnatish', 'Unitaz o‘rnatish', 'Dush komplekti o‘rnatish',
  'Suv isitgich o‘rnatish', 'Suv quvurini almashtirish', 'Kanalizatsiya quvurini yotqizish',
  'Radiator o‘rnatish', 'Isitish quvurini almashtirish',
];
const services: Service[] = serviceNames.map((name, i) => ({
  id: `S-${i + 1}`, name, nameRu: '', nameEn: '', category: categories[i < 3 ? 0 : i < 8 ? 1 : i < 10 ? 2 : 3],
  unit: i === 1 ? 'nuqta' : i === 2 ? 'holat' : [8, 9, 11].includes(i) ? 'metr' : 'dona',
  areaRate: i === 11 ? null : [80000, 120000, 150000, 100000, 180000, 200000, 170000, 300000, 45000, 50000, 180000][i],
  emergencyFee: i === 11 ? null : 50000, warranty: '', description: 'Namuna katalog. Tariflar tasdiqlanmagan demo qiymatlar.', isActive: true, visible: true,
}));
const statuses: OrderStatus[] = ['new', 'inspection', 'approval', 'contract', 'partial', 'dispute', 'completed', 'assigned', 'shop_pending', 'preparing', 'working', 'cancelled', 'transit', 'completion', 'rejected', 'accepted', 'estimating', 'delivered'];

export function createSeed(): Database {
  const customers = ['Azizbek Karimov', 'Dilnoza Qodirova', 'Javohir Rasulov', 'Gulnoza Ergasheva', 'Shoxrux Aliyev', 'Malika Sobirova', 'Otabek Tursunov', 'Nargiza Yo‘ldosheva', 'Sardor Mahmudov', 'Zilola Hamidova'].map((name, i) => ({
    id: `C-${i + 1}`, name, phone: `+99800000${String(i + 1).padStart(4, '0')}`, telegramId: `demo-customer-${i + 1}`,
    createdAt: at(1 + i), notes: 'Sun’iy namuna mijoz. Aloqa ma’lumotlari haqiqiy emas.', consent: true,
  }));
  const plumbers: Database['plumbers'] = ['Akmal Rahimov', 'Bekzod Ismoilov', 'Diyorbek Usmonov', 'Farrux Olimov', 'Jamshid Nabiyev'].map((name, i) => ({
    id: `P-${i + 1}`, name, phone: `+99800001${String(i + 1).padStart(4, '0')}`, telegramId: i === 4 ? '' : `demo-plumber-${i + 1}`,
    district: 'Marhamat', categories: i === 0 ? [...categories] : [categories[i % 4], categories[0]],
    experience: 4 + i, photo: '', notes: 'Demo profil. Shaxsiy akkaunt.', isActive: i !== 4, commission: 10 as number | null,
  }));
  const shops = ['Aqua Market', 'Marhamat Santex', 'Quvur Savdo', 'Vodiy Qurilish'].map((name, i) => ({
    id: `SH-${i + 1}`, name, contactName: 'Demo vakil', address: `Namuna savdo ko‘chasi, ${i + 1}-uy`,
    district: i === 3 ? 'Andijon shahri' : 'Marhamat', phone: `+99800002${String(i + 1).padStart(4, '0')}`,
    telegramId: `demo-shop-${i + 1}`, description: 'Bitta umumiy Telegram akkaunti. Demo do‘kon.', isActive: true, commission: 5 as number | null,
  }));
  const materialNames = ['PPR suv quvuri', 'PPR tirsak', 'PPR troynik', 'Sharli kran', 'Qaytish klapani', 'Suv filtri', 'Aralashtirgich', 'Sifon', 'Kanalizatsiya quvuri', 'Radiator', 'FUM lenta', 'Mahkamlash xomuti'];
  const materials = materialNames.map((name, i) => ({
    id: `M-${i + 1}`, name, category: ['Suv quvurlari', 'Quvur fitinglari', 'Quvur fitinglari', 'Berkitish va nazorat', 'Berkitish va nazorat', 'Berkitish va nazorat', 'Kran va jihozlar', 'Kran va jihozlar', 'Kanalizatsiya', 'Isitish', 'Sarf materiallari', 'Sarf materiallari'][i],
    brand: 'Demo marka', size: i < 6 ? '25 mm' : '', unit: [0, 8].includes(i) ? 'metr' : 'dona', description: 'Namuna nomenklatura.', isActive: true,
  }));
  const orders: Order[] = statuses.map((status, i) => {
    const service = services[i % services.length];
    const approved = ['contract', 'partial', 'dispute', 'completed', 'preparing', 'working', 'cancelled', 'transit', 'completion', 'delivered'].includes(status);
    const assigned = !['new', 'rejected'].includes(status);
    const day = i < 6 ? 18 : 17 - (i % 6);
    const estimate: Estimate = {
      version: 1, services: [{ id: `EL-${i}`, name: service.name, quantity: service.unit === 'metr' ? 6 : 1, unit: service.unit, price: service.areaRate ?? 40000 }],
      materials: [
        { id: `ML-${i}-1`, name: 'PPR suv quvuri', quantity: 6, unit: 'metr', price: 18000, brand: 'Demo marka', available: true },
        { id: `ML-${i}-2`, name: 'PPR tirsak', quantity: 4, unit: 'dona', price: 8000, brand: 'Demo marka', available: true },
      ], deliveryFee: 25000, emergencyFee: i % 5 === 0 ? 50000 : 0, approved, createdAt: at(day, 9),
    };
    if (status === 'new' || status === 'assigned') { estimate.materials = []; estimate.deliveryFee = null; }
    const signatures = approved && status !== 'contract' ? [true, true, true, true] : [false, false, false, false];
    return {
      id: `DEMO-${1001 + i}`, createdAt: at(day, 8 + i % 9), customerId: customers[i % customers.length].id,
      plumberId: assigned ? (plumbers.find(p => p.isActive && p.categories.includes(service.category))?.id ?? 'P-1') : null,
      shopId: approved || ['approval', 'shop_pending'].includes(status) ? shops[i % shops.length].id : null,
      category: service.category, service: service.name, address: `Marhamat, Namuna mahallasi, ${12 + i}-uy`, coordinates: '40.5000, 72.3300 · demo nuqta',
      description: 'Oshxona suv tizimini ko‘rib chiqish va zarur qismlarni almashtirish. Bu sun’iy namuna so‘rov.',
      status, urgent: i % 5 === 0, urgencyApproved: i % 5 === 0 && approved, consent: true,
      assignedAt: assigned ? at(day, 8) : null, inspectionAt: assigned ? at(day, 14) : '', workStart: approved ? at(day, 15) : '', workEnd: approved ? at(day, 18) : '', etaReason: '', preparationMinutes: approved ? 30 : null,
      estimate, confirmedEstimate: approved ? structuredClone(estimate) : null, estimateHistory: [],
      advance: { mode: 'percent', value: 30 }, commissions: { plumber: 10, shop: 5 },
      contract: { templateId: 'CT-UZ-1', version: 1, language: 'UZ', text: contractText, signatures, signedAt: signatures.every(Boolean) ? at(day, 11) : null, signedBy: signatures.every(Boolean) ? 'Demo administrator' : null },
      deliveries: status === 'partial' ? [
        { id: `D-${i}-1`, label: '1-qism · quvurlar', status: 'delivered', eta: at(18, 12), note: 'Mijozga topshirilgan (demo).' },
        { id: `D-${i}-2`, label: '2-qism · fitinglar', status: 'transit', eta: at(18, 16), note: 'Yo‘l ETA namuna; integratsiya ulanmagan.' },
      ] : approved && !['contract', 'cancelled'].includes(status) ? [{ id: `D-${i}`, label: 'Asosiy yetkazish', status: ['completed', 'working', 'completion', 'dispute', 'delivered'].includes(status) ? 'delivered' : status === 'transit' ? 'transit' : 'preparing', eta: at(day, 14), note: 'Demo ETA. Jonli kuzatuv yo‘q.' }] : [],
      timeline: [
        { id: `T-${i}-1`, at: at(day, 8), title: 'So‘rov yaratildi', detail: 'Mijoz roziligi qayd etilgan · DEMO' },
        ...(assigned ? [{ id: `T-${i}-2`, at: at(day, 9), title: 'Santexnik tayinlandi', detail: 'Xizmat markazi · demo administrator' }] : []),
        ...(approved ? [{ id: `T-${i}-3`, at: at(day, 10), title: 'Smeta demo tasdiqlandi', detail: '1-versiya · namuna mijoz tasdig‘i' }] : []),
      ], notes: [], dispute: { open: status === 'dispute', reason: status === 'dispute' ? 'Ulanish joyida sizish qayta kuzatilgan. Mijoz tekshiruv so‘radi (demo).' : '', resolution: '', previousStatus: status === 'dispute' ? 'completion' : null },
      materialReceived: ['working', 'completion', 'completed', 'dispute'].includes(status), customerCompleted: status === 'completed',
      preparationStarted: approved && !['contract', 'cancelled'].includes(status), workStarted: ['working', 'completion', 'completed', 'dispute'].includes(status),
      cancelReason: status === 'cancelled' ? 'Mijoz ko‘rikdan oldin bekor qilgan (demo).' : '', refundDecision: status === 'cancelled' ? 'full' : null,
    };
  });
  const payments: Database['payments'] = [];
  for (const [i, order] of orders.entries()) {
    const total = order.estimate.services.reduce((s, l) => s + l.quantity * (l.price ?? 0), 0) + order.estimate.materials.reduce((s, l) => s + l.quantity * (l.price ?? 0), 0) + (order.estimate.deliveryFee ?? 0) + (order.estimate.emergencyFee ?? 0);
    if (order.contract.signedAt) {
      payments.push({ id: `PAY-${i}-A`, orderId: order.id, type: 'advance', method: 'cash', amount: Math.round(total * 0.3), timestamp: order.createdAt, receivedBy: 'Demo administrator', recordedBy: 'Demo administrator', note: 'Namuna avans', status: 'confirmed', collector: i % 2 === 0 ? 'plumber' : 'center', confirmedBy: 'Demo operator' });
      if (order.status === 'completed') {
        payments.push({ ...payments[payments.length - 1], id: `PAY-${i}-B`, type: 'balance', collector: 'center', amount: total - Math.round(total * 0.3) });
        const labor = order.estimate.services.reduce((s, l) => s + l.quantity * (l.price ?? 0), 0);
        const materialsTotal = order.estimate.materials.reduce((s, l) => s + l.quantity * (l.price ?? 0), 0);
        payments.push({ ...payments[payments.length - 1], id: `PAY-${i}-S`, type: 'shop_settlement', amount: materialsTotal - Math.round(materialsTotal * 0.05) + 25000 });
        payments.push({ ...payments[payments.length - 1], id: `PAY-${i}-P`, type: 'plumber_settlement', amount: labor - Math.round(labor * 0.1) });
      }
    }
  }
  return {
    customers, plumbers, shops, services: structuredClone(services), materials, orders, payments,
    reviews: [
      { id: 'R-1', orderId: 'DEMO-1007', customerId: 'C-7', targetType: 'plumber', targetId: orders[6].plumberId!, score: 5, comment: 'Vaqtida keldi, ishni tartibli bajardi. Rahmat! (Demo izoh)', createdAt: at(17, 18), status: 'pending' },
      { id: 'R-2', orderId: 'DEMO-1007', customerId: 'C-7', targetType: 'shop', targetId: orders[6].shopId!, score: 4, comment: 'Materiallar to‘liq yetkazildi. (Demo izoh)', createdAt: at(17, 18), status: 'published' },
      { id: 'R-3', orderId: 'DEMO-1007', customerId: 'C-7', targetType: 'plumber', targetId: 'P-1', score: 3, comment: 'Qo‘shimcha tekshiruv talab qilinadigan namuna izoh.', createdAt: at(17, 19), status: 'hidden' },
    ],
    templates: [
      { id: 'CT-UZ-1', name: 'Santexnika xizmat ko‘rsatish', language: 'UZ', version: 1, note: 'Boshlang‘ich demo andoza', text: contractText, status: 'active', createdAt: at(1), author: 'Demo administrator' },
      { id: 'CT-RU-1', name: 'Santexnika xizmat ko‘rsatish', language: 'RU', version: 1, note: 'Tarjima uchun qoralama', text: 'ДЕМО — перевод не утверждён. Юридический приоритет имеет узбекский текст.', status: 'draft', createdAt: at(2), author: 'Demo administrator' },
      { id: 'CT-EN-1', name: 'Santexnika xizmat ko‘rsatish', language: 'EN', version: 1, note: 'Tarjima uchun qoralama', text: 'DEMO — translation pending review. The Uzbek text takes legal precedence.', status: 'draft', createdAt: at(2), author: 'Demo administrator' },
    ],
    audit: orders.slice(0, 8).map((o, i) => ({ id: `AUD-${i}`, actor: i === 4 ? 'Do‘kon: Aqua Market (umumiy akkaunt)' : 'Demo administrator', action: 'Yaratish', objectType: 'Buyurtma', objectId: o.id, timestamp: o.createdAt, summary: 'Namuna buyurtma yaratildi', before: null, after: { status: o.status } })),
    settings: { centerName: 'Santex xizmat markazi', address: '', phone: '', opens: '', closes: '', responseMinutes: 30, advanceMode: 'percent', advanceValue: null, plumberCommission: null, shopCommission: null, language: 'uz', notifications: true },
  };
}
