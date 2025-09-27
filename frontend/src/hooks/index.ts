// Custom hooks for Review Radar frontend

import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api.ts';
import type { 
  ProductSummary, 
  DashboardSummary, 
  ScrapeStatus, 
  AnalysisResponse,
  LoadingState 
} from '../types/index.ts';

// Hook for managing loading states
export const useLoadingState = (initialLoading: boolean = false) => {
  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: initialLoading,
    error: undefined,
  });

  const setLoading = useCallback((isLoading: boolean) => {
    setLoadingState(prev => ({ ...prev, isLoading, error: undefined }));
  }, []);

  const setError = useCallback((error: string) => {
    setLoadingState({ isLoading: false, error });
  }, []);

  const clearError = useCallback(() => {
    setLoadingState(prev => ({ ...prev, error: undefined }));
  }, []);

  return {
    ...loadingState,
    setLoading,
    setError,
    clearError,
  };
};

// Hook for fetching dashboard data
export const useDashboard = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentProducts, setRecentProducts] = useState<ProductSummary[]>([]);
  const { isLoading, error, setLoading, setError } = useLoadingState(true);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [summaryData, productsData] = await Promise.all([
        apiService.getDashboardSummary(),
        apiService.getRecentProducts(10),
      ]);
      
      setSummary(summaryData);
      setRecentProducts(productsData);
      setLoading(false); // Set loading to false after successful fetch
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    }
  }, [setLoading, setError]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return {
    summary,
    recentProducts,
    isLoading,
    error,
    refresh: fetchDashboardData,
  };
};

// Hook for managing product list
export const useProducts = (initialParams?: {
  skip?: number;
  limit?: number;
  platform?: string;
  category?: string;
}) => {
  const [products, setProducts] = useState<ProductSummary[]>([]);
  const [params, setParams] = useState(initialParams || {});
  const { isLoading, error, setLoading, setError } = useLoadingState();

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getProducts(params);
      setProducts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch products');
    }
  }, [params, setLoading, setError]);

  const updateParams = useCallback((newParams: typeof params) => {
    setParams(prev => ({ ...prev, ...newParams }));
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  return {
    products,
    isLoading,
    error,
    params,
    updateParams,
    refresh: fetchProducts,
  };
};

// Hook for polling operation status
export const usePolling = <T>(
  pollFn: () => Promise<T>,
  isComplete: (data: T) => boolean,
  interval: number = 2000,
  enabled: boolean = true
) => {
  const [data, setData] = useState<T | null>(null);
  const { isLoading, error, setLoading, setError } = useLoadingState();

  useEffect(() => {
    if (!enabled) return;

    let intervalId: number | undefined;
    let cancelled = false;

    const poll = async () => {
      try {
        if (cancelled) return;
        
        setLoading(true);
        const result = await pollFn();
        
        if (cancelled) return;
        
        setData(result);
        
        if (isComplete(result)) {
          setLoading(false);
          if (intervalId) clearInterval(intervalId);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Polling failed');
        if (intervalId) clearInterval(intervalId);
      }
    };

    // Initial poll
    poll();

    // Set up interval if not complete
    if (data && !isComplete(data)) {
      intervalId = window.setInterval(poll, interval);
    }

    // Cleanup
    return () => {
      cancelled = true;
      if (intervalId) clearInterval(intervalId);
    };
  }, [pollFn, isComplete, interval, enabled, data, setLoading, setError]);

  return { data, isLoading, error };
};

// Hook for scraping operations
export const useScraping = () => {
  const [sessions, setSessions] = useState<ScrapeStatus[]>([]);
  const { isLoading, error, setLoading, setError } = useLoadingState();

  const startScraping = useCallback(async (url: string, maxReviews: number = 100) => {
    try {
      setLoading(true);
      const response = await apiService.startScraping({ url, max_reviews: maxReviews });
      
      // Add the new session to the list
      const newSession: ScrapeStatus = {
        session_id: response.session_id,
        status: 'pending',
        progress: {},
        total_reviews_found: 0,
        reviews_scraped: 0,
        reviews_failed: 0,
      };
      
      setSessions(prev => [newSession, ...prev]);
      setLoading(false);
      
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scraping');
      throw err;
    }
  }, [setLoading, setError]);

  const getSessionStatus = useCallback(async (sessionId: string) => {
    try {
      const status = await apiService.getScrapingStatus(sessionId);
      
      // Update the session in the list
      setSessions(prev => 
        prev.map(session => 
          session.session_id === sessionId ? status : session
        )
      );
      
      return status;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get session status');
      throw err;
    }
  }, [setError]);

  const refreshSessions = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getAllScrapingSessions();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
    }
  }, [setLoading, setError]);

  return {
    sessions,
    isLoading,
    error,
    startScraping,
    getSessionStatus,
    refreshSessions,
  };
};

// Hook for analysis operations
export const useAnalysis = () => {
  const [sessions, setSessions] = useState<AnalysisResponse[]>([]);
  const { isLoading, error, setLoading, setError } = useLoadingState();

  const startAnalysis = useCallback(async (productId: number) => {
    try {
      setLoading(true);
      const response = await apiService.startAnalysis({ product_id: productId });
      
      setSessions(prev => [response, ...prev]);
      setLoading(false);
      
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis');
      throw err;
    }
  }, [setLoading, setError]);

  const getAnalysisStatus = useCallback(async (sessionId: string) => {
    try {
      const status = await apiService.getAnalysisStatus(sessionId);
      
      setSessions(prev => 
        prev.map(session => 
          session.session_id === sessionId ? status : session
        )
      );
      
      return status;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get analysis status');
      throw err;
    }
  }, [setError]);

  return {
    sessions,
    isLoading,
    error,
    startAnalysis,
    getAnalysisStatus,
  };
};

// Hook for API health check
export const useApiHealth = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const { isLoading, setLoading } = useLoadingState();

  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      await apiService.healthCheck();
      setIsHealthy(true);
    } catch {
      setIsHealthy(false);
    } finally {
      setLoading(false);
    }
  }, [setLoading]);

  useEffect(() => {
    checkHealth();
    
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    isHealthy,
    isLoading,
    checkHealth,
  };
};