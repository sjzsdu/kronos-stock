import os
import sys
import warnings
from typing import Optional, Dict, Any, Tuple
from flask import current_app

warnings.filterwarnings('ignore')

class ModelService:
    """AI model management service"""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None 
        self.predictor = None
        self._setup_paths()
        self._model_available = self._check_model_availability()
    
    def _setup_paths(self):
        """Setup model import paths"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        embedded_model_dir = os.path.join(root_dir, 'model')
        if os.path.isdir(embedded_model_dir) and embedded_model_dir not in sys.path:
            sys.path.insert(0, embedded_model_dir)
            
        if root_dir not in sys.path:
            sys.path.append(root_dir)
    
    def _check_model_availability(self) -> bool:
        """Check if model code is available"""
        try:
            from model import Kronos, KronosTokenizer, KronosPredictor
            return True
        except Exception as e:
            current_app.logger.error(f"Model import error: {e}")
            return False
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        return current_app.config['AVAILABLE_MODELS']
    
    def load_model(self, model_name: str) -> Tuple[bool, str]:
        """Load specified model"""
        if not self._model_available:
            return False, "Model code not available"
        
        try:
            from model import Kronos, KronosTokenizer, KronosPredictor
            
            models_config = self.get_available_models()
            if model_name not in models_config:
                return False, f"Model {model_name} not found"
            
            model_path = os.path.join(current_app.config['MODEL_DIR'], model_name)
            if not os.path.exists(model_path):
                return False, f"Model path {model_path} does not exist"
            
            # Load tokenizer and model with CPU device
            import torch
            device = torch.device('cpu')  # Force CPU usage
            
            self.tokenizer = KronosTokenizer.from_pretrained(model_path)
            self.model = Kronos.from_pretrained(model_path)
            
            # Move model to CPU
            self.model = self.model.to(device)
            self.model.eval()  # Set to evaluation mode
            
            # Create predictor with CPU device
            self.predictor = KronosPredictor(self.model, self.tokenizer, device="cpu")
            
            current_app.logger.info(f"Successfully loaded model: {model_name}")
            return True, f"Model {model_name} loaded successfully"
            
        except Exception as e:
            error_msg = f"Failed to load model {model_name}: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return all([self.tokenizer, self.model, self.predictor])
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status"""
        return {
            'available': self._model_available,
            'loaded': self.is_model_loaded(),
            'models': self.get_available_models()
        }
    
    def unload_model(self):
        """Unload current model to free memory"""
        self.tokenizer = None
        self.model = None
        self.predictor = None

# Global model service instance
model_service = ModelService()