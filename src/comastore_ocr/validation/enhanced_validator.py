"""Enhanced validation module with better organization and extensibility."""
import math

from typing import Tuple, List, Optional, Any, Dict
from .validation_rule import ValidationRule
from .validation_result import ValidationResult

class LabelValidator:
    """Enhanced validator for label objects."""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        # Basic structure rules
        self.add_rule(ValidationRule(
            name="structure_check",
            validator=self._validate_structure,
            description="Check if object has correct structure"
        ))
        
        # Field type rules
        self.add_rule(ValidationRule(
            name="field_types",
            validator=self._validate_field_types,
            description="Validate field types"
        ))
        
        # Promo code rules
        self.add_rule(ValidationRule(
            name="promo_code",
            validator=self._validate_promo_code,
            description="Validate promotion code"
        ))
        
        # Core field rules
        self.add_rule(ValidationRule(
            name="core_field",
            validator=self._validate_core_field,
            description="Validate core field based on promo"
        ))
        
        # Cross-field rules
        self.add_rule(ValidationRule(
            name="cross_field_validation",
            validator=self._validate_cross_fields,
            description="Validate cross-field relationships"
        ))
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a new validation rule."""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_count
    
    def validate(self, obj: Any) -> Tuple[bool, List[ValidationResult]]:
        """Validate an object using all rules."""
        results = []
        
        for rule in self.rules:
            try:
                is_valid, message, details = rule.validator(obj)
                result = ValidationResult(
                    is_valid=is_valid,
                    message=message,
                    rule_name=rule.name,
                    severity=rule.severity,
                    details=details
                )
                results.append(result)
            except Exception as e:
                # Rule execution failed
                result = ValidationResult(
                    is_valid=False,
                    message=f"Rule execution failed: {e}",
                    rule_name=rule.name,
                    severity="error",
                    details={"exception": str(e)}
                )
                results.append(result)
        
        # Overall validation result
        overall_valid = all(r.is_valid for r in results if r.severity == "error")
        
        return overall_valid, results
    
    def validate_with_summary(self, obj: Any) -> Dict:
        """Validate object and return detailed summary."""
        is_valid, results = self.validate(obj)
        
        # Group results by severity
        errors = [r for r in results if r.severity == "error" and not r.is_valid]
        warnings = [r for r in results if r.severity == "warning" and not r.is_valid]
        info = [r for r in results if r.severity == "info"]
        
        return {
            "is_valid": is_valid,
            "summary": {
                "total_rules": len(results),
                "passed": len([r for r in results if r.is_valid]),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info)
            },
            "results": results,
            "errors": errors,
            "warnings": warnings,
            "info": info
        }
    
    # Rule implementations
    def _validate_structure(self, obj: Any) -> Tuple[bool, str, Optional[Dict]]:
        """Validate basic object structure."""
        if not isinstance(obj, dict):
            return False, "Object must be a dictionary", None
        
        expected_keys = {"name", "price", "promo", "core", "cond", "nth"}
        actual_keys = set(obj.keys())
        
        if actual_keys != expected_keys:
            missing = expected_keys - actual_keys
            extra = actual_keys - expected_keys
            details = {"missing": list(missing), "extra": list(extra)}
            return False, f"Keys must be exactly {sorted(expected_keys)}", details
        
        return True, "Structure is valid", None
    
    def _validate_field_types(self, obj: Any) -> Tuple[bool, str, Optional[Dict]]:
        """Validate field types."""
        # name
        if not isinstance(obj["name"], str) or not obj["name"].strip():
            return False, "Name must be non-empty string", None
        
        # price
        price = obj["price"]
        if price is not None:
            if not isinstance(price, (int, float)):
                return False, "Price must be number or null", None
            if not math.isfinite(float(price)):
                return False, "Price must be finite number", None
        
        # core, cond, nth must be strings without spaces
        for field_name in ("core", "cond", "nth"):
            value = obj[field_name]
            if not isinstance(value, str):
                return False, f"{field_name} must be string", None
            if " " in value:
                return False, f"{field_name} must not contain spaces", None
        
        return True, "Field types are valid", None
    
    def _validate_promo_code(self, obj: Any) -> Tuple[bool, str, Optional[Dict]]:
        """Validate promotion code."""
        from ..common.validation import ALLOWED_PROMO_CODES
        
        promo = obj["promo"]
        if promo not in ALLOWED_PROMO_CODES:
            return False, f"Promo '{promo}' not in {sorted(ALLOWED_PROMO_CODES)}", None
        
        return True, "Promotion code is valid", None
    
    def _validate_core_field(self, obj: Any) -> Tuple[bool, str, Optional[Dict]]:
        """Validate core field based on promo."""
        from ..common.validation import CORE_PATTERNS
        
        promo = obj["promo"]
        core = obj["core"]
        
        if promo not in CORE_PATTERNS:
            return False, f"No core pattern defined for promo '{promo}'", None
        
        pattern = CORE_PATTERNS[promo]
        if not pattern.match(core):
            return False, f"Core '{core}' invalid for {promo}", None
        
        return True, "Core field is valid", None
    
    def _validate_cross_fields(self, obj: Any) -> Tuple[bool, str, Optional[Dict]]:
        """Validate cross-field relationships."""
        promo = obj["promo"]
        core = obj["core"]
        cond = obj["cond"]
        nth = obj["nth"]
        
        # NONE requires empty fields
        if promo == "NONE":
            if core or cond or nth:
                return False, "NONE requires core='', cond='', nth=''", None
        
        # SUP requires empty nth
        if promo == "SUP":
            if nth:
                return False, "SUP requires nth=''", None
        
        # DEALFIX requires non-empty cond and empty nth
        if promo == "DEALFIX":
            if not cond:
                return False, "DEALFIX requires non-empty cond (N or AxB)", None
            if nth:
                return False, "DEALFIX requires nth=''", None
        
        # BXYG requires empty nth
        if promo == "BXYG":
            if nth:
                return False, "BXYG requires nth=''", None
        
        return True, "Cross-field validation passed", None
    
    def get_validation_statistics(self) -> Dict:
        """Get statistics about validation rules."""
        return {
            "total_rules": len(self.rules),
            "rules_by_severity": {
                severity: [r.name for r in self.rules if r.severity == severity]
                for severity in set(r.severity for r in self.rules)
            }
        }


# Backward compatibility function
def validate_label_object(obj: object) -> Tuple[bool, str]:
    """Legacy validation function for backward compatibility."""
    validator = LabelValidator()
    is_valid, results = validator.validate(obj)
    
    if is_valid:
        return True, ""
    
    # Return first error message
    for result in results:
        if not result.is_valid and result.severity == "error":
            return False, result.message
    
    return False, "Validation failed"


# Global validator instance
_global_validator = LabelValidator()


def get_validator() -> LabelValidator:
    """Get the global validator instance."""
    return _global_validator


def validate_with_details(obj: object) -> Dict:
    """Validate object with detailed results using global validator."""
    return _global_validator.validate_with_summary(obj)
