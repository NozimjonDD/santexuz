import type { Database } from '../domain/types';
import { isRecord, parseDatabase } from './schema';

// The JSON uses explicit shared defaults and snapshot references to avoid copying
// the same material rows and contract text into every static example.
export function parseMockDatabase(value: unknown): Database {
  if (!isRecord(value) || !isRecord(value.orderDefaults) || !isRecord(value.estimateDefaults)
    || !isRecord(value.contractDefaults) || !isRecord(value.estimates) || !isRecord(value.contracts) || !Array.isArray(value.orders)) {
    throw new Error('Mock JSON tuzilishi mos emas.');
  }
  const { orderDefaults, estimateDefaults, contractDefaults, estimates, contracts } = value;
  function snapshot(records: Record<string, unknown>, defaults: Record<string, unknown>, key: unknown) {
    const record = typeof key === 'string' && Object.hasOwn(records, key) ? records[key] : undefined;
    if (!isRecord(record)) throw new Error('Mock JSON snapshot havolasi topilmadi.');
    return structuredClone({ ...defaults, ...record });
  }
  const orders = value.orders.map(row => {
    if (!isRecord(row)) throw new Error('Mock buyurtma formati mos emas.');
    const { estimateId, confirmedEstimateId, contractId, ...fields } = { ...orderDefaults, ...row };
    return {
      ...structuredClone(fields), estimate: snapshot(estimates, estimateDefaults, estimateId),
      confirmedEstimate: confirmedEstimateId === null ? null : snapshot(estimates, estimateDefaults, confirmedEstimateId),
      contract: snapshot(contracts, contractDefaults, contractId),
    };
  });
  const { orderDefaults: _orders, estimateDefaults: _estimates, contractDefaults: _contracts, estimates: _versions, contracts: _documents, ...collections } = value;
  return parseDatabase({ ...structuredClone(collections), orders });
}
