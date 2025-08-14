"""Factory for creating OCR engines."""

from typing import Dict, Type
from pathlib import Path

from .base import LabelEngine
from .openai_engine import OpenAIEngine


class EngineFactory:
    """Factory for creating and managing OCR engines."""
    
    def __init__(self):
        self._engines: Dict[str, Type[LabelEngine]] = {}
        self._instances: Dict[str, LabelEngine] = {}
        self._register_default_engines()
    
    def _register_default_engines(self) -> None:
        """Register default engine types."""
        self.register_engine("openai", OpenAIEngine)
    
    def register_engine(self, name: str, engine_class: Type[LabelEngine]) -> None:
        """Register a new engine type."""
        if not issubclass(engine_class, LabelEngine):
            raise ValueError(f"Engine class must inherit from LabelEngine")
        
        self._engines[name] = engine_class
        print(f"✅ Registered engine: {name}")
    
    def get_engine(self, name: str) -> LabelEngine:
        """Get or create an engine instance."""
        if name not in self._engines:
            available = ", ".join(self._engines.keys())
            raise ValueError(f"Unknown engine '{name}'. Available: {available}")
        
        # Return cached instance if exists
        if name in self._instances:
            return self._instances[name]
        
        # Create new instance
        engine_class = self._engines[name]
        engine_instance = engine_class()
        self._instances[name] = engine_instance
        
        return engine_instance
    
    def list_available_engines(self) -> Dict[str, str]:
        """List all available engine types."""
        return {
            name: engine_class.__name__
            for name, engine_class in self._engines.items()
        }
    
    def get_engine_info(self, name: str) -> Dict:
        """Get detailed information about an engine."""
        if name not in self._engines:
            return {"error": f"Engine '{name}' not found"}
        
        engine_class = self._engines[name]
        return {
            "name": name,
            "class_name": engine_class.__name__,
            "module": engine_class.__module__,
            "docstring": engine_class.__doc__ or "No documentation available",
            "methods": [method for method in dir(engine_class) if not method.startswith("_")]
        }
    
    def test_engine(self, name: str, test_image_path: Path) -> Dict:
        """Test an engine with a test image."""
        try:
            engine = self.get_engine(name)
            
            # Test basic functionality
            test_result = {
                "engine_name": name,
                "status": "success",
                "tests": {}
            }
            
            # Test message building
            try:
                messages = engine.build_messages(test_image_path)
                test_result["tests"]["build_messages"] = {
                    "status": "success",
                    "message_count": len(messages)
                }
            except Exception as e:
                test_result["tests"]["build_messages"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Test label generation (if test image exists)
            if test_image_path.exists():
                try:
                    label = engine.generate_label(test_image_path)
                    test_result["tests"]["generate_label"] = {
                        "status": "success",
                        "label_keys": list(label.keys()) if isinstance(label, dict) else []
                    }
                except Exception as e:
                    test_result["tests"]["generate_label"] = {
                        "status": "failed",
                        "error": str(e)
                    }
            else:
                test_result["tests"]["generate_label"] = {
                    "status": "skipped",
                    "reason": "Test image does not exist"
                }
            
            return test_result
            
        except Exception as e:
            return {
                "engine_name": name,
                "status": "failed",
                "error": str(e)
            }
    
    def cleanup(self) -> None:
        """Clean up engine instances."""
        self._instances.clear()


# Global factory instance
_engine_factory = EngineFactory()


def get_engine(name: str) -> LabelEngine:
    """Get an engine instance using the global factory."""
    return _engine_factory.get_engine(name)


def register_engine(name: str, engine_class: Type[LabelEngine]) -> None:
    """Register a new engine type using the global factory."""
    _engine_factory.register_engine(name, engine_class)


def list_engines() -> Dict[str, str]:
    """List available engines using the global factory."""
    return _engine_factory.list_available_engines()
