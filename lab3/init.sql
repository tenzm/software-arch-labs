-- Инициализация базы данных для Profi.ru
-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(20) DEFAULT 'client' CHECK (role IN ('admin', 'specialist', 'client')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для таблицы пользователей
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Создание таблицы категорий услуг
CREATE TABLE IF NOT EXISTS service_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для категорий
CREATE INDEX IF NOT EXISTS idx_categories_name ON service_categories(name);
CREATE INDEX IF NOT EXISTS idx_categories_active ON service_categories(is_active);

-- Создание таблицы услуг
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES service_categories(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price_from DECIMAL(10,2),
    price_to DECIMAL(10,2),
    duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для услуг
CREATE INDEX IF NOT EXISTS idx_services_category ON services(category_id);
CREATE INDEX IF NOT EXISTS idx_services_name ON services(name);
CREATE INDEX IF NOT EXISTS idx_services_price ON services(price_from, price_to);
CREATE INDEX IF NOT EXISTS idx_services_active ON services(is_active);

-- Создание триггера для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применение триггеров
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON service_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Вставка тестовых данных
-- Админ пользователь будет создан автоматически при запуске приложения

-- Тестовые категории услуг
INSERT INTO service_categories (name, description) VALUES
('Ремонт и строительство', 'Услуги по ремонту квартир, домов и строительству'),
('Красота и здоровье', 'Парикмахерские услуги, косметология, массаж'),
('Репетиторство', 'Индивидуальные занятия по различным предметам'),
('Транспорт', 'Грузоперевозки, такси, курьерские услуги'),
('Уборка', 'Клининговые услуги для дома и офиса'),
('IT и технологии', 'Программирование, настройка техники, веб-дизайн')
ON CONFLICT DO NOTHING;

-- Тестовые услуги
INSERT INTO services (category_id, name, description, price_from, price_to, duration_minutes) 
SELECT 
    c.id, 
    s.name, 
    s.description, 
    s.price_from, 
    s.price_to, 
    s.duration_minutes
FROM service_categories c
CROSS JOIN (VALUES
    ('Покраска стен', 'Качественная покраска стен в квартире', 1500.00, 3000.00, 240),
    ('Поклейка обоев', 'Профессиональная поклейка обоев', 800.00, 2000.00, 180),
    ('Мужская стрижка', 'Стрижка для мужчин', 500.00, 1500.00, 30),
    ('Женская стрижка', 'Стрижка для женщин', 1000.00, 3000.00, 60),
    ('Математика', 'Репетиторство по математике', 800.00, 2000.00, 60),
    ('Английский язык', 'Индивидуальные занятия английским', 1000.00, 2500.00, 60),
    ('Грузоперевозки', 'Перевозка мебели и грузов', 1000.00, 5000.00, 120),
    ('Уборка квартиры', 'Генеральная уборка квартиры', 2000.00, 8000.00, 180),
    ('Разработка сайта', 'Создание веб-сайтов под ключ', 15000.00, 100000.00, 480)
) s(name, description, price_from, price_to, duration_minutes)
WHERE c.name IN (
    'Ремонт и строительство', 
    'Красота и здоровье', 
    'Репетиторство', 
    'Транспорт', 
    'Уборка', 
    'IT и технологии'
)
ON CONFLICT DO NOTHING; 