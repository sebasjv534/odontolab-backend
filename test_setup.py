"""
Test script to verify the application setup.

This script performs basic tests to ensure the application is properly configured
and can start successfully.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

async def test_configuration():
    """Test application configuration."""
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print("✅ Configuration loaded successfully")
        print(f"   Project: {settings.PROJECT_NAME}")
        print(f"   Version: {settings.VERSION}")
        print(f"   Environment: {settings.ENVIRONMENT}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_database_models():
    """Test database models import."""
    try:
        from app.domain.models import (
            User, Role, RoleType,
            DentistProfile, ReceptionistProfile, AdministratorProfile,
            Patient, ClinicalRecord, Intervention,
            Gender, BloodType, InterventionType
        )
        print("✅ Database models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Database models error: {e}")
        return False

async def test_services():
    """Test services import."""
    try:
        from app.application.services.auth_service import AuthService
        from app.application.services.user_service import UserService
        from app.application.services.clinical_service import PatientService, ClinicalService
        print("✅ Services imported successfully")
        return True
    except Exception as e:
        print(f"❌ Services error: {e}")
        return False

async def test_repositories():
    """Test repositories import."""
    try:
        from app.insfraestructure.repositories import (
            UserRepository, RoleRepository,
            PatientRepository, ClinicalInterventionRepository
        )
        print("✅ Repositories imported successfully")
        return True
    except Exception as e:
        print(f"❌ Repositories error: {e}")
        return False

async def test_fastapi_app():
    """Test FastAPI app creation."""
    try:
        from app.main import app
        print("✅ FastAPI application created successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Testing OdontoLab Backend Setup\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Models", test_database_models),
        ("Services", test_services),
        ("Repositories", test_repositories),
        ("FastAPI App", test_fastapi_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        result = await test_func()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary")
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Next steps:")
        print("   1. Set up your .env file with database credentials")
        print("   2. Run: python init_db.py")
        print("   3. Start the server: uvicorn app.main:app --reload")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())