"""
Workspace management utilities for AnythingLLM
"""
import requests
import yaml
import sys
from typing import List, Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: config.yaml not found. Please create it with your API key and settings.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}")
        sys.exit(1)

def get_workspaces() -> List[Dict[str, Any]]:
    """Get list of available workspaces"""
    config = load_config()
    
    headers = {
        'Authorization': f"Bearer {config['api_key']}",
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{config['model_server_base_url']}/workspaces",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Handle the response structure - workspaces might be nested
            if 'workspaces' in data:
                return data['workspaces']
            else:
                return data
        else:
            print(f"Error fetching workspaces: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return []

def list_workspaces():
    """List all available workspaces with their slugs"""
    workspaces = get_workspaces()
    
    if not workspaces:
        print("No workspaces found or error occurred.")
        return
    
    print("\n📁 Available Workspaces:")
    print("-" * 50)
    
    # Handle both list and single workspace response
    if isinstance(workspaces, list):
        workspace_list = workspaces
    else:
        workspace_list = [workspaces]
    
    for workspace in workspace_list:
        if isinstance(workspace, dict):
            print(f"Name: {workspace.get('name', 'Unknown')}")
            print(f"Slug: {workspace.get('slug', 'Unknown')}")
            print(f"ID: {workspace.get('id', 'Unknown')}")
            print(f"Vector Count: {workspace.get('vectorCount', 0)}")
        else:
            print(f"Workspace: {workspace}")
        print("-" * 50)

if __name__ == "__main__":
    list_workspaces()
