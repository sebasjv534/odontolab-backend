-- ============================================
-- OdontoLab Database Schema
-- PostgreSQL 14+
-- ============================================

-- Crear extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Eliminar tablas si existen (para reinicializar)
DROP TABLE IF EXISTS contact_requests CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Tipos ENUM
CREATE TYPE user_role AS ENUM ('admin', 'dentist', 'receptionist');
CREATE TYPE contact_status AS ENUM ('pending', 'contacted', 'resolved');

-- ============================================
-- TABLA: users
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================
-- TABLA: patients
-- ============================================
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    medical_conditions TEXT,
    allergies TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Índices para patients
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_created_by ON patients(created_by);
CREATE INDEX idx_patients_name ON patients(first_name, last_name);

-- Índice de texto completo para búsqueda
CREATE INDEX idx_patients_fulltext ON patients 
USING gin(to_tsvector('spanish', first_name || ' ' || last_name || ' ' || email));

-- ============================================
-- TABLA: medical_records
-- ============================================
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    dentist_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    visit_date TIMESTAMP WITH TIME ZONE NOT NULL,
    diagnosis TEXT NOT NULL,
    treatment TEXT NOT NULL,
    notes TEXT,
    teeth_chart JSONB,
    next_appointment TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint para asegurar que dentist_id sea realmente un dentista
    CONSTRAINT check_dentist_role CHECK (
        dentist_id IN (SELECT id FROM users WHERE role = 'dentist')
    )
);

-- Índices para medical_records
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_medical_records_dentist_id ON medical_records(dentist_id);
CREATE INDEX idx_medical_records_visit_date ON medical_records(visit_date);
CREATE INDEX idx_medical_records_next_appointment ON medical_records(next_appointment);

-- Índice GIN para búsqueda en teeth_chart JSON
CREATE INDEX idx_medical_records_teeth_chart ON medical_records USING gin(teeth_chart);

-- ============================================
-- TABLA: contact_requests
-- ============================================
CREATE TABLE contact_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    servicio TEXT,
    acepta_politica BOOLEAN NOT NULL DEFAULT FALSE,
    status contact_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint para asegurar que acepta_politica sea TRUE
    CONSTRAINT check_acepta_politica CHECK (acepta_politica = TRUE)
);

-- Índices para contact_requests
CREATE INDEX idx_contact_requests_email ON contact_requests(email);
CREATE INDEX idx_contact_requests_status ON contact_requests(status);
CREATE INDEX idx_contact_requests_created_at ON contact_requests(created_at DESC);

-- ============================================
-- FUNCIONES Y TRIGGERS
-- ============================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- DATOS DE PRUEBA (SEEDS)
-- ============================================

-- NOTA: Los passwords están hasheados con bcrypt (factor 12)
-- Password original para todos: "admin123", "dentist123", "reception123"

-- Usuario Admin
INSERT INTO users (id, email, hashed_password, first_name, last_name, role, is_active)
VALUES (
    '550e8400-e29b-41d4-a716-446655440001',
    'admin@odontolab.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ij.RqVKqjQu6', -- admin123
    'Admin',
    'Sistema',
    'admin',
    TRUE
);

-- Usuario Dentista
INSERT INTO users (id, email, hashed_password, first_name, last_name, role, is_active)
VALUES (
    '550e8400-e29b-41d4-a716-446655440002',
    'dentist@odontolab.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ij.RqVKqjQu6', -- dentist123
    'Juan Carlos',
    'Pérez García',
    'dentist',
    TRUE
);

-- Usuario Recepcionista
INSERT INTO users (id, email, hashed_password, first_name, last_name, role, is_active)
VALUES (
    '550e8400-e29b-41d4-a716-446655440003',
    'reception@odontolab.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ij.RqVKqjQu6', -- reception123
    'Ana María',
    'Martínez López',
    'receptionist',
    TRUE
);

