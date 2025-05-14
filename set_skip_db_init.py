#!/usr/bin/env python
"""
Script to set SKIP_DB_INIT=true in the deployment environment
This should be run once after the initial deployment has successfully
initialized the database.
"""
import os
import sys
import argparse
import requests

def main():
    parser = argparse.ArgumentParser(
        description="Set SKIP_DB_INIT=true in deployment environment")
    parser.add_argument(
        "--railway", 
        action="store_true", 
        help="Set for Railway deployment"
    )
    args = parser.parse_args()
    
    if args.railway:
        # For Railway, use their API
        railway_api_token = os.environ.get("RAILWAY_API_TOKEN")
        project_id = os.environ.get("RAILWAY_PROJECT_ID")
        service_id = os.environ.get("RAILWAY_SERVICE_ID")
        
        if not railway_api_token or not project_id or not service_id:
            print("Error: Railway API token, project ID, and service ID are required.")
            print("Please set RAILWAY_API_TOKEN, RAILWAY_PROJECT_ID, and RAILWAY_SERVICE_ID environment variables.")
            sys.exit(1)
        
        try:
            # This is a simplified example - actual Railway API usage would depend on their current API structure
            headers = {
                "Authorization": f"Bearer {railway_api_token}",
                "Content-Type": "application/json"
            }
            
            # Get current variables
            get_url = f"https://backboard.railway.app/api/projects/{project_id}/services/{service_id}/variables"
            response = requests.get(get_url, headers=headers)
            response.raise_for_status()
            
            # Add SKIP_DB_INIT=true
            variables = response.json()
            variables["SKIP_DB_INIT"] = "true"
            
            # Update variables
            update_url = f"https://backboard.railway.app/api/projects/{project_id}/services/{service_id}/variables"
            response = requests.patch(update_url, headers=headers, json=variables)
            response.raise_for_status()
            
            print("Successfully set SKIP_DB_INIT=true in Railway environment")
        except Exception as e:
            print(f"Error setting environment variable: {e}")
            sys.exit(1)
    else:
        # For local testing, just print instructions
        print("For deployment environments, set SKIP_DB_INIT=true in your environment variables.")
        print("Railway: Go to your project dashboard → Variables → Add SKIP_DB_INIT=true")
        print("Heroku: heroku config:set SKIP_DB_INIT=true --app YOUR_APP_NAME")
        print("Other platforms: Check your platform's documentation for setting environment variables")

if __name__ == "__main__":
    main() 