import requests

API_KEY = "eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzYzODA3Njc2LCJqdGkiOiI4MTU2YWVjZS04ZDVhLTRhYjgtYTYzYS02MWE4MmI2YTIxNTciLCJ1c2VyX3V1aWQiOiJjNjZiMDE5MC0yNjNhLTRkMzItOWZhYi1kOTIyNTZlY2ZiMjAifQ.G02mHUpuJl_LeIKHjzRrHNGeZFfNFZ8wMCToS70YLobDSZWsnMfIFbYusnNLK8NEzdiz_gnkqCj1zo5A8BQZxg"  # ← Pega tu API Key aquí

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.calendly.com/users/me', headers=headers)

if response.status_code == 200:
    data = response.json()
    user_uri = data['resource']['uri']
    print("✅ Tu User URI es:")
    print(user_uri)
    print("\nCópialo y pégalo en tu .env")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)