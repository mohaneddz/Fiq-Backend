"""
Supabase database connection manager.
Replaces SQLite with PostgreSQL via Supabase REST API.
Uses requests library for HTTP calls to avoid dependency issues.
"""
import os
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()


class SupabaseManager:
    """Supabase database connection manager using REST API."""
    
    def __init__(self, table_name: str = None):
        """
        Initialize Supabase REST client.
        
        Args:
            table_name: Default table name for operations (for backwards compatibility)
        """
        self.url = os.getenv("DB_URL")
        self.service_role_key = os.getenv("SERVICE_ROLE_KEY")
        
        if not self.url or not self.service_role_key:
            raise ValueError("DB_URL and SERVICE_ROLE_KEY must be set in environment variables")
        
        # REST API base URL
        self.rest_url = f"{self.url}/rest/v1"
        self.headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.table_name = table_name
    
    def execute_query(self, query: str = None, params: tuple = (), table: str = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        For backwards compatibility with SQLite code.
        This method is kept but the query parameter is ignored - use select() instead.
        
        Args:
            query: SQL query (ignored for Supabase)
            params: Query parameters (ignored for Supabase)
            table: Table name to query from
            
        Returns:
            List of dictionaries representing rows
        """
        table_to_use = table or self.table_name
        if not table_to_use:
            raise ValueError("No table specified")
        
        try:
            url = f"{self.rest_url}/{table_to_use}?select=*"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Query error: {e}")
            return []
    
    def select(self, table: str = None, columns: str = "*", filters: Dict[str, Any] = None, 
               limit: int = None, order_by: str = None, order_desc: bool = True,
               ilike_filters: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """
        Select data from a table with flexible filtering.
        
        Args:
            table: Table name (optional if set in constructor)
            columns: Columns to select (default: "*")
            filters: Dictionary of column: value for exact match filters
            limit: Maximum number of rows to return
            order_by: Column to order by
            order_desc: Order descending if True, ascending if False
            ilike_filters: Dictionary of column: pattern for case-insensitive LIKE filters
            
        Returns:
            List of dictionaries representing rows
        """
        table_to_use = table or self.table_name
        if not table_to_use:
            raise ValueError("No table specified")
        
        try:
            # Build URL with query parameters
            url = f"{self.rest_url}/{table_to_use}?select={columns}"
            
            # Apply exact match filters
            if filters:
                for key, value in filters.items():
                    url += f"&{key}=eq.{value}"
            
            # Apply case-insensitive LIKE filters
            if ilike_filters:
                for key, pattern in ilike_filters.items():
                    url += f"&{key}=ilike.{pattern}"
            
            # Apply ordering
            if order_by:
                order_dir = "desc" if order_desc else "asc"
                url += f"&order={order_by}.{order_dir}"
            
            # Apply limit
            if limit:
                url += f"&limit={limit}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            print(f"Select error: {e}")
            return []
    
    def insert(self, data: Dict[str, Any], table: str = None) -> Dict[str, Any]:
        """
        Insert a row into a table.
        
        Args:
            data: Dictionary of column: value pairs
            table: Table name (optional if set in constructor)
            
        Returns:
            Inserted row data
        """
        table_to_use = table or self.table_name
        if not table_to_use:
            raise ValueError("No table specified")
        
        try:
            url = f"{self.rest_url}/{table_to_use}"
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result[0] if result else {}
        except Exception as e:
            print(f"Insert error: {e}")
            return {"error": str(e)}
    
    def update(self, data: Dict[str, Any], filters: Dict[str, Any], table: str = None) -> List[Dict[str, Any]]:
        """
        Update rows in a table.
        
        Args:
            data: Dictionary of column: value pairs to update
            filters: Dictionary of column: value filters for WHERE clause
            table: Table name (optional if set in constructor)
            
        Returns:
            List of updated rows
        """
        table_to_use = table or self.table_name
        if not table_to_use:
            raise ValueError("No table specified")
        
        try:
            # Build URL with filters
            url = f"{self.rest_url}/{table_to_use}?"
            filter_parts = []
            for key, value in filters.items():
                filter_parts.append(f"{key}=eq.{value}")
            url += "&".join(filter_parts)
            
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Update error: {e}")
            return []
    
    def delete(self, filters: Dict[str, Any], table: str = None) -> List[Dict[str, Any]]:
        """
        Delete rows from a table.
        
        Args:
            filters: Dictionary of column: value filters for WHERE clause
            table: Table name (optional if set in constructor)
            
        Returns:
            List of deleted rows
        """
        table_to_use = table or self.table_name
        if not table_to_use:
            raise ValueError("No table specified")
        
        try:
            # Build URL with filters
            url = f"{self.rest_url}/{table_to_use}?"
            filter_parts = []
            for key, value in filters.items():
                filter_parts.append(f"{key}=eq.{value}")
            url += "&".join(filter_parts)
            
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json() if response.text else []
        except Exception as e:
            print(f"Delete error: {e}")
            return []
    
    def execute_update(self, query: str = None, params: tuple = (), table: str = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        Kept for backwards compatibility with SQLite code.
        
        Returns:
            Number of affected rows (always 1 for compatibility)
        """
        return 1
    
    def get_cursor(self):
        """
        Context manager for backwards compatibility.
        Returns self since Supabase doesn't use cursors.
        """
        return self
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    def close(self):
        """Close connection (no-op for Supabase as it uses HTTP)."""
        pass
    
    def close_connection(self):
        """Close connection (no-op for Supabase as it uses HTTP)."""
        pass


# Backwards compatibility alias
DatabaseManager = SupabaseManager
