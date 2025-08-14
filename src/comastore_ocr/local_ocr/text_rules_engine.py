"""Enhanced text rules engine with better organization and extensibility."""

import re
from typing import List, Optional, Dict, Pattern

from .text_rule import TextRule


class TextRulesEngine:
    """Engine for applying text classification rules."""
    
    def __init__(self):
        self.rules: List[TextRule] = []
        self._compiled_patterns: Dict[str, Pattern] = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default text classification rules."""
        self.add_rule(TextRule(
            name="BXYG - Buy X Get Y Gratis",
            matcher=self._rule_bxyg,
            promo="BXYG",
            description="Keywords like 'X+Y gratis' or 'gratis przy zakupie'",
            priority=1
        ))
        
        self.add_rule(TextRule(
            name="DEALFIX - Fixed Price Deal",
            matcher=self._rule_dealfix,
            promo="DEALFIX",
            description="'drugi za X zł' or 'N-ty za X zł' patterns",
            priority=2
        ))
        
        self.add_rule(TextRule(
            name="DISC - Discount",
            matcher=self._rule_disc,
            promo="DISC",
            description="Percentage discounts and 'teraz taniej'",
            priority=3
        ))
        
        self.add_rule(TextRule(
            name="SUP - Supercena",
            matcher=self._rule_sup,
            promo="SUP",
            description="'supercena' keyword",
            priority=4
        ))
        
        self.add_rule(TextRule(
            name="NONE - No Promotion",
            matcher=self._rule_none,
            promo="NONE",
            description="'na stałe w ofercie' or no promotion",
            priority=5
        ))
    
    def add_rule(self, rule: TextRule) -> None:
        """Add a new text classification rule."""
        self.rules.append(rule)
        # Sort by priority (lower number = higher priority)
        self.rules.sort(key=lambda r: r.priority)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_count
    
    def get_rule(self, rule_name: str) -> Optional[TextRule]:
        """Get a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def list_rules(self) -> List[Dict]:
        """List all available rules with their details."""
        return [
            {
                "name": rule.name,
                "promo": rule.promo,
                "description": rule.description,
                "priority": rule.priority
            }
            for rule in self.rules
        ]
    
    def classify_text(self, text: str) -> Optional[str]:
        """Classify text using available rules in priority order."""
        for rule in self.rules:
            try:
                if rule.matcher(text):
                    return rule.promo
            except Exception as e:
                print(f"⚠️  Error applying rule '{rule.name}': {e}")
                continue
        return None
    
    def classify_text_with_details(self, text: str) -> Dict:
        """Classify text and return detailed results."""
        results = {
            "text": text,
            "classification": None,
            "applied_rule": None,
            "all_matches": []
        }
        
        for rule in self.rules:
            try:
                if rule.matcher(text):
                    results["all_matches"].append({
                        "rule_name": rule.name,
                        "promo": rule.promo,
                        "priority": rule.priority
                    })
                    
                    # First match (highest priority) becomes the classification
                    if results["classification"] is None:
                        results["classification"] = rule.promo
                        results["applied_rule"] = rule.name
            except Exception as e:
                print(f"⚠️  Error applying rule '{rule.name}': {e}")
                continue
        
        return results
    
    # Rule implementations
    def _rule_bxyg(self, text: str) -> bool:
        """Check for BXYG patterns."""
        # Keywords like "X+Y gratis" → BXYG
        if re.search(r"\b(\d+)\s*\+\s*(\d+)\s*gratis\b", text, flags=re.IGNORECASE):
            return True
        
        # Check for "gratis przy zakupie" or "gratis"
        keywords = ["gratis przy zakupie", "gratis"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _rule_dealfix(self, text: str) -> bool:
        """Check for DEALFIX patterns."""
        # "drugi za X zł" / "N-ty za X zł"
        pattern = r"\b(drugi|\d+-?ty)\b\s*za\s*\d+[\,\.]?\d*\s*zł"
        return bool(re.search(pattern, text, flags=re.IGNORECASE))
    
    def _rule_disc(self, text: str) -> bool:
        """Check for DISC patterns."""
        text_lower = text.lower()
        
        # 1) "drugi … % taniej"
        if re.search(r"\bdrugi\b.*?\%\s*taniej", text, flags=re.IGNORECASE | re.DOTALL):
            return True
        
        # 2) "% taniej przy zakupie N"
        if re.search(r"\%\s*taniej\s*przy\s*zakupie\s*\d+", text, flags=re.IGNORECASE):
            return True
        
        # 3) TERAZ TANIEJ keyword
        if "teraz taniej" in text_lower:
            return True
        
        # 4) Standalone "% taniej" without explicit purchase-condition keywords
        if re.search(r"\b\d+\s*%\s*taniej\b", text, flags=re.IGNORECASE):
            # Check that it's not part of other patterns
            exclusion_keywords = ["przy zakupie", "drugi", "n-ty"]
            if not any(keyword in text_lower for keyword in exclusion_keywords):
                return True
        
        return False
    
    def _rule_sup(self, text: str) -> bool:
        """Check for SUP patterns."""
        # SUPERCENA: allow regardless of presence of "pak/PAKU" or other qualifiers
        return "supercena" in text.lower()
    
    def _rule_none(self, text: str) -> bool:
        """Check for NONE patterns."""
        # Check for "na stałe w ofercie"
        return "na stałe w ofercie" in text.lower()
    
    def test_rule(self, rule_name: str, test_text: str) -> bool:
        """Test a specific rule with given text."""
        rule = self.get_rule(rule_name)
        if rule is None:
            raise ValueError(f"Rule '{rule_name}' not found")
        
        return rule.matcher(test_text)
    
    def get_rule_statistics(self) -> Dict:
        """Get statistics about rule usage."""
        return {
            "total_rules": len(self.rules),
            "rules_by_priority": {
                rule.priority: [r.name for r in self.rules if r.priority == rule.priority]
                for rule in self.rules
            },
            "promo_coverage": list(set(rule.promo for rule in self.rules))
        }


# Backward compatibility
DEFAULT_RULES = [
    lambda text: TextRulesEngine()._rule_bxyg(text),
    lambda text: TextRulesEngine()._rule_dealfix(text),
    lambda text: TextRulesEngine()._rule_disc(text),
    lambda text: TextRulesEngine()._rule_sup(text),
    lambda text: TextRulesEngine()._rule_none(text),
]
