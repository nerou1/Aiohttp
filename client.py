from aiohttp import ClientSession

async def main():
    data = {
        'email': 'asd@dsa.eu',
        'name': 'Asd Dsa',
        'password': '12345'
    }
    async with ClientSession() as session:
        async with session.post('http://127.0.0.1:8080/user', json_data=data) as response:
            result = await response.json()
    print(result)