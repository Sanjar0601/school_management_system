import requests

def get_location(ip_address):
    url = f'http://ip-api.com/json/{ip_address}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            location_info = {
                'IP': data['query'],
                'City': data['city'],
                'Region': data['regionName'],
                'Country': data['country'],
                'ZIP': data['zip'],
                'Latitude': data['lat'],
                'Longitude': data['lon']
            }
            return location_info
        else:
            return f"Error: {data['message']}"
    else:
        return f"Error: Unable to connect to API (status code: {response.status_code})"

if __name__ == '__main__':
    ip = input("Введите IP адрес: ")
    location = get_location(ip)
    print(location)
