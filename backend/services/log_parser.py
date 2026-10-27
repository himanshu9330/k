"""
SentinelAI-X Log Parser Compatibility Module
==============================================
Re-exports parse_log from parser_service to maintain backwards compatibility.
"""

from services.parser_service import parse_log

__all__ = ["parse_log"]