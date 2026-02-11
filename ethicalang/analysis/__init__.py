"""Static analysis modules for EthicaLang"""
from .energy import EnergyAnalyzer
from .ethics import EthicsChecker
from .readability import ReadabilityScorer
from .cleverness import ClevernessDetector

__all__ = ['EnergyAnalyzer', 'EthicsChecker', 'ReadabilityScorer', 'ClevernessDetector']
