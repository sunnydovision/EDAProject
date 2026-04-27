"""
Singleton for SentenceTransformer model to avoid repeated loading.
"""

from sentence_transformers import SentenceTransformer

_model_instance = None
_model_name = 'all-MiniLM-L6-v2'


def get_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    """
    Get or create a singleton instance of the SentenceTransformer model.
    
    Args:
        model_name: Name of the model to load (default: 'all-MiniLM-L6-v2')
    
    Returns:
        SentenceTransformer model instance
    """
    global _model_instance, _model_name
    
    if _model_instance is None or _model_name != model_name:
        _model_instance = SentenceTransformer(model_name)
        _model_name = model_name
    
    return _model_instance


def reset_model():
    """Reset the singleton model instance (for testing)."""
    global _model_instance
    _model_instance = None
