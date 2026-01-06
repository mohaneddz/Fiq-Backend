"""
Database tools for Chat agent.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.db import DatabaseManager
from Chat import config


class DrugLookupTool:
    """Tool to lookup drug information from database."""
    
    def __init__(self):
        self.db = DatabaseManager(config.DRUGS_DB_PATH)
    
    def run(self, drug_name: str) -> dict:
        """
        Lookup drug information by name.
        
        Args:
            drug_name: Name of the drug to lookup
            
        Returns:
            Dictionary with drug information or error
        """
        try:
            query = """
                SELECT * FROM drugs 
                WHERE LOWER(name) = LOWER(?) OR LOWER(common_name) LIKE LOWER(?)
                LIMIT 1
            """
            results = self.db.execute_query(query, (drug_name, f"%{drug_name}%"))
            
            if results:
                return {"found": True, "drug": results[0]}
            else:
                return {"found": False, "message": f"No information found for '{drug_name}'"}
        except Exception as e:
            return {"found": False, "error": str(e)}
    
    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'db'):
            self.db.close()


class HistoryLookupTool:
    """Tool to lookup user medical history."""
    
    def __init__(self):
        self.db = DatabaseManager(config.HISTORY_DB_PATH)
    
    def run(self, user_id: str) -> dict:
        """
        Lookup user medical history.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with encounter history or error
        """
        try:
            query = """
                SELECT * FROM encounters 
                WHERE user_id = ?
                ORDER BY encounter_date DESC
                LIMIT 10
            """
            results = self.db.execute_query(query, (user_id,))
            
            return {
                "found": True,
                "user_id": user_id,
                "encounters": results,
                "count": len(results)
            }
        except Exception as e:
            return {"found": False, "error": str(e)}
    
    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'db'):
            self.db.close()


def get_tools():
    """Get all available tools for the agent."""
    return {
        "lookup_drug": DrugLookupTool(),
        "lookup_history": HistoryLookupTool()
    }
