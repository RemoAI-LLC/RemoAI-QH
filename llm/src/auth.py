"""
Authentication module for AnythingLLM API
"""
import requests
import yaml
import sys
from typing import Dict, Any

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

def test_auth() -> bool:
    """Test authentication with AnythingLLM API"""
    config = load_config()
    
    headers = {
        'Authorization': f"Bearer {config['api_key']}",
        'Content-Type': 'application/json'
    }
    
    print(f"🔍 Testing connection to AnythingLLM...")
    print(f"Base URL: {config['model_server_base_url']}")
    print(f"API Key: {config['api_key'][:8]}...")
    
    # Test authentication by getting workspaces (this is a reliable endpoint)
    try:
        print(f"Testing workspaces endpoint...")
        response = requests.get(
            f"{config['model_server_base_url']}/workspaces",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            try:
                workspaces_data = response.json()
                workspaces = workspaces_data.get('workspaces', [])
                print(f"Found {len(workspaces)} workspace(s)")
                for workspace in workspaces:
                    print(f"  - {workspace.get('name', 'Unknown')} (slug: {workspace.get('slug', 'Unknown')})")
                
                # Check if the configured workspace exists
                configured_slug = config.get('workspace_slug', '')
                workspace_slugs = [w.get('slug', '') for w in workspaces]
                if configured_slug in workspace_slugs:
                    print(f"✅ Configured workspace '{configured_slug}' found!")
                else:
                    print(f"⚠️  Configured workspace '{configured_slug}' not found in available workspaces")
                    print(f"Available workspaces: {', '.join(workspace_slugs)}")
                
                return True
            except Exception as e:
                print(f"Response received but error parsing: {e}")
                return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Make sure AnythingLLM is running on the configured URL")
        return False

if __name__ == "__main__":
    test_auth()
