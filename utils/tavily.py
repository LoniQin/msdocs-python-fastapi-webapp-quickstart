
import requests
import os
def tavily_search(query):
    url = "https://api.tavily.com/search"
    api_key = os.environ["TAVILY_API_KEY"]  # Replace with your actual API key

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "query": query  # Replace with your actual query
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    print(tavily_search("What is weather like in Guang Zhou?"))
