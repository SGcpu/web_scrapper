// Type definitions for Review Radar frontend

export interface Product {
  id: number;
  name: string;
  url: string;
  category?: string;
  platform: string;
  image_url?: string;
  price?: string;
  rating?: string;
  total_reviews: number;
  last_scraped?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  product_id: number;
  text: string;
  rating?: number;
  reviewer_name?: string;
  review_date?: string;
  verified_purchase: boolean;
  helpful_votes: number;
  total_votes: number;
  source_url?: string;
  review_id_on_site?: string;
  is_processed: boolean;
  created_at: string;
  updated_at: string;
}

export interface SentimentResult {
  label: string;
  score: number;
  distribution: {
    POSITIVE: number;
    NEGATIVE: number;
    NEUTRAL: number;
  };
}

export interface AspectSentiment {
  aspect: string;
  sentiment: string;
  score: number;
  mentions: number;
}

export interface TopicResult {
  topic_id: number;
  label: string;
  keywords: string[];
  probability: number;
  review_count: number;
}

export interface AnalysisResult {
  product_id: number;
  total_reviews: number;
  sentiment: SentimentResult;
  aspects: AspectSentiment[];
  topics: TopicResult[];
  keywords: string[];
  trust_score: number;
  processing_time: number;
}

export interface ScrapeRequest {
  url: string;
  max_reviews?: number;
  platform?: string;
}

export interface ScrapeResponse {
  session_id: string;
  product_id: number;
  status: string;
  message: string;
}

export interface ScrapeStatus {
  session_id: string;
  status: string;
  progress: Record<string, number | string | boolean>;
  total_reviews_found: number;
  reviews_scraped: number;
  reviews_failed: number;
  error_message?: string;
}

export interface AnalysisRequest {
  product_id?: number;
  url?: string;
  reviews?: string[];
}

export interface AnalysisResponse {
  session_id: string;
  status: string;
  result?: AnalysisResult;
  message: string;
}

export interface ProductSummary {
  id: number;
  name: string;
  url: string;
  platform: string;
  total_reviews: number;
  avg_rating?: number;
  sentiment_score?: number;
  last_analyzed?: string;
}

export interface DashboardSummary {
  total_products: number;
  total_reviews: number;
  avg_sentiment: number;
  recent_analyses: number;
  sentiment_distribution?: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

// Loading states
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

// Form data types
export interface UrlAnalysisForm {
  url: string;
  maxReviews: number;
  platform?: string;
}

// Chart data types
export interface ChartDataPoint {
  name: string;
  value: number;
  fill?: string;
}

export interface SentimentTrendPoint {
  date: string;
  sentiment: number;
  reviews: number;
}