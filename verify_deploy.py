#!/usr/bin/env python
"""
Script de verificación pre-despliegue para Render.
Verifica que todos los archivos y configuraciones estén listos.
"""

import os
import sys
from pathlib import Path


def print_header(text: str):
    """Imprime un encabezado formateado."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_success(text: str):
    """Imprime mensaje de éxito."""
    print(f"✅ {text}")


def print_error(text: str):
    """Imprime mensaje de error."""
    print(f"❌ {text}")


def print_warning(text: str):
    """Imprime mensaje de advertencia."""
    print(f"⚠️  {text}")


def print_info(text: str):
    """Imprime mensaje informativo."""
    print(f"ℹ️  {text}")


def check_file_exists(file_path: str, required: bool = True) -> bool:
    """Verifica si un archivo existe."""
    exists = Path(file_path).exists()
    if exists:
        print_success(f"Archivo encontrado: {file_path}")
    elif required:
        print_error(f"Archivo requerido no encontrado: {file_path}")
    else:
        print_warning(f"Archivo opcional no encontrado: {file_path}")
    return exists


def check_requirements():
    """Verifica que las dependencias estén en requirements.txt."""
    print_header("Verificando Dependencias")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'asyncpg',
        'psycopg',
        'python-jose',
        'passlib',
        'gunicorn',
        'pydantic',
        'pydantic-settings'
    ]
    
    if not Path('requirements.txt').exists():
        print_error("requirements.txt no encontrado!")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    missing = []
    for package in required_packages:
        if package.lower() in content:
            print_success(f"Paquete encontrado: {package}")
        else:
            print_error(f"Paquete faltante: {package}")
            missing.append(package)
    
    if missing:
        print_error(f"\nPaquetes faltantes: {', '.join(missing)}")
        return False
    
    return True


def check_render_yaml():
    """Verifica la configuración de render.yaml."""
    print_header("Verificando render.yaml")
    
    if not Path('render.yaml').exists():
        print_error("render.yaml no encontrado!")
        return False
    
    with open('render.yaml', 'r') as f:
        content = f.read()
    
    checks = [
        ('databases:', 'Configuración de base de datos'),
        ('plan: free', 'Plan gratuito configurado'),
        ('services:', 'Servicios definidos'),
        ('type: web', 'Servicio web definido'),
        ('buildCommand:', 'Comando de build definido'),
        ('startCommand:', 'Comando de start definido'),
        ('gunicorn', 'Gunicorn en start command'),
        ('uvicorn.workers.UvicornWorker', 'Worker de Uvicorn configurado'),
    ]
    
    all_ok = True
    for check_str, description in checks:
        if check_str in content:
            print_success(description)
        else:
            print_error(f"{description} - No encontrado: '{check_str}'")
            all_ok = False
    
    # Verificar configuración optimizada para free tier
    if '-w 1' in content or '-w1' in content:
        print_success("Worker único configurado (optimizado para free tier)")
    else:
        print_warning("Considerar usar solo 1 worker (-w 1) para plan gratuito")
    
    if '--timeout' in content:
        print_success("Timeout configurado")
    else:
        print_warning("Considerar agregar --timeout 300")
    
    return all_ok


def check_database_config():
    """Verifica la configuración de base de datos."""
    print_header("Verificando Configuración de Base de Datos")
    
    config_file = Path('app/core/config.py')
    if not config_file.exists():
        print_error("app/core/config.py no encontrado!")
        return False
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    checks = [
        ('DATABASE_URL', 'Variable DATABASE_URL definida'),
        ('SECRET_KEY', 'Variable SECRET_KEY definida'),
        ('ALGORITHM', 'Variable ALGORITHM definida'),
        ('CORS_ORIGINS', 'Variable CORS_ORIGINS definida'),
    ]
    
    all_ok = True
    for check_str, description in checks:
        if check_str in content:
            print_success(description)
        else:
            print_error(description + " - No encontrada")
            all_ok = False
    
    return all_ok


def check_database_optimizations():
    """Verifica optimizaciones de base de datos."""
    print_header("Verificando Optimizaciones de Base de Datos")
    
    database_file = Path('app/core/database.py')
    if not database_file.exists():
        print_error("app/core/database.py no encontrado!")
        return False
    
    with open(database_file, 'r') as f:
        content = f.read()
    
    optimizations = [
        ('pool_size', 'Pool size configurado'),
        ('max_overflow', 'Max overflow configurado'),
        ('pool_pre_ping', 'Pre-ping habilitado'),
        ('pool_recycle', 'Pool recycle configurado'),
        ('timeout', 'Timeout configurado'),
    ]
    
    for opt, description in optimizations:
        if opt in content:
            print_success(description)
        else:
            print_warning(f"{description} - No encontrado")
    
    return True


def check_init_script():
    """Verifica el script de inicialización."""
    print_header("Verificando Script de Inicialización")
    
    if check_file_exists('init_db_render.py'):
        with open('init_db_render.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('async def', 'Funciones asíncronas'),
            ('wait_for_db', 'Función de espera de DB'),
            ('Base.metadata.create_all', 'Creación de tablas'),
            ('User', 'Modelo de usuario'),
            ('hash_password', 'Hashing de contraseñas'),
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print_success(description)
            else:
                print_warning(f"{description} - No encontrado")
        
        return True
    
    return False


def check_project_structure():
    """Verifica la estructura del proyecto."""
    print_header("Verificando Estructura del Proyecto")
    
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/core/__init__.py',
        'app/core/config.py',
        'app/core/database.py',
        'app/core/security.py',
        'app/domain/models/__init__.py',
        'app/domain/schemas/__init__.py',
        'app/presentation/api/__init__.py',
    ]
    
    all_ok = True
    for file_path in required_files:
        if not check_file_exists(file_path):
            all_ok = False
    
    return all_ok


def check_env_example():
    """Verifica el archivo .env.example."""
    print_header("Verificando .env.example")
    
    if not Path('.env.example').exists():
        print_warning(".env.example no encontrado (opcional pero recomendado)")
        return True
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'ALGORITHM',
        'CORS_ORIGINS',
        'DEBUG',
        'ENVIRONMENT'
    ]
    
    for var in required_vars:
        if var in content:
            print_success(f"Variable de ejemplo: {var}")
        else:
            print_warning(f"Variable no documentada: {var}")
    
    return True


def check_gitignore():
    """Verifica que .env esté en .gitignore."""
    print_header("Verificando .gitignore")
    
    if not Path('.gitignore').exists():
        print_error(".gitignore no encontrado!")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    if '.env' in content:
        print_success(".env está en .gitignore (correcto)")
    else:
        print_error(".env NO está en .gitignore (PELIGRO DE SEGURIDAD)")
        return False
    
    dangerous_patterns = [
        ('*.pyc', 'Archivos compilados de Python'),
        ('__pycache__', 'Cache de Python'),
        ('.vscode', 'Configuración de IDE'),
    ]
    
    for pattern, description in dangerous_patterns:
        if pattern in content:
            print_success(f"{description} ignorado")
        else:
            print_info(f"{description} podría agregarse")
    
    return True


def print_summary(checks_passed: int, total_checks: int):
    """Imprime resumen final."""
    print_header("Resumen de Verificación")
    
    percentage = (checks_passed / total_checks) * 100
    
    print(f"Verificaciones pasadas: {checks_passed}/{total_checks} ({percentage:.1f}%)\n")
    
    if checks_passed == total_checks:
        print_success("¡TODO LISTO PARA DESPLEGAR! 🚀")
        print_info("\nPróximos pasos:")
        print("   1. Sube los cambios a GitHub: git push origin main")
        print("   2. Ve a Render Dashboard: https://dashboard.render.com")
        print("   3. Crea un nuevo Blueprint o Web Service")
        print("   4. Ejecuta 'python init_db_render.py' desde Render Shell")
        print("   5. Verifica /health endpoint")
        print("\n   📚 Ver DEPLOY_QUICK.md para guía detallada")
    elif percentage >= 80:
        print_warning("Casi listo, revisa las advertencias arriba")
        print_info("Puedes proceder con el despliegue, pero considera resolver las advertencias")
    else:
        print_error("Hay problemas que deben resolverse antes de desplegar")
        print_info("Revisa los errores marcados con ❌ arriba")


def main():
    """Función principal."""
    print_header("🔍 OdontoLab - Verificación Pre-Despliegue para Render")
    
    checks = [
        ("Archivos del Proyecto", check_project_structure),
        ("requirements.txt", check_requirements),
        ("render.yaml", check_render_yaml),
        ("Configuración de DB", check_database_config),
        ("Optimizaciones de DB", check_database_optimizations),
        ("Script de Inicialización", check_init_script),
        (".env.example", check_env_example),
        (".gitignore", check_gitignore),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print_error(f"Error en verificación de {name}: {str(e)}")
            results.append(False)
    
    checks_passed = sum(results)
    total_checks = len(checks)
    
    print_summary(checks_passed, total_checks)
    
    return 0 if checks_passed == total_checks else 1


if __name__ == '__main__':
    sys.exit(main())
