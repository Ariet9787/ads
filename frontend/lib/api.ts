import axios from "axios";
import Cookies from "js-cookie";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = Cookies.get("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  phone: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AdImage {
  id: number;
  url: string;
  order: number;
}

export interface Ad {
  id: number;
  title: string;
  description: string;
  price: number;
  category_id: number;
  user_id: number;
  images: AdImage[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedAdsResponse {
  items: Ad[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const authAPI = {
  login: async (data: LoginData): Promise<TokenResponse> => {
    const response = await api.post("/auth/login", data);
    return response.data;
  },

  register: async (data: RegisterData): Promise<TokenResponse> => {
    const response = await api.post("/auth/register", data);
    return response.data;
  },
};

export const adsAPI = {
  getMyAds: async (
    page: number = 1,
    size: number = 10,
  ): Promise<PaginatedAdsResponse> => {
    const response = await api.get("/ads/my", { params: { page, size } });
    return response.data;
  },
  deleteAd: async (adId: number): Promise<void> => {
    await api.delete(`/ads/${adId}`);
  },
};
