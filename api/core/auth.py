from fastapi import HTTPException, Header
from core.supabase_client import supabase

async def verify_token(authorization: str = Header(None)):
    """
    Validates the Supabase JWT and retrieves the user's organization.
    """
    if not supabase:
        return {"id": "dev_user", "organization_id": None}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Se requiere un token de sesión válido (Bearer Token)."
        )

    token = authorization.split(" ")[1]
    try:
        user_res = supabase.auth.get_user(token)
        if not user_res or not user_res.user:
            raise HTTPException(status_code=401, detail="Sesión expirada o inválida.")
        
        user_id = user_res.user.id
        profile_res = supabase.table("profiles").select("organization_id").eq("id", user_id).single().execute()
        
        if not profile_res.data:
            raise HTTPException(status_code=403, detail="Usuario no tiene un perfil configurado.")
            
        return {
            "id": user_id,
            "organization_id": profile_res.data.get("organization_id")
        }
    except Exception as e:
        print(f"🚨 Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Error en la validación de identidad.")
