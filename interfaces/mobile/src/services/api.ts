import axios from 'axios';
import { Platform } from 'react-native';

// Adresse IP de la machine hôte pour le développement mobile (wlan0: 192.168.88.22)
const API_URL = Platform.OS === 'web' ? 'http://localhost:8000' : 'http://192.168.88.22:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authService = {
  signIn: async (credentials: any) => {
    const response = await api.post('/api/auth/signin', credentials);
    return response.data;
  },
  signUp: async (userData: any) => {
    const response = await api.post('/api/auth/signup', userData);
    return response.data;
  },
  getUsers: async () => {
    const response = await api.get('/api/auth/users');
    return response.data;
  },
};

export const blockchainService = {
  getStatus: async () => {
    const response = await api.get('/api/blockchain/');
    return response.data;
  },
  getBlocks: async () => {
    const response = await api.get('/api/blockchain/blocks');
    return response.data;
  },
  mine: async (publicKey: string) => {
    const response = await api.post('/api/blockchain/mine', {}, {
      headers: { 'public_key': publicKey }
    });
    return response.data;
  },
  getPendingTransactions: async () => {
    const response = await api.get('/api/blockchain/pending-transactions');
    return response.data;
  },
  getBalance: async (publicKey: string) => {
    const response = await api.get(`/api/blockchain/balance/${encodeURIComponent(publicKey)}`);
    return response.data;
  },
  getBalanceHistory: async (publicKey: string) => {
    const response = await api.get(`/api/blockchain/balance/history/${encodeURIComponent(publicKey)}`);
    return response.data;
  },
};

export const algoService = {
  getDistricts: async () => {
    const response = await api.get('/api/algo/districts');
    return response.data;
  },
  findPath: async (startId: number, endId: number) => {
    const response = await api.post('/api/algo/path', { start_id: startId, end_id: endId });
    return response.data;
  },
  selectValidator: async (currentDistrictId: number) => {
    const response = await api.post('/api/algo/select-validator', { current_district_id: currentDistrictId });
    return response.data;
  },
};

export const agriService = {
  recordHarvest: async (harvestData: any) => {
    const response = await api.post('/api/agriculture/harvest', harvestData);
    return response.data;
  },
  optimizeTransport: async (transportData: { lot_id: string; destination: string }) => {
    const response = await api.post('/api/agriculture/transport', transportData);
    return response.data;
  },
  getLot: async (lotId: string) => {
    const response = await api.get(`/api/agriculture/lot/${lotId}`);
    return response.data;
  },
  getAllLots: async () => {
    const response = await api.get('/api/agriculture/all');
    return response.data;
  },
  sellLot: async (lotData: { lot_id: string; buyer_id: string; price: number; seller_id: string }) => {
    const response = await api.post('/api/agriculture/sell', lotData, {
      headers: { 'public-key': lotData.seller_id }
    });
    return response.data;
  },
  inspectVanilla: async (data: any) => {
    const response = await api.post('/api/agriculture/vanilla/inspect', data);
    return response.data;
  },
  sealVanillaPassport: async (data: any) => {
    const response = await api.post('/api/agriculture/vanilla/seal', data);
    return response.data;
  },
  getVanillaDashboardData: async () => {
    const response = await api.get('/api/agriculture/vanilla/dashboard-data');
    return response.data;
  },
  getVanillaModelInfo: async () => {
    const response = await api.get('/api/agriculture/vanilla/model-info');
    return response.data;
  },
};


export default api;
