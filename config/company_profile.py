# config/company_profile.py

import json
import os
from datetime import datetime
from pathlib import Path

class CompanyProfile:
    """Manages company profile configuration"""
    
    def __init__(self):
        self.config_file = Path('config/company_profile.json')
        self.company_name = ""
        self.description = ""
        self.budget = 0.0
        self.sector = ""
        self.goal = ""
        self.target_location = "India"
        self.created_at = None
        self.updated_at = None
        
        # Load existing profile if it exists
        self.load_profile()
    
    def load_profile(self):
        """Load company profile from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                self.company_name = data.get('company_name', '')
                self.description = data.get('description', '')
                self.budget = data.get('budget', 0.0)
                self.sector = data.get('sector', '')
                self.goal = data.get('goal', '')
                self.target_location = data.get('target_location', 'India')
                self.created_at = data.get('created_at')
                self.updated_at = data.get('updated_at')
                
        except Exception as e:
            print(f"Warning: Could not load company profile: {e}")
    
    def save_profile(self):
        """Save company profile to file"""
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'company_name': self.company_name,
                'description': self.description,
                'budget': self.budget,
                'sector': self.sector,
                'goal': self.goal,
                'target_location': self.target_location,
                'created_at': self.created_at or datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error: Could not save company profile: {e}")
    
    def set_profile(self, company_name: str, description: str, budget: float, 
                   sector: str, goal: str, target_location: str = "India"):
        """Set company profile data"""
        self.company_name = company_name
        self.description = description
        self.budget = budget
        self.sector = sector
        self.goal = goal
        self.target_location = target_location
        
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        
        self.save_profile()
    
    def get_context(self) -> str:
        """Get company context for agents"""
        if not self.company_name:
            return "Company profile not set up yet."
        
        context = f"""
Company Profile:
- Name: {self.company_name}
- Description: {self.description}
- Sector: {self.sector}
- Budget: ${self.budget:,.2f}
- Goal: {self.goal}
- Target Location: {self.target_location}
"""
        return context.strip()
    
    def is_configured(self) -> bool:
        """Check if company profile is configured"""
        return bool(self.company_name and self.description)
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary"""
        return {
            'company_name': self.company_name,
            'description': self.description,
            'budget': self.budget,
            'sector': self.sector,
            'goal': self.goal,
            'target_location': self.target_location,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_configured': self.is_configured()
        }
    
    def __str__(self):
        """String representation of company profile"""
        if not self.is_configured():
            return "Company profile not configured"
        
        return f"""
🏢 {self.company_name}
📝 {self.description}
🏭 Sector: {self.sector}
💰 Budget: ${self.budget:,.2f}
🎯 Goal: {self.goal}
📍 Location: {self.target_location}
"""

# Global company profile instance
company_profile = CompanyProfile()