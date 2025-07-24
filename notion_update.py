import requests
import os

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

def update_notion_dashboard(page_id, content):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "Status": {
                "rich_text": [{
                    "text": {
                        "content": content
                    }
                }]
            }
        }
    }

    response = requests.patch(url, headers=headers, json=data)
    return response.status_code
