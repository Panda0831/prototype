import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://192.168.155.6:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Expires": "0",
  },
});

// Intercepteur pour ajouter le token JWT dans les headers
api.interceptors.request.use((config) => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    const user = JSON.parse(userStr);
    if (user.access_token) {
      config.headers['Authorization'] = `Bearer ${user.access_token}`;
    }
    if (user.public_key) {
      config.headers['public-key'] = user.public_key;
      // Log for debugging (I will check browser console)
      console.log("[DEBUG] Sending request with public-key:", user.public_key);
    }
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Intercepteur pour gérer les erreurs de session (401) et loguer les réponses
api.interceptors.response.use((response) => {
  console.log("[DEBUG] Response from", response.config.url, ":", response.data);
  return response;
}, (error) => {
  if (error.response && error.response.status === 401) {
    console.error("Session expirée ou invalide");
    localStorage.removeItem('user');
    window.location.href = '/auth';
  }
  return Promise.reject(error);
});

export const authService = {
  signIn: async (credentials: any) => {
    const response = await api.post("/api/auth/signin", credentials);
    return response.data;
  },
  signUp: async (userData: any) => {
    const response = await api.post("/api/auth/signup", userData);
    return response.data;
  },
  getUsers: async () => {
    const response = await api.get("/api/auth/users");
    return response.data;
  },
};

export const blockchainService = {
  getStatus: async () => {
    const response = await api.get("/api/blockchain/");
    return response.data;
  },
  getBlocks: async () => {
    const response = await api.get("/api/blockchain/blocks");
    return response.data;
  },
  getBrainInfo: async () => {
    const response = await api.get("/api/blockchain/brain-info");
    return response.data;
  },
  mine: async (publicKey: string) => {
    const response = await api.post("/api/blockchain/mine", {}, {
      headers: { 'public_key': publicKey }
    });
    return response.data;
  },
  getPendingTransactions: async () => {
    const response = await api.get("/api/blockchain/pending-transactions");
    return response.data;
  },
  getBalance: async (publicKey: string) => {
    const response = await api.get(`/api/blockchain/balance/${publicKey}`);
    return response.data;
  },
  getBalanceHistory: async (publicKey: string) => {
    const response = await api.get(`/api/blockchain/balance/history/${publicKey}`);
    return response.data;
  },
};

export const algoService = {
  getDistricts: async () => {
    const response = await api.get("/api/algo/districts");
    return response.data;
  },
  findPath: async (startId: number, endId: number) => {
    const response = await api.post("/api/algo/path", { start_id: startId, end_id: endId });
    return response.data;
  },
  selectValidator: async (currentDistrictId: number) => {
    const response = await api.post("/api/algo/select-validator", { current_district_id: currentDistrictId });
    return response.data;
  },
};
export const notificationService = {
  getNotifications: async (publicKey: string) => {
    const response = await api.get(`/api/notifications/${publicKey}`);
    return response.data;
  },
};

export const agriService = {
  recordHarvest: async (harvestData: any) => {
    const response = await api.post("/api/agriculture/harvest", harvestData);
    return response.data;
  },
  sellLot: async (lotData: { lot_id: string; buyer_id: string; price: number; seller_id: string }) => {
    const response = await api.post("/api/agriculture/sell", lotData);
    return response.data;
  },
  acceptSale: async (saleOfferId: string) => {
    const response = await api.post(`/api/agriculture/accept-sale/${saleOfferId}`);
    return response.data;
  },
  optimizeTransport: async (transportData: { lot_id: string; destination: string }) => {
    const response = await api.post("/api/agriculture/transport", transportData);
    return response.data;
  },
  getLot: async (lotId: string) => {
    const response = await api.get(`/api/agriculture/lot/${lotId}`);
    return response.data;
  },
  getAllLots: async () => {
    const response = await api.get("/api/agriculture/all");
    return response.data;
  },
  inspectVanilla: async (data: any) => {
    const response = await api.post("/api/agriculture/vanilla/inspect", data);
    return response.data;
  },
  sealVanillaPassport: async (data: any) => {
    const response = await api.post("/api/agriculture/vanilla/seal", data);
    return response.data;
  },
  getVanillaDashboardData: async () => {
    const response = await api.get("/api/agriculture/vanilla/dashboard-data");
    return response.data;
  },
  getVanillaModelInfo: async () => {
    const response = await api.get("/api/agriculture/vanilla/model-info");
    return response.data;
  },
  getVanillaPassport: async (passportHash: string) => {
    const response = await api.get(`/api/agriculture/vanilla/passport/${passportHash}`);
    return response.data;
  },
};

export default api;
