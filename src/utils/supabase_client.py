import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class RealSupabaseResponse:
    def __init__(self, data, error=None):
        self.data = data
        self.error = error

class RealSupabaseTable:
    def __init__(self, url, key, table_name):
        self.url = url
        self.key = key
        self.table_name = table_name
        self.params = {}
        self._order = None
        self._limit = None
        self._method = "GET"
        self._json_data = None

    def select(self, columns="*"):
        self.params["select"] = columns
        self._method = "GET"
        return self

    def insert(self, data):
        self._method = "POST"
        self._json_data = data
        return self

    def update(self, data):
        self._method = "PATCH"
        self._json_data = data
        return self

    def eq(self, column, value):
        self.params[column] = f"eq.{value}"
        return self

    def order(self, column, desc=True):
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self

    def limit(self, count):
        self._limit = count
        return self

    def execute(self):
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.url}/rest/v1/{self.table_name}"
        
        if self._method == "POST":
            headers["Prefer"] = "return=representation"
            res = requests.post(url, headers=headers, json=self._json_data)
        elif self._method == "PATCH":
            headers["Prefer"] = "return=representation"
            res = requests.patch(url, headers=headers, params=self.params, json=self._json_data)
        else: # GET
            if self._order: self.params["order"] = self._order
            if self._limit: self.params["limit"] = self._limit
            res = requests.get(url, headers=headers, params=self.params)

        if res.status_code >= 400:
            return RealSupabaseResponse([], error=res.text)
        
        # Postgrest returns 204 No Content for some updates if representation not requested, 
        # but we added it. For GET/POST it returns JSON.
        try:
            return RealSupabaseResponse(res.json() if res.text else [])
        except:
            return RealSupabaseResponse([])

class SupabaseLightClient:
    def __init__(self, url, key):
        self.url = url.rstrip('/')
        self.key = key

    def table(self, name):
        return RealSupabaseTable(self.url, self.key, name)

def get_supabase_client():
    """
    Retorna un cliente Supabase REAL basado en peticiones HTTP directas (REST/Postgrest).
    Esto evita la dependencia de la librería 'supabase-py' que falla en Python 3.14.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key or url == "YOUR_SUPABASE_URL" or key == "YOUR_SUPABASE_KEY":
        return None
        
    return SupabaseLightClient(url, key)