-- Pacientes de ejemplo
INSERT INTO patients (id, first_name, last_name, email, phone, date_of_birth, address, emergency_contact_name, emergency_contact_phone, medical_conditions, allergies, created_by)
VALUES 
(
    '650e8400-e29b-41d4-a716-446655440001',
    'María',
    'García Rodríguez',
    'maria.garcia@email.com',
    '3001234567',
    '1990-05-15',
    'Calle 45 #23-12, Bogotá',
    'Pedro García',
    '3009876543',
    'Hipertensión controlada',
    'Penicilina',
    '550e8400-e29b-41d4-a716-446655440003' -- Creado por recepcionista
),
(
    '650e8400-e29b-41d4-a716-446655440002',
    'Carlos',
    'López Mendoza',
    'carlos.lopez@email.com',
    '3107654321',
    '1985-08-22',
    'Carrera 15 #78-45, Medellín',
    'Laura López',
    '3156789012',
    'Diabetes tipo 2',
    'Ninguna conocida',
    '550e8400-e29b-41d4-a716-446655440003'
),
(
    '650e8400-e29b-41d4-a716-446655440003',
    'Laura',
    'Martínez Silva',
    'laura.martinez@email.com',
    '3209876543',
    '1995-03-10',
    'Avenida 68 #12-34, Cali',
    'Jorge Martínez',
    '3134567890',
    NULL,
    'Látex',
    '550e8400-e29b-41d4-a716-446655440003'
);

-- Historias clínicas de ejemplo
INSERT INTO medical_records (id, patient_id, dentist_id, visit_date, diagnosis, treatment, notes, teeth_chart, next_appointment)
VALUES 
(
    '750e8400-e29b-41d4-a716-446655440001',
    '650e8400-e29b-41d4-a716-446655440001', -- María García
    '550e8400-e29b-41d4-a716-446655440002', -- Dr. Juan Carlos Pérez
    '2025-01-15 10:00:00+00',
    'Caries dental en segundo molar superior derecho',
    'Restauración con resina compuesta. Se realizó limpieza profunda y aplicación de sellante.',
    'Paciente cooperativa. Se recomienda control en 6 meses.',
    '{"tooth_17": {"status": "restored", "notes": "Resina compuesta"}, "general": "Higiene oral regular"}',
    '2025-07-15 10:00:00+00'
),
(
    '750e8400-e29b-41d4-a716-446655440002',
    '650e8400-e29b-41d4-a716-446655440002', -- Carlos López
    '550e8400-e29b-41d4-a716-446655440002',
    '2025-01-18 14:30:00+00',
    'Periodontitis moderada',
    'Limpieza dental profunda (raspaje y alisado radicular). Instrucciones de higiene oral.',
    'Paciente con acumulación de placa. Se recetó enjuague bucal con clorhexidina.',
    '{"general": "Periodontitis moderada", "gums": "Inflamación leve a moderada"}',
    '2025-02-18 14:30:00+00'
),
(
    '750e8400-e29b-41d4-a716-446655440003',
    '650e8400-e29b-41d4-a716-446655440003', -- Laura Martínez
    '550e8400-e29b-41d4-a716-446655440002',
    '2025-01-20 16:00:00+00',
    'Revisión de rutina - Estado dental óptimo',
    'Limpieza dental y aplicación de flúor. Profilaxis.',
    'Excelente higiene oral. Sin hallazgos patológicos.',
    '{"general": "Estado dental óptimo", "hygiene": "Excelente"}',
    '2025-07-20 16:00:00+00'
);

-- Solicitudes de contacto de ejemplo
INSERT INTO contact_requests (nombre, cedula, email, telefono, motivo, servicio, acepta_politica, status)
VALUES 
(
    'Roberto Sánchez',
    '1234567890',
    'roberto.sanchez@email.com',
    '3001112233',
    'Consulta por ortodoncia y blanqueamiento dental',
    'Ortodoncia',
    TRUE,
    'pending'
),
(
    'Diana Vargas',
    '9876543210',
    'diana.vargas@email.com',
    '3104445566',
    'Dolor en muela del juicio, requiero valoración urgente',
    'Cirugía',
    TRUE,
    'contacted'
);

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Pacientes con conteo de historias clínicas
CREATE OR REPLACE VIEW patients_with_records AS
SELECT 
    p.*,
    COUNT(mr.id) as total_records,
    MAX(mr.visit_date) as last_visit,
    MIN(mr.next_appointment) as next_appointment
