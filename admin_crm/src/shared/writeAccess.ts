import { createContext, useContext } from 'react';

export const WriteAccessContext = createContext(false);
export const useCanWrite = () => useContext(WriteAccessContext);
