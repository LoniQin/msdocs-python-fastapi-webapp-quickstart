import requests

def create_medium_blog():
    access_token = 'YOUR_ACCESS_TOKEN'
    user_id = 'YOUR_USER_ID'
    url = f'https://api.medium.com/v1/users/{user_id}/posts'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'title': 'My First Markdown Post',
        'contentFormat': 'markdown',
        'content': '# Hello World\n\nThis is my first post on Medium using **Markdown**.\n\n- Item 1\n- Item 2\n- Item 3\n\n[Visit Medium](https://medium.com)',
        'tags': ['markdown', 'api'],
        'publishStatus': 'public'
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print('Post created successfully!')
        print(response.json())
    else:
        print('Failed to create post')
        print(response.json())

if __name__ == "__main__":
    create_medium_blog() 