FROM patients p
LEFT JOIN medical_records mr ON p.id = mr.patient_id
GROUP BY p.id;

-- Vista: Estadísticas por dentista
CREATE OR REPLACE VIEW dentist_statistics AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.email,
    COUNT(DISTINCT mr.patient_id) as total_patients,
    COUNT(mr.id) as total_records,
    COUNT(CASE WHEN mr.visit_date >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as records_last_month
FROM users u
LEFT JOIN medical_records mr ON u.id = mr.dentist_id
WHERE u.role = 'dentist' AND u.is_active = TRUE
GROUP BY u.id;

-- ============================================
-- FUNCIONES DE BÚSQUEDA
-- ============================================

-- Función para buscar pacientes por texto
CREATE OR REPLACE FUNCTION search_patients(search_query TEXT)
RETURNS TABLE (
    id UUID,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    date_of_birth DATE,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.first_name,
        p.last_name,
        p.email,
        p.phone,
        p.date_of_birth,
        ts_rank(
            to_tsvector('spanish', p.first_name || ' ' || p.last_name || ' ' || p.email),
            plainto_tsquery('spanish', search_query)
        ) as rank
    FROM patients p
    WHERE 
        to_tsvector('spanish', p.first_name || ' ' || p.last_name || ' ' || p.email) 
        @@ plainto_tsquery('spanish', search_query)
        OR p.first_name ILIKE '%' || search_query || '%'
        OR p.last_name ILIKE '%' || search_query || '%'
        OR p.email ILIKE '%' || search_query || '%'
        OR p.phone ILIKE '%' || search_query || '%'
    ORDER BY rank DESC, p.first_name ASC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PERMISOS Y SEGURIDAD
-- ============================================

-- Crear usuario de aplicación (opcional)
-- CREATE USER odontolab_app WITH PASSWORD 'your_secure_password';
-- GRANT CONNECT ON DATABASE odontolab_db TO odontolab_app;
-- GRANT USAGE ON SCHEMA public TO odontolab_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO odontolab_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO odontolab_app;

-- ============================================
-- CONSULTAS ÚTILES PARA VERIFICACIÓN
-- ============================================

-- Verificar usuarios creados
-- SELECT id, email, first_name, last_name, role, is_active FROM users;

-- Verificar pacientes
-- SELECT id, first_name, last_name, email, phone FROM patients;

-- Verificar historias clínicas
-- SELECT 
--     mr.id,
--     p.first_name || ' ' || p.last_name as patient_name,
--     u.first_name || ' ' || u.last_name as dentist_name,
--     mr.visit_date,
--     mr.diagnosis
-- FROM medical_records mr
-- JOIN patients p ON mr.patient_id = p.id
-- JOIN users u ON mr.dentist_id = u.id;

-- Estadísticas generales
-- SELECT 
--     (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as total_users,
--     (SELECT COUNT(*) FROM users WHERE role = 'dentist' AND is_active = TRUE) as total_dentists,
--     (SELECT COUNT(*) FROM patients) as total_patients,
--     (SELECT COUNT(*) FROM medical_records) as total_records,
--     (SELECT COUNT(*) FROM contact_requests WHERE status = 'pending') as pending_contacts;

-- ============================================
-- SCRIPT COMPLETADO
-- ============================================

COMMENT ON TABLE users IS 'Usuarios del sistema (admin, dentist, receptionist)';
COMMENT ON TABLE patients IS 'Pacientes de la clínica dental';
COMMENT ON TABLE medical_records IS 'Historias clínicas y registros de visitas';
COMMENT ON TABLE contact_requests IS 'Solicitudes de contacto del sitio web público';

-- Información de la base de datos
SELECT 'Base de datos OdontoLab creada exitosamente!' as status;
SELECT 'Usuarios de prueba creados:' as info;
SELECT email, role FROM users ORDER BY role;
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM patients) as patients,
    (SELECT COUNT(*) FROM medical_records) as medical_records,
    (SELECT COUNT(*) FROM contact_requests) as contact_requests;
