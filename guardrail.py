#!/usr/bin/env python3

import re
import sys
from typing import List, Tuple

class Guardrail:
    """Guardrail system to prevent prompt injection and jailbreaking attempts"""
    
    def __init__(self):
        # Suspicious patterns that might indicate prompt injection
        self.suspicious_patterns = [
            # Role manipulation attempts
            r"ignore.*previous.*instructions",
            r"forget.*previous.*instructions", 
            r"disregard.*previous.*instructions",
            r"ignore.*above.*instructions",
            r"pretend.*you.*are",
            r"act.*as.*if.*you.*are",
            r"you.*are.*now",
            r"from.*now.*on.*you.*are",
            
            # System prompt injection
            r"system.*prompt",
            r"system.*message",
            r"assistant.*role",
            r"user.*role",
            
            # Jailbreaking attempts
            r"bypass.*safety",
            r"ignore.*safety",
            r"disable.*safety",
            r"override.*safety",
            r"ignore.*content.*policy",
            r"bypass.*content.*policy",
            
            # Output manipulation
            r"output.*only",
            r"respond.*only",
            r"answer.*only",
            r"ignore.*everything.*except",
            
            # Dangerous content requests
            r"how.*to.*hack",
            r"how.*to.*exploit",
            r"how.*to.*bypass",
            r"create.*malware",
            r"create.*virus",
            r"create.*exploit",
            
            # Personal information requests
            r"what.*is.*your.*name",
            r"what.*is.*your.*real.*name",
            r"what.*is.*your.*identity",
            r"who.*created.*you",
            r"who.*developed.*you",
            
            # Model information requests
            r"what.*model.*are.*you",
            r"what.*version.*are.*you",
            r"what.*is.*your.*architecture",
            r"what.*are.*your.*parameters",
            
            # API key or token requests
            r"api.*key",
            r"access.*token",
            r"authentication.*token",
            r"secret.*key",
            
            # File system access
            r"read.*file",
            r"write.*file",
            r"delete.*file",
            r"access.*file.*system",
            r"file.*system.*access",
            
            # Network access
            r"make.*http.*request",
            r"send.*request",
            r"network.*access",
            r"internet.*access",
            
            # Code execution
            r"execute.*code",
            r"run.*code",
            r"eval.*code",
            r"exec.*code",
            
            # Database access
            r"access.*database",
            r"sql.*query",
            r"database.*query",
            
            # Environment variables
            r"environment.*variable",
            r"env.*var",
            r"getenv",
            
            # Process manipulation
            r"kill.*process",
            r"terminate.*process",
            r"system.*command",
            r"shell.*command",
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        
        # Warning messages for different types of violations
        self.warning_messages = {
            "role_manipulation": "⚠️  Warning: Attempting to manipulate AI behavior is not allowed.",
            "system_injection": "⚠️  Warning: System prompt injection attempts are blocked.",
            "jailbreaking": "⚠️  Warning: Safety bypass attempts are not permitted.",
            "dangerous_content": "⚠️  Warning: Requests for harmful content are blocked.",
            "personal_info": "⚠️  Warning: Personal information requests are not allowed.",
            "technical_info": "⚠️  Warning: Technical system information requests are blocked.",
            "access_attempts": "⚠️  Warning: System access attempts are not permitted."
        }

    def check_input(self, user_input: str) -> Tuple[bool, str, str]:
        """
        Check user input for suspicious patterns
        
        Returns:
            Tuple[bool, str, str]: (is_safe, warning_message, violation_type)
        """
        if not user_input or not user_input.strip():
            return True, "", ""
        
        user_input_lower = user_input.lower()
        
        # Check for suspicious patterns
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(user_input):
                violation_type = self._get_violation_type(i)
                warning_message = self.warning_messages.get(violation_type, "⚠️  Warning: Suspicious input detected.")
                return False, warning_message, violation_type
        
        # Additional checks for specific dangerous patterns
        if self._check_dangerous_content(user_input_lower):
            return False, self.warning_messages["dangerous_content"], "dangerous_content"
        
        if self._check_access_attempts(user_input_lower):
            return False, self.warning_messages["access_attempts"], "access_attempts"
        
        return True, "", ""

    def _get_violation_type(self, pattern_index: int) -> str:
        """Map pattern index to violation type"""
        if pattern_index < 8:
            return "role_manipulation"
        elif pattern_index < 12:
            return "system_injection"
        elif pattern_index < 18:
            return "jailbreaking"
        elif pattern_index < 24:
            return "dangerous_content"
        elif pattern_index < 29:
            return "personal_info"
        elif pattern_index < 33:
            return "technical_info"
        elif pattern_index < 37:
            return "access_attempts"
        elif pattern_index < 42:
            return "access_attempts"
        elif pattern_index < 46:
            return "access_attempts"
        elif pattern_index < 50:
            return "access_attempts"
        elif pattern_index < 54:
            return "access_attempts"
        else:
            return "access_attempts"

    def _check_dangerous_content(self, text: str) -> bool:
        """Check for dangerous content patterns"""
        dangerous_keywords = [
            "bomb", "explosive", "weapon", "drug", "illegal", "criminal",
            "hack", "exploit", "malware", "virus", "trojan", "ransomware",
            "phishing", "scam", "fraud", "steal", "rob", "kill", "murder"
        ]
        
        return any(keyword in text for keyword in dangerous_keywords)

    def _check_access_attempts(self, text: str) -> bool:
        """Check for system access attempts"""
        access_keywords = [
            "sudo", "root", "admin", "privilege", "elevate", "escalate",
            "shell", "terminal", "command", "execute", "run", "system",
            "file", "directory", "path", "read", "write", "delete",
            "network", "http", "request", "api", "database", "sql"
        ]
        
        # Check if multiple access-related keywords are present
        access_count = sum(1 for keyword in access_keywords if keyword in text)
        return access_count >= 2

    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input by removing or escaping potentially dangerous content
        """
        if not user_input:
            return user_input
        
        # Remove or escape special characters that might be used for injection
        sanitized = user_input
        
        # Escape backticks and other code markers
        sanitized = sanitized.replace("`", "\\`")
        
        # Remove multiple spaces and newlines that might be used for formatting attacks
        sanitized = re.sub(r'\n+', '\n', sanitized)
        sanitized = re.sub(r' +', ' ', sanitized)
        
        # Limit input length to prevent overwhelming the model
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000] + "..."
        
        return sanitized.strip()