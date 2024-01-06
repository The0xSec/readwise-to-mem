import requests
import datetime
import os
import markdownify
import json

base_readwise_url = "https://readwise.io/api/v2/auth/"
readwise_token = os.environ['READWISE_TOKEN'] 
base_mem_url = "https://api.mem.ai/v0/mems"


def main():
    print("Starting Export Operation")
        
    last_fetch_was_at = datetime.datetime.now() - datetime.timedelta(days=1)
    new_data = fetch_from_export_api()
    return
    
def fetch_from_export_api(updated_after=None):
    full_data = []
    next_page_cursor = None
    
    while True:
        params = {}
        if next_page_cursor:
            params['pageCursor'] = next_page_cursor
        if updated_after:
            params['updatedAfter'] = updated_after
        print("Making export api request with params " + str(params) + "...")
        response = requests.get(
            url="https://readwise.io/api/v2/export/",
            params=params,
            headers={"Authorization": f"Token {readwise_token}"}, verify=False
        )
        full_data.extend(response.json()['results'])
        next_page_cursor = response.json().get('nextPageCursor')
        if not next_page_cursor:
            break
    
    print("Exported " + str(len(full_data)) + " highlights from Readwise")
    print("Starting import to Mem.ai")
    
    for highlight in full_data:
        converted_data = json_to_markdown(full_data)
        create_mem(converted_data)
    
def json_to_markdown(json_data):
    markdown = ""

    def traverse_json(data, indentation=""):
        nonlocal markdown

        if isinstance(data, dict):
            for key, value in data.items():
                markdown += f"{indentation}- **{key}**: "

                if isinstance(value, (str, int, float, bool)):
                    markdown += str(value) + '\n'
                elif isinstance(value, (list, dict)):
                    markdown += '\n'
                    traverse_json(value, indentation + '  ')
                else:
                    markdown += '\n'

        elif isinstance(data, list):
            for item in data:
                traverse_json(item, indentation + '  ')

    traverse_json(json_data)
    return markdown
    
    
def create_mem(highlights):
    for highlight in highlights:
            
        data = {
            "content": highlight,
            "isRead": False,
            "isArchived": False,
            "createdAt": datetime.datetime.now().isoformat(),
        }
        
        auth = {
            "Authorization": "ApiAccessToken" + "Bearer " + os.environ['MEM_TOKEN'],
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            url=base_mem_url,
            json=data,
            headers=auth
        )
                
        print(response.status_code)
        
        if response.status_code != 200:
            print("Error importing highlight to Mem.ai")
            print(response.json())
            break
    return
    
if __name__ == "__main__":
    main()