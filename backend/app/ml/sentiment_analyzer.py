"""Sentiment analysis module using Hugging Face transformers."""

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any, Tuple
import logging
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Sentiment analysis using pre-trained transformers."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.SENTIMENT_MODEL
        self._pipeline = None
        self._tokenizer = None
        self._model = None
    
    @property
    def pipeline(self):
        """Lazy loading of sentiment analysis pipeline."""
        if self._pipeline is None:
            try:
                self._pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1,
                    truncation=True,
                    max_length=512
                )
                logger.info(f"Loaded sentiment analysis model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load sentiment model: {e}")
                # Fallback to a smaller model
                self._pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=-1,
                    truncation=True,
                    max_length=512
                )
        return self._pipeline
    
    def analyze_single(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text."""
        if not text or not text.strip():
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "confidence": "low"
            }
        
        try:
            # Truncate text if too long
            text = text[:1000]  # Keep within reasonable limits
            
            result = self.pipeline(text)[0]
            
            # Normalize labels to standard format
            label = self._normalize_label(result['label'])
            score = result['score']
            
            # Determine confidence level
            confidence = self._get_confidence_level(score)
            
            return {
                "label": label,
                "score": score,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "confidence": "error"
            }
    
    def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts in batches."""
        results = []
        
        # Process in batches for better performance
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Filter and prepare batch
            valid_batch = []
            indices = []
            
            for j, text in enumerate(batch):
                if text and text.strip():
                    valid_batch.append(text[:1000])  # Truncate
                    indices.append(i + j)
                else:
                    results.append({
                        "label": "NEUTRAL",
                        "score": 0.5,
                        "confidence": "low"
                    })
            
            if valid_batch:
                try:
                    batch_results = self.pipeline(valid_batch)
                    
                    for result in batch_results:
                        label = self._normalize_label(result['label'])
                        score = result['score']
                        confidence = self._get_confidence_level(score)
                        
                        results.append({
                            "label": label,
                            "score": score,
                            "confidence": confidence
                        })
                        
                except Exception as e:
                    logger.error(f"Error in batch sentiment analysis: {e}")
                    # Add neutral results for failed batch
                    for _ in valid_batch:
                        results.append({
                            "label": "NEUTRAL",
                            "score": 0.5,
                            "confidence": "error"
                        })
        
        return results
    
    def get_sentiment_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sentiment distribution from analysis results."""
        if not results:
            return {"POSITIVE": 0.0, "NEGATIVE": 0.0, "NEUTRAL": 0.0}
        
        counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
        
        for result in results:
            label = result.get("label", "NEUTRAL")
            counts[label] = counts.get(label, 0) + 1
        
        total = len(results)
        return {
            label: count / total for label, count in counts.items()
        }
    
    def get_average_sentiment_score(self, results: List[Dict[str, Any]]) -> float:
        """Calculate average sentiment score."""
        if not results:
            return 0.5
        
        total_score = 0.0
        count = 0
        
        for result in results:
            label = result.get("label", "NEUTRAL")
            score = result.get("score", 0.5)
            
            # Convert to positive/negative scale (-1 to 1)
            if label == "POSITIVE":
                normalized_score = score
            elif label == "NEGATIVE":
                normalized_score = -score
            else:  # NEUTRAL
                normalized_score = 0.0
            
            total_score += normalized_score
            count += 1
        
        # Return average score normalized to 0-1 scale
        avg_score = total_score / count
        return (avg_score + 1) / 2  # Convert from -1,1 to 0,1
    
    @staticmethod
    def _normalize_label(label: str) -> str:
        """Normalize sentiment labels to standard format."""
        label = label.upper()
        
        # Handle various label formats
        if label in ["POSITIVE", "POS", "1"]:
            return "POSITIVE"
        elif label in ["NEGATIVE", "NEG", "0"]:
            return "NEGATIVE"
        else:
            return "NEUTRAL"
    
    @staticmethod
    def _get_confidence_level(score: float) -> str:
        """Determine confidence level based on score."""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"


# Global sentiment analyzer instance
@lru_cache(maxsize=1)
def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get cached sentiment analyzer instance."""
    return SentimentAnalyzer()