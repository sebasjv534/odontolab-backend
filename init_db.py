""""""

Database initialization script for the OdontoLab system.Database initialization script for the odontology system.



This script creates the database tables and seeds initial data following the API_SUMMARY.md specifications.This script creates the database tables and initializes default roles

"""and a default administrator user.

"""

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSessionimport asyncio

from sqlalchemy.orm import sessionmakerimport uuid

from sqlalchemy.future import selectfrom sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy.orm import sessionmaker

from app.core.database import Base

from app.core.config import get_settingsfrom app.core.database import Base

from app.core.security import hash_passwordfrom app.core.config import get_settings

from app.domain.models import User, UserRole, Patient, ContactRequest, ContactStatusfrom app.domain.models.role_model import Role, RoleType

from app.domain.models.user_model import User

from app.domain.models.profile_models import AdministratorProfile

async def create_tables(engine):from app.core.security import hash_password

    """Create all database tables."""

    async with engine.begin() as conn:

        print("Creating database tables...")async def init_database():

        await conn.run_sync(Base.metadata.drop_all)    """

        await conn.run_sync(Base.metadata.create_all)    Initialize the database with tables and default data.

        print("✓ Database tables created successfully!")    """

    settings = get_settings()

    

async def seed_users(session: AsyncSession):    # Create async engine

    """Create initial users with different roles."""    engine = create_async_engine(

    print("\nCreating default users...")        settings.DATABASE_URL,

            echo=True

    # Check if users already exist    )

    result = await session.execute(select(User))    

    existing_users = result.scalars().all()    # Create all tables

        async with engine.begin() as conn:

    if existing_users:        await conn.run_sync(Base.metadata.create_all)

        print("✗ Users already exist. Skipping user creation.")    

        return    # Create async session

        async_session = sessionmaker(

    users = [        engine, class_=AsyncSession, expire_on_commit=False

        {    )

            "nombre": "Administrador Principal",    

            "email": "admin@odontolab.com",    async_session = sessionmaker(

            "password": "admin123",        engine, class_=AsyncSession, expire_on_commit=False

            "role": UserRole.ADMIN,    )

            "is_active": True    

        },    async with async_session() as session:

        {        # Check if roles already exist

            "nombre": "Dr. Juan Pérez",        from sqlalchemy.future import select

            "email": "dentista@odontolab.com",        result = await session.execute(select(Role))

            "password": "dentista123",        existing_roles = result.scalars().all()

            "role": UserRole.DENTIST,        

            "is_active": True        if not existing_roles:

        },            print("Creating default roles...")

        {            

            "nombre": "María González",            # Create default roles

            "email": "recepcion@odontolab.com",            roles = [

            "password": "recepcion123",                Role(

            "role": UserRole.RECEPTIONIST,                    id=uuid.uuid4(),

            "is_active": True                    name=RoleType.ADMINISTRATOR.value,

        }                    description="System administrator with full access",

    ]                    permissions='{"all": true}'

                    ),

    created_users = []                Role(

    for user_data in users:                    id=uuid.uuid4(),

        password = user_data.pop("password")                    name=RoleType.DENTIST.value,

        user = User(                    description="Dentist with access to clinical records and interventions",

            **user_data,                    permissions='{"clinical": true, "patients": true}'

            hashed_password=hash_password(password)                ),

        )                Role(

        session.add(user)                    id=uuid.uuid4(),

        created_users.append(user)                    name=RoleType.RECEPTIONIST.value,

                        description="Receptionist with access to patient management",

    await session.commit()                    permissions='{"patients": true, "appointments": true}'

                    )

    print("✓ Default users created successfully!")            ]

    print("\n=== Default User Credentials ===")            

    for user_data in users:            for role in roles:

        print(f"Email: {user_data['email']}")                session.add(role)

        print(f"Password: admin123 / dentista123 / recepcion123")            

        print(f"Role: {user_data['role'].value}")            await session.commit()

        print("-" * 40)            print("Default roles created successfully!")

                

    return created_users            # Get administrator role

            admin_role_result = await session.execute(

                select(Role).where(Role.name == RoleType.ADMINISTRATOR.value)

async def seed_patients(session: AsyncSession, receptionist_id):            )

    """Create sample patients."""            admin_role = admin_role_result.scalar_one()

    print("\nCreating sample patients...")            

                # Check if admin user exists

    # Check if patients already exist            admin_user_result = await session.execute(

    result = await session.execute(select(Patient))                select(User).where(User.email == "admin@odontolab.com")

    existing_patients = result.scalars().all()            )

                existing_admin = admin_user_result.scalar_one_or_none()

    if existing_patients:            

        print("✗ Patients already exist. Skipping patient creation.")            if not existing_admin:

        return                print("Creating default administrator user...")

                    

    patients = [                # Create default admin user

        {                admin_user = User(

            "nombre": "Carlos Rodríguez",                    id=uuid.uuid4(),

            "cedula": "1234567890",                    email="admin@odontolab.com",

            "email": "carlos@example.com",                    password_hash=hash_password("admin123456"),

            "telefono": "555-0101",                    first_name="System",

            "direccion": "Calle Principal #123",                    last_name="Administrator",

            "fecha_nacimiento": "1985-03-15",                    is_active=True,

            "genero": "M",                    is_verified=True,

            "nombre_contacto_emergencia": "Ana Rodríguez",                    role_id=admin_role.id

            "telefono_contacto_emergencia": "555-0102",                )

            "condiciones_medicas": "Ninguna",                

            "alergias": "Ninguna",                session.add(admin_user)

            "created_by": receptionist_id                await session.commit()

        },                await session.refresh(admin_user)

        {                

            "nombre": "Laura Martínez",                # Create administrator profile

            "cedula": "0987654321",                admin_profile = AdministratorProfile(

            "email": "laura@example.com",                    id=uuid.uuid4(),

            "telefono": "555-0201",                    user_id=admin_user.id,

            "direccion": "Avenida Central #456",                    department="IT",

            "fecha_nacimiento": "1990-07-22",                    permissions_level="full"

            "genero": "F",                )

            "nombre_contacto_emergencia": "Pedro Martínez",                

            "telefono_contacto_emergencia": "555-0202",                session.add(admin_profile)

            "condiciones_medicas": "Hipertensión",                await session.commit()

            "alergias": "Penicilina",                

            "created_by": receptionist_id                print("Default administrator user created successfully!")

        }                print("Email: admin@odontolab.com")

    ]                print("Password: admin123456")

                    print("Please change the password after first login!")

    for patient_data in patients:            

        patient = Patient(**patient_data)        else:

        session.add(patient)            print("Roles already exist. Skipping role creation.")

        

    await session.commit()    await engine.dispose()

    print(f"✓ {len(patients)} sample patients created successfully!")    print("Database initialization completed!")





