from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from src.services.maps_service import maps_service
import logging

logger = logging.getLogger(__name__)

maps_bp = Blueprint('maps', __name__, url_prefix='/api/maps')

def jwt_required_optional():
    """Decorator for optional JWT verification"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=True)
            except:
                pass
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@maps_bp.route('/geocode', methods=['POST'])
@jwt_required_optional()
def geocode_address():
    """Convert address to coordinates"""
    try:
        data = request.get_json()
        
        address = data.get('address', '').strip()
        city = data.get('city', 'cuiaba').lower()
        
        if not address:
            return jsonify({
                'success': False,
                'message': 'Endereço é obrigatório'
            }), 400
        
        result = maps_service.geocode_address(address, city)
        
        if result:
            return jsonify({
                'success': True,
                'location': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Endereço não encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error geocoding address: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar localização'
        }), 500

@maps_bp.route('/reverse-geocode', methods=['POST'])
@jwt_required_optional()
def reverse_geocode():
    """Convert coordinates to address"""
    try:
        data = request.get_json()
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({
                'success': False,
                'message': 'Latitude e longitude são obrigatórias'
            }), 400
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Coordenadas inválidas'
            }), 400
        
        result = maps_service.reverse_geocode(latitude, longitude)
        
        if result:
            return jsonify({
                'success': True,
                'location': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Localização não encontrada'
            }), 404
            
    except Exception as e:
        logger.error(f"Error reverse geocoding: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar endereço'
        }), 500

@maps_bp.route('/nearby-complaints', methods=['GET'])
@jwt_required_optional()
def get_nearby_complaints():
    """Get complaints near a location"""
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius_km = request.args.get('radius', 1.0, type=float)
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        if latitude is None or longitude is None:
            return jsonify({
                'success': False,
                'message': 'Latitude e longitude são obrigatórias'
            }), 400
        
        # Limit radius to reasonable values
        radius_km = min(max(radius_km, 0.1), 10.0)
        
        complaints = maps_service.get_nearby_complaints(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'complaints': complaints,
            'search_params': {
                'latitude': latitude,
                'longitude': longitude,
                'radius_km': radius_km,
                'limit': limit
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting nearby complaints: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar reclamações próximas'
        }), 500

@maps_bp.route('/heatmap', methods=['GET'])
@jwt_required_optional()
def get_heatmap_data():
    """Get complaint data for heatmap visualization"""
    try:
        city = request.args.get('city', 'cuiaba').lower()
        status_filter = request.args.get('status', 'all').lower()
        
        # Validate status filter
        valid_statuses = ['all', 'pendente', 'em_andamento', 'resolvida', 'respondida']
        if status_filter not in valid_statuses:
            status_filter = 'all'
        
        heatmap_data = maps_service.get_complaints_heatmap_data(
            city=city,
            status_filter=status_filter
        )
        
        return jsonify({
            'success': True,
            'heatmap_data': heatmap_data,
            'filters': {
                'city': city,
                'status': status_filter
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting heatmap data: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar dados do mapa de calor'
        }), 500

@maps_bp.route('/city-stats', methods=['GET'])
@jwt_required_optional()
def get_city_statistics():
    """Get geographical statistics for a city"""
    try:
        city = request.args.get('city', 'cuiaba').lower()
        
        stats = maps_service.get_city_statistics(city)
        
        return jsonify({
            'success': True,
            'city': city,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting city statistics: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar estatísticas da cidade'
        }), 500

@maps_bp.route('/route-to-complaint/<int:complaint_id>', methods=['GET'])
@jwt_required_optional()
def get_route_to_complaint(complaint_id):
    """Get route from user location to complaint"""
    try:
        start_lat = request.args.get('start_lat', type=float)
        start_lng = request.args.get('start_lng', type=float)
        
        if start_lat is None or start_lng is None:
            return jsonify({
                'success': False,
                'message': 'Localização de origem é obrigatória'
            }), 400
        
        route = maps_service.get_route_to_complaint(
            start_lat=start_lat,
            start_lng=start_lng,
            complaint_id=complaint_id
        )
        
        if route:
            return jsonify({
                'success': True,
                'route': route
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Reclamação não encontrada ou sem localização'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting route to complaint: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao calcular rota'
        }), 500

@maps_bp.route('/validate-coordinates', methods=['POST'])
@jwt_required_optional()
def validate_coordinates():
    """Validate if coordinates are reasonable for the city"""
    try:
        data = request.get_json()
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        city = data.get('city', 'cuiaba').lower()
        
        if latitude is None or longitude is None:
            return jsonify({
                'success': False,
                'message': 'Latitude e longitude são obrigatórias'
            }), 400
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Coordenadas inválidas'
            }), 400
        
        validation_result = maps_service.validate_coordinates(
            latitude=latitude,
            longitude=longitude,
            city=city
        )
        
        return jsonify({
            'success': True,
            'validation': validation_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error validating coordinates: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao validar coordenadas'
        }), 500

@maps_bp.route('/popular-locations', methods=['GET'])
@jwt_required_optional()
def get_popular_locations():
    """Get most popular locations for complaints"""
    try:
        city = request.args.get('city', 'cuiaba').lower()
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        locations = maps_service.get_popular_locations(
            city=city,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'popular_locations': locations,
            'city': city
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting popular locations: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar locais populares'
        }), 500

@maps_bp.route('/city-bounds', methods=['GET'])
@jwt_required_optional()
def get_city_bounds():
    """Get city boundaries and center"""
    try:
        city = request.args.get('city', 'cuiaba').lower()
        
        # Get default bounds from maps service
        bounds_data = maps_service.default_city_bounds.get(city)
        
        if bounds_data:
            return jsonify({
                'success': True,
                'city': city,
                'center': bounds_data['center'],
                'bounds': bounds_data['bounds']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Cidade não encontrada'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting city bounds: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar limites da cidade'
        }), 500

# Admin routes for maps management
@maps_bp.route('/admin/hotspots', methods=['GET'])
@jwt_required()
def get_hotspots():
    """Get complaint hotspots (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is admin
        from src.models.user import User
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'gestor_publico':
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        city = request.args.get('city', 'cuiaba').lower()
        
        stats = maps_service.get_city_statistics(city)
        hotspots = stats.get('hotspots', [])
        
        return jsonify({
            'success': True,
            'city': city,
            'hotspots': hotspots,
            'total_complaints': stats.get('total_complaints', 0)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting hotspots: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar pontos críticos'
        }), 500

@maps_bp.route('/admin/coverage-analysis', methods=['GET'])
@jwt_required()
def get_coverage_analysis():
    """Get geographical coverage analysis (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is admin
        from src.models.user import User
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'gestor_publico':
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        city = request.args.get('city', 'cuiaba').lower()
        
        from src.models.complaint import Complaint
        from sqlalchemy import func
        
        # Get complaints by region/neighborhood
        coverage_data = Complaint.query.filter(
            Complaint.city == city,
            Complaint.latitude.isnot(None),
            Complaint.longitude.isnot(None)
        ).with_entities(
            Complaint.location,
            func.count(Complaint.id).label('complaint_count'),
            func.avg(Complaint.latitude).label('avg_lat'),
            func.avg(Complaint.longitude).label('avg_lng')
        ).group_by(
            Complaint.location
        ).order_by(
            func.count(Complaint.id).desc()
        ).limit(20).all()
        
        coverage_analysis = []
        for data in coverage_data:
            coverage_analysis.append({
                'location': data.location,
                'complaint_count': data.complaint_count,
                'center': {
                    'latitude': float(data.avg_lat),
                    'longitude': float(data.avg_lng)
                }
            })
        
        return jsonify({
            'success': True,
            'city': city,
            'coverage_analysis': coverage_analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting coverage analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao analisar cobertura geográfica'
        }), 500

