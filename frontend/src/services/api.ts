// API service layer for communicating with the Review Radar backend

import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type {
  Product,
  ProductSummary,
  ScrapeRequest,
  ScrapeResponse,
  ScrapeStatus,
  AnalysisRequest,
  AnalysisResponse,
  AnalysisResult,
  DashboardSummary,
} from '../types/index.ts';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: unknown): Error {
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response: { status: number; data?: { detail?: string; message?: string } } };
      const message = axiosError.response.data?.detail || axiosError.response.data?.message || `HTTP ${axiosError.response.status}`;
      return new Error(message);
    } else if (error && typeof error === 'object' && 'request' in error) {
      // Request was made but no response received
      return new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      const message = error instanceof Error ? error.message : 'An unexpected error occurred';
      return new Error(message);
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Scraping endpoints
  async startScraping(request: ScrapeRequest): Promise<ScrapeResponse> {
    const response = await this.api.post('/api/scrape/', request);
    return response.data;
  }

  async getScrapingStatus(sessionId: string): Promise<ScrapeStatus> {
    const response = await this.api.get(`/api/scrape/status/${sessionId}`);
    return response.data;
  }

  async getAllScrapingSessions(): Promise<ScrapeStatus[]> {
    const response = await this.api.get('/api/scrape/sessions');
    return response.data;
  }

  // Analysis endpoints
  async startAnalysis(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await this.api.post('/api/analyze/', request);
    return response.data;
  }

  async getAnalysisStatus(sessionId: string): Promise<AnalysisResponse> {
    const response = await this.api.get(`/api/analyze/status/${sessionId}`);
    return response.data;
  }

  async getAnalysisResults(productId: number): Promise<AnalysisResult> {
    const response = await this.api.get(`/api/analyze/results/${productId}`);
    return response.data;
  }

  async getAllAnalysisSessions(): Promise<{ sessions: AnalysisResult[]; total: number }> {
    const response = await this.api.get('/api/analyze/sessions');
    return response.data;
  }

  // Product endpoints
  async getProducts(params?: {
    skip?: number;
    limit?: number;
    platform?: string;
    category?: string;
  }): Promise<ProductSummary[]> {
    const response = await this.api.get('/api/products/', { params });
    return response.data;
  }

  async getProduct(productId: number): Promise<Product> {
    const response = await this.api.get(`/api/products/${productId}`);
    return response.data;
  }

  async createProduct(product: Omit<Product, 'id' | 'total_reviews' | 'last_scraped' | 'is_active' | 'created_at' | 'updated_at'>): Promise<Product> {
    const response = await this.api.post('/api/products/', product);
    return response.data;
  }

  async updateProduct(productId: number, updates: Partial<Product>): Promise<Product> {
    const response = await this.api.put(`/api/products/${productId}`, updates);
    return response.data;
  }

  async deleteProduct(productId: number): Promise<{ message: string }> {
    const response = await this.api.delete(`/api/products/${productId}`);
    return response.data;
  }

  async getProductReviews(productId: number, params?: { skip?: number; limit?: number }) {
    const response = await this.api.get(`/api/products/${productId}/reviews`, { params });
    return response.data;
  }

  async getProductStats(productId: number) {
    const response = await this.api.get(`/api/products/${productId}/stats`);
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardSummary(): Promise<DashboardSummary> {
    try {
      const response = await this.api.get('/api/dashboard/summary');
      return response.data || {
        total_products: 0,
        total_reviews: 0,
        avg_sentiment: 0.5,
        recent_analyses: 0,
        sentiment_distribution: {
          positive: 0.5,
          negative: 0.3,
          neutral: 0.2
        }
      };
    } catch (error) {
      console.error("Error fetching dashboard summary:", error);
      // Return default values if fetch fails
      return {
        total_products: 0,
        total_reviews: 0,
        avg_sentiment: 0.5,
        recent_analyses: 0,
        sentiment_distribution: {
          positive: 0.5,
          negative: 0.3,
          neutral: 0.2
        }
      };
    }
  }

  async getRecentProducts(limit: number = 10): Promise<ProductSummary[]> {
    try {
      const response = await this.api.get('/api/dashboard/recent-products', { params: { limit } });
      return response.data || [];
    } catch (error) {
      console.error("Error fetching recent products:", error);
      return []; // Return empty array on error
    }
  }

  async getPlatformStats(): Promise<{ platform_statistics: Record<string, number> }> {
    const response = await this.api.get('/api/dashboard/platform-stats');
    return response.data;
  }

  async getSentimentTrends(days: number = 30): Promise<{ sentiment_trends: Array<{ date: string; positive: number; negative: number; neutral: number }>; period_days: number }> {
    const response = await this.api.get('/api/dashboard/sentiment-trends', { params: { days } });
    return response.data;
  }

  async getTopKeywords(limit: number = 20): Promise<{ top_keywords: Array<{ keyword: string; count: number; sentiment_score: number }> }> {
    const response = await this.api.get('/api/dashboard/top-keywords', { params: { limit } });
    return response.data;
  }

  async getScrapingActivity(days: number = 7): Promise<{
    period_days: number;
    activity_stats: Record<string, number>;
    total_reviews_scraped: number;
    recent_sessions: Array<{ id: string; product_name: string; status: string; created_at: string }>;
  }> {
    const response = await this.api.get('/api/dashboard/scraping-activity', { params: { days } });
    return response.data;
  }

  // Utility methods
  async pollStatus<T>(
    getStatusFn: () => Promise<T>,
    isCompleteFn: (status: T) => boolean,
    interval: number = 2000,
    maxAttempts: number = 150 // 5 minutes with 2s intervals
  ): Promise<T> {
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++;
          const status = await getStatusFn();
          
          if (isCompleteFn(status)) {
            resolve(status);
          } else if (attempts >= maxAttempts) {
            reject(new Error('Polling timeout reached'));
          } else {
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };
      
      poll();
    });
  }
}

// Create and export singleton instance
export const apiService = new ApiService();
export default apiService;