async def seed_contact_requests(session: AsyncSession):if __name__ == "__main__":

    """Create sample contact requests."""    asyncio.run(init_database())
    print("\nCreating sample contact requests...")
    
    # Check if contact requests already exist
    result = await session.execute(select(ContactRequest))
    existing_contacts = result.scalars().all()
    
    if existing_contacts:
        print("✗ Contact requests already exist. Skipping contact creation.")
        return
    
    contacts = [
        {
            "nombre": "Roberto Sánchez",
            "cedula": "1122334455",
            "email": "roberto@example.com",
            "telefono": "555-0301",
            "motivo": "Consulta por servicio de ortodoncia",
            "acepta_politica": True,
            "status": ContactStatus.PENDING
        },
        {
            "nombre": "Patricia López",
            "cedula": "5544332211",
            "email": "patricia@example.com",
            "telefono": "555-0401",
            "motivo": "Solicitud de información sobre precios",
            "acepta_politica": True,
            "status": ContactStatus.PENDING
        }
    ]
    
    for contact_data in contacts:
        contact = ContactRequest(**contact_data)
        session.add(contact)
    
    await session.commit()
    print(f"✓ {len(contacts)} sample contact requests created successfully!")


async def init_database():
    """
    Initialize the database with tables and seed data.
    """
    print("=" * 60)
    print("OdontoLab Database Initialization")
    print("=" * 60)
    
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False  # Set to True to see SQL queries
    )
    
    # Create all tables
    await create_tables(engine)
    
    # Create async session
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        # Seed users
        users = await seed_users(session)
        
        if users:
            # Get receptionist user for patient creation
            receptionist = next(u for u in users if u.role == UserRole.RECEPTIONIST)
            
            # Seed patients
            await seed_patients(session, receptionist.id)
        
        # Seed contact requests
        await seed_contact_requests(session)
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("✓ Database initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now start the application with:")
    print("  python run_dev.py")
    print("\nAPI Documentation will be available at:")
    print("  http://localhost:8000/docs")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(init_database())
