// Utility functions for the Review Radar frontend

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return 'Invalid Date';
  }
};

export const formatRelativeTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    if (diffInDays < 7) return `${diffInDays} days ago`;
    
    return formatDate(dateString);
  } catch {
    return 'Unknown time';
  }
};

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const getSentimentColor = (sentiment: string | number): string => {
  if (typeof sentiment === 'string') {
    switch (sentiment.toUpperCase()) {
      case 'POSITIVE':
        return '#10B981'; // green
      case 'NEGATIVE':
        return '#EF4444'; // red
      case 'NEUTRAL':
      default:
        return '#6B7280'; // gray
    }
  } else {
    // Numeric sentiment score (0-1)
    if (sentiment > 0.6) return '#10B981'; // green
    if (sentiment < 0.4) return '#EF4444'; // red
    return '#F59E0B'; // yellow/amber
  }
};

export const getSentimentLabel = (score: number): string => {
  if (score > 0.6) return 'Positive';
  if (score < 0.4) return 'Negative';
  return 'Neutral';
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const isValidUrl = (string: string): boolean => {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
};

export const extractDomain = (url: string): string => {
  try {
    const domain = new URL(url).hostname;
    return domain.replace('www.', '');
  } catch {
    return 'Unknown';
  }
};

export const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const debounce = <T extends (...args: unknown[]) => void>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: number;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = window.setTimeout(() => func(...args), wait);
  };
};

export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Platform detection
export const getPlatformIcon = (platform: string): string => {
  switch (platform.toLowerCase()) {
    case 'amazon':
      return '🛒';
    case 'ebay':
      return '🏪';
    case 'walmart':
      return '🏬';
    case 'target':
      return '🎯';
    case 'bestbuy':
      return '💻';
    case 'etsy':
      return '🎨';
    default:
      return '🌐';
  }
};

// Status helpers
export const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'completed':
    case 'success':
      return '#10B981'; // green
    case 'failed':
    case 'error':
      return '#EF4444'; // red
    case 'running':
    case 'processing':
      return '#F59E0B'; // amber
    case 'pending':
    case 'waiting':
      return '#6B7280'; // gray
    default:
      return '#6B7280';
  }
};

export const getStatusIcon = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'completed':
    case 'success':
      return '✅';
    case 'failed':
    case 'error':
      return '❌';
    case 'running':
    case 'processing':
      return '⏳';
    case 'pending':
    case 'waiting':
      return '⏸️';
    default:
      return '❓';
  }
};