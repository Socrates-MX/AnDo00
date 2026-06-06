from fastapi import HTTPException, Header
from core.supabase_client import supabase
import base64
import json

async def verify_token(
    authorization: str = Header(None),
    x_apigateway_api_userinfo: str = Header(None)
):
    """
    Validates identity from API Gateway or falls back to Supabase directly.
    """
    if not supabase:
        return {"id": "dev_user", "organization_id": None}
    
    user_id = None

    if x_apigateway_api_userinfo:
        try:
            padding = '=' * ((4 - len(x_apigateway_api_userinfo) % 4) % 4)
            decoded_bytes = base64.urlsafe_b64decode(x_apigateway_api_userinfo + padding)
            payload = json.loads(decoded_bytes.decode('utf-8'))
            user_id = payload.get("sub")
        except Exception as e:
            print(f"🚨 API Gateway Userinfo Error: {e}")
            raise HTTPException(status_code=401, detail="Error decodificando identidad del Gateway.")
            
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            user_res = supabase.auth.get_user(token)
            if not user_res or not user_res.user:
                raise HTTPException(status_code=401, detail="Sesión expirada o inválida.")
            user_id = user_res.user.id
        except Exception as e:
            print(f"🚨 Local Auth Error: {e}")
            raise HTTPException(status_code=401, detail="Error en la validación de identidad.")
            
    if not user_id:
        raise HTTPException(
            status_code=401, 
            detail="Se requiere un token de sesión válido (Bearer Token o Gateway)."
        )

    try:
        profile_res = supabase.table("profiles").select("organization_id").eq("id", user_id).single().execute()
        if not profile_res.data:
            raise HTTPException(status_code=403, detail="Usuario no tiene un perfil configurado.")
            
        return {
            "id": user_id,
            "organization_id": profile_res.data.get("organization_id")
        }
    except Exception as e:
        print(f"🚨 Profile DB Error: {e}")
        raise HTTPException(status_code=403, detail="Usuario no tiene un perfil configurado o falló BD.")
