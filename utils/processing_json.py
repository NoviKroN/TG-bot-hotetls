import json
from typing import Dict, Any


def get_city(response_text: str) -> Dict[str, Any]:
    data = json.loads(response_text)
    if not data:
        raise ValueError('Empty response from server')

    possible_cities = {}
    for id_place in data.get('sr', []):
        gaia_id = id_place.get('gaiaId')
        region_name = id_place.get('regionNames', {}).get('fullName')
        if gaia_id and region_name:
            possible_cities[gaia_id] = {
                "gaiaId": gaia_id,
                "regionNames": region_name
            }
    return possible_cities


def create_hotel_data(hotel: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return {
            'name': hotel['name'], 'id': hotel['id'],
            'distance': hotel['destinationInfo']['distanceFromDestination']['value'],
            'unit': hotel['destinationInfo']['distanceFromDestination']['unit'],
            'price': hotel['price']['lead']['amount']
        }
    except KeyError:
        return {}


def get_hotels(response_text: str, command: str, landmark_in: str, landmark_out: str) -> Dict[str, Any]:
    data = json.loads(response_text)
    if not data:
        raise ValueError('Empty response from server')

    if 'errors' in data:
        return {'error': data['errors'][0]['message']}

    hotels_data = {hotel['id']: create_hotel_data(hotel) for hotel in data['data']['propertySearch']['properties']}

    if command == '/highprice':
        hotels_data = {k: v for k, v in sorted(hotels_data.items(), key=lambda item: item[1]['price'], reverse=True)}
    elif command == '/bestdeal':
        hotels_data = {
            k: v for k, v in hotels_data.items() if float(landmark_in) < v['distance'] < float(landmark_out)
        }
    return hotels_data


def hotel_info(hotels_request: str) -> Dict[str, Any]:
    data = json.loads(hotels_request)
    if not data:
        raise ValueError('Empty response from server')

    hotel_data = {
        'id': data['data']['propertyInfo']['summary']['id'],
        'name': data['data']['propertyInfo']['summary']['name'],
        'address': data['data']['propertyInfo']['summary']['location']['address']['addressLine'],
        'coordinates': data['data']['propertyInfo']['summary']['location']['coordinates'],
        'images': [url['image']['url'] for url in data['data']['propertyInfo']['propertyGallery']['images']]
    }
    return hotel_data
