#!/usr/bin/env python3
"""
Test script to verify all components are ready for deployment.
"""

def test_deployment_readiness():
    print("🔍 Verificando preparación para despliegue...")
    
    try:
        # Test 1: Import main app
        from app.main import app
        print("✅ Aplicación FastAPI importada correctamente")
        
        # Test 2: Check configuration
        from app.core.config import settings
        print("✅ Configuración cargada correctamente")
        
        # Test 3: Check models
        from app.domain.models.user_model import User
        from app.domain.models.role_model import Role
        print("✅ Modelos de dominio importados correctamente")
        
        # Test 4: Check services  
        from app.application.services.auth_service import AuthService
        print("✅ Servicios de aplicación importados correctamente")
        
        # Test 5: Check routes
        from app.presentation.api.v1.router import api_router
        print("✅ Rutas de API importadas correctamente")
        
        print("\n🎉 ¡Todo listo para desplegar en Render!")
        print("📝 Recuerda configurar las variables de entorno en Render")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_deployment_readiness()