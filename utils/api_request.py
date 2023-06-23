import requests
from config_data import config

headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def request(method: str, url: str, query_string: dict, timeout=10) -> requests.Response:
    """
    Посылаем запрос к серверу
    : param method : str
    : param url : str
    : param query_string : dict
    : param timeout : int (optional)
    : return : request.Response
    """
    try:
        if method == "GET":
            response = requests.get(url, params=query_string, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=query_string, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Invalid method: {method}")

        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
