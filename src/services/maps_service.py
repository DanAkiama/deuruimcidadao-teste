import requests
import logging
from typing import Dict, List, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json

logger = logging.getLogger(__name__)

class MapsService:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize maps service with Flask app"""
        self.google_maps_api_key = app.config.get('GOOGLE_MAPS_API_KEY', '')
        self.geocoder = Nominatim(user_agent="deuruimcidadao")
        
        # Default city boundaries (Cuiabá, MT)
        self.default_city_bounds = {
            'cuiaba': {
                'center': (-15.6014, -56.0979),
                'bounds': {
                    'north': -15.4000,
                    'south': -15.8000,
                    'east': -55.8000,
                    'west': -56.4000
                }
            },
            'varzea-grande': {
                'center': (-15.6467, -56.1326),
                'bounds': {
                    'north': -15.5000,
                    'south': -15.8000,
                    'east': -55.9000,
                    'west': -56.3000
                }
            }
        }
    
    def geocode_address(self, address: str, city: str = 'cuiaba') -> Optional[Dict]:
        """Convert address to coordinates"""
        try:
            # Add city context to improve accuracy
            full_address = f"{address}, {city}, Mato Grosso, Brasil"
            
            location = self.geocoder.geocode(full_address, timeout=10)
            
            if location:
                # Verify if location is within city bounds
                if self._is_within_city_bounds(location.latitude, location.longitude, city):
                    return {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'formatted_address': location.address,
                        'confidence': 'high'
                    }
                else:
                    logger.warning(f"Address '{address}' is outside {city} bounds")
                    return {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'formatted_address': location.address,
                        'confidence': 'low'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {str(e)}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Convert coordinates to address"""
        try:
            location = self.geocoder.reverse((latitude, longitude), timeout=10)
            
            if location:
                return {
                    'formatted_address': location.address,
                    'latitude': latitude,
                    'longitude': longitude
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}): {str(e)}")
            return None
    
    def _is_within_city_bounds(self, latitude: float, longitude: float, city: str) -> bool:
        """Check if coordinates are within city bounds"""
        if city not in self.default_city_bounds:
            return True  # If we don't have bounds, assume it's valid
        
        bounds = self.default_city_bounds[city]['bounds']
        
        return (bounds['south'] <= latitude <= bounds['north'] and
                bounds['west'] <= longitude <= bounds['east'])
    
    def get_nearby_complaints(self, latitude: float, longitude: float, 
                            radius_km: float = 1.0, limit: int = 10) -> List[Dict]:
        """Get complaints near a location"""
        try:
            from src.models.complaint import Complaint
            
            # Get all complaints with coordinates
            complaints = Complaint.query.filter(
                Complaint.latitude.isnot(None),
                Complaint.longitude.isnot(None)
            ).all()
            
            nearby_complaints = []
            user_location = (latitude, longitude)
            
            for complaint in complaints:
                complaint_location = (complaint.latitude, complaint.longitude)
                distance = geodesic(user_location, complaint_location).kilometers
                
                if distance <= radius_km:
                    complaint_data = complaint.to_dict()
                    complaint_data['distance_km'] = round(distance, 2)
                    nearby_complaints.append(complaint_data)
            
            # Sort by distance and limit results
            nearby_complaints.sort(key=lambda x: x['distance_km'])
            return nearby_complaints[:limit]
            
        except Exception as e:
            logger.error(f"Error getting nearby complaints: {str(e)}")
            return []
    
    def get_complaints_heatmap_data(self, city: str = 'cuiaba', 
                                  status_filter: str = 'all') -> List[Dict]:
        """Get complaint data for heatmap visualization"""
        try:
            from src.models.complaint import Complaint
            
            query = Complaint.query.filter(
                Complaint.latitude.isnot(None),
                Complaint.longitude.isnot(None),
                Complaint.city == city
            )
            
            # Apply status filter
            if status_filter != 'all':
                query = query.filter(Complaint.status == status_filter)
            
            complaints = query.all()
            
            heatmap_data = []
            for complaint in complaints:
                # Weight based on priority and votes
                weight = 1
                if complaint.priority == 'urgent':
                    weight = 4
                elif complaint.priority == 'high':
                    weight = 3
                elif complaint.priority == 'medium':
                    weight = 2
                
                # Add vote weight
                weight += min(complaint.votes_count / 10, 2)  # Max 2 extra points from votes
                
                heatmap_data.append({
                    'lat': complaint.latitude,
                    'lng': complaint.longitude,
                    'weight': weight,
                    'complaint_id': complaint.id,
                    'title': complaint.title,
                    'category': complaint.category,
                    'status': complaint.status,
                    'priority': complaint.priority,
                    'votes_count': complaint.votes_count
                })
            
            return heatmap_data
            
        except Exception as e:
            logger.error(f"Error getting heatmap data: {str(e)}")
            return []
    
    def get_city_statistics(self, city: str = 'cuiaba') -> Dict:
        """Get geographical statistics for a city"""
        try:
            from src.models.complaint import Complaint
            
            complaints = Complaint.query.filter(
                Complaint.city == city,
                Complaint.latitude.isnot(None),
                Complaint.longitude.isnot(None)
            ).all()
            
            if not complaints:
                return {
                    'total_complaints': 0,
                    'center': self.default_city_bounds.get(city, {}).get('center', (-15.6014, -56.0979)),
                    'hotspots': []
                }
            
            # Calculate center based on complaints
            avg_lat = sum(c.latitude for c in complaints) / len(complaints)
            avg_lng = sum(c.longitude for c in complaints) / len(complaints)
            
            # Find hotspots (areas with high complaint density)
            hotspots = self._find_hotspots(complaints)
            
            return {
                'total_complaints': len(complaints),
                'center': (avg_lat, avg_lng),
                'hotspots': hotspots,
                'bounds': self.default_city_bounds.get(city, {}).get('bounds', {})
            }
            
        except Exception as e:
            logger.error(f"Error getting city statistics: {str(e)}")
            return {
                'total_complaints': 0,
                'center': (-15.6014, -56.0979),
                'hotspots': []
            }
    
    def _find_hotspots(self, complaints: List, radius_km: float = 0.5) -> List[Dict]:
        """Find areas with high complaint density"""
        hotspots = []
        processed_complaints = set()
        
        for i, complaint in enumerate(complaints):
            if i in processed_complaints:
                continue
            
            complaint_location = (complaint.latitude, complaint.longitude)
            nearby_complaints = [complaint]
            nearby_indices = {i}
            
            # Find nearby complaints
            for j, other_complaint in enumerate(complaints):
                if j == i or j in processed_complaints:
                    continue
                
                other_location = (other_complaint.latitude, other_complaint.longitude)
                distance = geodesic(complaint_location, other_location).kilometers
                
                if distance <= radius_km:
                    nearby_complaints.append(other_complaint)
                    nearby_indices.add(j)
            
            # If we found a cluster (3+ complaints), create a hotspot
            if len(nearby_complaints) >= 3:
                # Calculate center of cluster
                center_lat = sum(c.latitude for c in nearby_complaints) / len(nearby_complaints)
                center_lng = sum(c.longitude for c in nearby_complaints) / len(nearby_complaints)
                
                # Count by category
                categories = {}
                for c in nearby_complaints:
                    categories[c.category] = categories.get(c.category, 0) + 1
                
                hotspots.append({
                    'center': (center_lat, center_lng),
                    'complaint_count': len(nearby_complaints),
                    'radius_km': radius_km,
                    'categories': categories,
                    'top_category': max(categories.items(), key=lambda x: x[1])[0]
                })
                
                # Mark these complaints as processed
                processed_complaints.update(nearby_indices)
        
        # Sort hotspots by complaint count
        hotspots.sort(key=lambda x: x['complaint_count'], reverse=True)
        return hotspots[:10]  # Return top 10 hotspots
    
    def get_route_to_complaint(self, start_lat: float, start_lng: float, 
                             complaint_id: int) -> Optional[Dict]:
        """Get route from start location to complaint location"""
        try:
            from src.models.complaint import Complaint
            
            complaint = Complaint.query.get(complaint_id)
            if not complaint or not complaint.latitude or not complaint.longitude:
                return None
            
            # Calculate straight-line distance
            start_location = (start_lat, start_lng)
            end_location = (complaint.latitude, complaint.longitude)
            distance = geodesic(start_location, end_location).kilometers
            
            # For demo purposes, return basic route info
            # In production, you would use Google Maps Directions API
            return {
                'distance_km': round(distance, 2),
                'estimated_time_minutes': max(5, int(distance * 3)),  # Rough estimate
                'start_location': {
                    'lat': start_lat,
                    'lng': start_lng
                },
                'end_location': {
                    'lat': complaint.latitude,
                    'lng': complaint.longitude
                },
                'complaint': {
                    'id': complaint.id,
                    'title': complaint.title,
                    'address': complaint.location
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting route to complaint {complaint_id}: {str(e)}")
            return None
    
    def validate_coordinates(self, latitude: float, longitude: float, city: str = 'cuiaba') -> Dict:
        """Validate if coordinates are reasonable for the city"""
        try:
            # Check if coordinates are within reasonable bounds
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return {
                    'valid': False,
                    'reason': 'Coordinates out of valid range'
                }
            
            # Check if within city bounds
            if not self._is_within_city_bounds(latitude, longitude, city):
                return {
                    'valid': False,
                    'reason': f'Coordinates outside {city} boundaries'
                }
            
            # Try to reverse geocode to get address
            address_info = self.reverse_geocode(latitude, longitude)
            
            return {
                'valid': True,
                'address': address_info.get('formatted_address', '') if address_info else '',
                'within_city_bounds': True
            }
            
        except Exception as e:
            logger.error(f"Error validating coordinates: {str(e)}")
            return {
                'valid': False,
                'reason': 'Error validating coordinates'
            }
    
    def get_popular_locations(self, city: str = 'cuiaba', limit: int = 10) -> List[Dict]:
        """Get most popular locations for complaints"""
        try:
            from src.models.complaint import Complaint
            from sqlalchemy import func
            
            # Group complaints by approximate location (rounded coordinates)
            results = Complaint.query.filter(
                Complaint.city == city,
                Complaint.latitude.isnot(None),
                Complaint.longitude.isnot(None)
            ).with_entities(
                func.round(Complaint.latitude, 3).label('lat_rounded'),
                func.round(Complaint.longitude, 3).label('lng_rounded'),
                func.count(Complaint.id).label('complaint_count'),
                func.max(Complaint.location).label('location_name')
            ).group_by(
                func.round(Complaint.latitude, 3),
                func.round(Complaint.longitude, 3)
            ).order_by(
                func.count(Complaint.id).desc()
            ).limit(limit).all()
            
            popular_locations = []
            for result in results:
                popular_locations.append({
                    'latitude': float(result.lat_rounded),
                    'longitude': float(result.lng_rounded),
                    'complaint_count': result.complaint_count,
                    'location_name': result.location_name
                })
            
            return popular_locations
            
        except Exception as e:
            logger.error(f"Error getting popular locations: {str(e)}")
            return []

# Global maps service instance
maps_service = MapsService()

