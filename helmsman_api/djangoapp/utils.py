import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_jwt_token(user_id):
    exp_date = datetime.utcnow() + timedelta(days=1)
    payload = {
        'user_id': user_id,
        'exp': exp_date,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token, exp_date

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # Обработка исключения, если токен истек
        return {'error': 'Token has expired.'}
    except jwt.InvalidTokenError:
        # Обработка неверного токена
        return {'error': 'Invalid token.'}