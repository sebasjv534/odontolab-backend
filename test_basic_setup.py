#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the basic setup of the OdontoLab API.
This script performs basic imports without requiring database connection.
"""

import sys
import os

def test_basic_imports():
    """Test basic imports without database connection."""
    print("🔧 Testing OdontoLab API Setup...")
    print("=" * 50)
    
    try:
        # Test configuration (without instantiating settings)
        print("1. Testing configuration module...")
        from app.core.config import Settings
        print("   ✓ Configuration module imported successfully")
        
        # Test security module
        print("2. Testing security module...")
        from app.core.security import create_access_token, verify_password, hash_password
        print("   ✓ Security module imported successfully")
        
        # Test schemas
        print("3. Testing schema modules...")
        from app.domain.schemas.auth_schemas import TokenResponse, TokenData, LoginRequest
        from app.domain.schemas.user_schemas import UserCreateBase, AdminCreateUserRequest
        print("   ✓ Schema modules imported successfully")
        
        # Test services (without database dependencies)
        print("4. Testing service interfaces...")
        from app.application.interfaces.user_repository import IUserRepository
        from app.application.interfaces.clinical_repository import IPatientRepository, IClinicalInterventionRepository
        print("   ✓ Service interfaces imported successfully")
        
        print("\n🎉 Basic setup verification completed successfully!")
        print("✅ All core modules are properly configured")
        print("\nNext steps:")
        print("- Install asyncpg: pip install asyncpg")
        print("- Configure PostgreSQL database")
        print("- Run database migrations")
        print("- Implement API routes")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_imports()
    sys.exit(0 if success else 1)