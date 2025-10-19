import requests
from django.core.cache import cache

API_KEY = '5bd901f76e15af52438c84de'  # We'll move this later
BASE_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}'

def get_exchange_rate(from_currency, to_currency):
    """
    Get exchange rate between two currencies.
    Returns the conversion rate or None if error.
    """
    # Check cache first (rates are cached for 1 hour)
    cache_key = f'rate_{from_currency}_{to_currency}'
    cached_rate = cache.get(cache_key)
    
    if cached_rate:
        return cached_rate
    
    try:
        url = f'{BASE_URL}/pair/{from_currency}/{to_currency}'
        response = requests.get(url)
        data = response.json()
        
        if data['result'] == 'success':
            rate = data['conversion_rate']
            # Cache for 1 hour (3600 seconds)
            cache.set(cache_key, rate, 3600)
            return rate
        return None
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def convert_currency(amount, from_currency, to_currency):
    """
    Convert an amount from one currency to another.
    """
    if from_currency == to_currency:
        return amount
    
    rate = get_exchange_rate(from_currency, to_currency)
    if rate:
        return round(amount * rate, 2)
    return None

def get_supported_currencies():
    """
    Get list of supported currencies.
    """
    try:
        url = f'{BASE_URL}/codes'
        response = requests.get(url)
        data = response.json()
        
        if data['result'] == 'success':
            # Returns list of [code, name] pairs
            return data['supported_codes']
        return []
    except Exception as e:
        print(f"Error fetching currencies: {e}")
        return []
