import { readFileSync } from 'node:fs';
import type { Database } from '../domain/types';
import { parseMockDatabase } from './mock';

// Node-only fixture helper. Application code never imports this module.
const database: unknown = JSON.parse(readFileSync(new URL('../../public/mock/database.json', import.meta.url), 'utf8').replace(/^\uFEFF/, ''));
export const mockFixture = () => structuredClone(database);

// Tests use the same static JSON that the browser fetches.
export function createSeed(): Database {
  return parseMockDatabase(database);
}
