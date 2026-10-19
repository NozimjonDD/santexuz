import { describe, expect, it } from 'vitest';
import { createSeed } from '../../data/seed';
import { directoryConfig } from './config';
import { applyDirectoryChange, directoryFormValues, normalizeDirectoryChange } from './model';

describe('Katalog va hamkor formalarini saqlash', () => {
  it('bo‘sh narx/stavkani null, aniq nolni esa nol sifatida saqlaydi', () => {
    for (const [input, expected] of [['', null], ['0', 0], ['15000', 15000]] as const) {
      const service = normalizeDirectoryChange('services', { name: 'Xizmat', areaRate: input, emergencyFee: input }, null, 'S-test');
      expect(service).toMatchObject({ kind: 'services', entity: { areaRate: expected, emergencyFee: expected } });

      for (const kind of ['plumbers', 'shops'] as const) {
        const partner = normalizeDirectoryChange(kind, { name: 'Hamkor', commission: input }, null, 'partner-test');
        expect(partner).toMatchObject({ kind, entity: { commission: expected } });
      }
    }
  });

  it('mijoz tahririda dastlabki ro‘yxatdan o‘tish sanasini saqlaydi', () => {
    const customer = createSeed().customers[0];
    const values = directoryFormValues(customer, directoryConfig.customers.fields);
    const change = normalizeDirectoryChange('customers', { ...values, name: '  Yangi ism  ' }, customer, customer.id);

    expect(change).toMatchObject({
      kind: 'customers',
      entity: { id: customer.id, name: 'Yangi ism', createdAt: customer.createdAt, consent: customer.consent },
    });
  });

  it('tarif va komissiya tahriri mavjud buyurtma nusxalarini o‘zgartirmaydi', () => {
    const db = createSeed();
    const orders = db.orders;
    const snapshots = structuredClone(orders);
    const service = db.services[0];
    const plumber = db.plumbers[0];
    const shop = db.shops[0];

    applyDirectoryChange(db, normalizeDirectoryChange('services', {
      ...directoryFormValues(service, directoryConfig.services.fields), areaRate: '999000',
    }, service, service.id));
    applyDirectoryChange(db, normalizeDirectoryChange('plumbers', {
      ...directoryFormValues(plumber, directoryConfig.plumbers.fields), commission: '0',
    }, plumber, plumber.id));
    applyDirectoryChange(db, normalizeDirectoryChange('shops', {
      ...directoryFormValues(shop, directoryConfig.shops.fields), commission: '',
    }, shop, shop.id));

    expect(db.services.find(item => item.id === service.id)?.areaRate).toBe(999000);
    expect(db.plumbers.find(item => item.id === plumber.id)?.commission).toBe(0);
    expect(db.shops.find(item => item.id === shop.id)?.commission).toBeNull();
    expect(db.orders).toBe(orders);
    expect(db.orders).toEqual(snapshots);
  });

  it('yangi hamkor yo‘nalishlarini forma massiviga bog‘lab qo‘ymaydi', () => {
    const db = createSeed();
    const categories = ['Ta’mirlash'];
    const previousCount = db.plumbers.length;
    const change = normalizeDirectoryChange('plumbers', { name: 'Yangi usta', categories }, null, 'P-test');
    applyDirectoryChange(db, change);
    categories.push('Isitish tizimi');

    expect(db.plumbers).toHaveLength(previousCount + 1);
    expect(db.plumbers[0]).toMatchObject({ id: 'P-test', categories: ['Ta’mirlash'] });
  });
});
