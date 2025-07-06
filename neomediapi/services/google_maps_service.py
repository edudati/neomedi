import os
import requests
from typing import Optional, Dict, Any, Tuple
from neomediapi.domain.address.exceptions import GoogleMapsError

class GoogleMapsService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise GoogleMapsError("GOOGLE_MAPS_API_KEY environment variable not set")
        
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address string to get coordinates and place details
        """
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "address": address,
                "key": self.api_key,
                "region": "br",  # Brazil
                "language": "pt-BR"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "OK":
                raise GoogleMapsError(f"Geocoding failed: {data['status']}")
            
            if not data["results"]:
                return None
            
            result = data["results"][0]
            
            # Extract coordinates
            location = result["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            
            # Extract place_id
            place_id = result["place_id"]
            
            # Extract formatted address
            formatted_address = result["formatted_address"]
            
            # Extract address components
            address_components = self._parse_address_components(result["address_components"])
            
            return {
                "latitude": lat,
                "longitude": lng,
                "place_id": place_id,
                "formatted_address": formatted_address,
                "address_components": address_components
            }
            
        except requests.RequestException as e:
            raise GoogleMapsError(f"Failed to call Google Maps API: {str(e)}")
        except Exception as e:
            raise GoogleMapsError(f"Unexpected error in geocoding: {str(e)}")
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to get address details
        """
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                "latlng": f"{latitude},{longitude}",
                "key": self.api_key,
                "region": "br",  # Brazil
                "language": "pt-BR"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "OK":
                raise GoogleMapsError(f"Reverse geocoding failed: {data['status']}")
            
            if not data["results"]:
                return None
            
            result = data["results"][0]
            
            # Extract place_id
            place_id = result["place_id"]
            
            # Extract formatted address
            formatted_address = result["formatted_address"]
            
            # Extract address components
            address_components = self._parse_address_components(result["address_components"])
            
            return {
                "place_id": place_id,
                "formatted_address": formatted_address,
                "address_components": address_components
            }
            
        except requests.RequestException as e:
            raise GoogleMapsError(f"Failed to call Google Maps API: {str(e)}")
        except Exception as e:
            raise GoogleMapsError(f"Unexpected error in reverse geocoding: {str(e)}")
    
    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a place using place_id
        """
        try:
            url = f"{self.base_url}/place/details/json"
            params = {
                "place_id": place_id,
                "key": self.api_key,
                "language": "pt-BR",
                "fields": "formatted_address,geometry,address_components,name"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "OK":
                raise GoogleMapsError(f"Place details failed: {data['status']}")
            
            result = data["result"]
            
            # Extract coordinates
            location = result["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            
            # Extract formatted address
            formatted_address = result["formatted_address"]
            
            # Extract address components
            address_components = self._parse_address_components(result["address_components"])
            
            return {
                "latitude": lat,
                "longitude": lng,
                "place_id": place_id,
                "formatted_address": formatted_address,
                "address_components": address_components,
                "name": result.get("name")
            }
            
        except requests.RequestException as e:
            raise GoogleMapsError(f"Failed to call Google Maps API: {str(e)}")
        except Exception as e:
            raise GoogleMapsError(f"Unexpected error getting place details: {str(e)}")
    
    def _parse_address_components(self, components: list) -> Dict[str, str]:
        """
        Parse Google Maps address components into a structured format
        """
        parsed = {}
        
        for component in components:
            types = component["types"]
            value = component["long_name"]
            
            if "street_number" in types:
                parsed["street_number"] = value
            elif "route" in types:
                parsed["street"] = value
            elif "sublocality_level_1" in types or "sublocality" in types:
                parsed["neighborhood"] = value
            elif "locality" in types:
                parsed["city"] = value
            elif "administrative_area_level_1" in types:
                parsed["state"] = value
            elif "postal_code" in types:
                parsed["postal_code"] = value
            elif "country" in types:
                parsed["country"] = value
        
        return parsed
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        import math
        
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    def search_nearby_places(self, latitude: float, longitude: float, radius: int = 5000, 
                           place_type: Optional[str] = None) -> list:
        """
        Search for nearby places
        """
        try:
            url = f"{self.base_url}/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "key": self.api_key,
                "language": "pt-BR"
            }
            
            if place_type:
                params["type"] = place_type
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "OK":
                raise GoogleMapsError(f"Nearby search failed: {data['status']}")
            
            return data["results"]
            
        except requests.RequestException as e:
            raise GoogleMapsError(f"Failed to call Google Maps API: {str(e)}")
        except Exception as e:
            raise GoogleMapsError(f"Unexpected error in nearby search: {str(e)}") 