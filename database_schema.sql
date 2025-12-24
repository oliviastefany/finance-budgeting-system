-- ========================================
-- SMART FINANCE DATABASE SCHEMA
-- PostgreSQL Database Tables
-- ========================================

-- Drop tables if exist (for fresh install)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ========================================
-- USERS TABLE
-- ========================================
CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,  -- SHA256 hash (64 characters)
    monthly_income DECIMAL(12, 2) DEFAULT 0.00,
    preferred_currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_currency CHECK (preferred_currency IN ('USD', 'IDR', 'CNY', 'EUR', 'GBP', 'JPY'))
);

-- ========================================
-- TRANSACTIONS TABLE
-- ========================================
CREATE TABLE transactions (
    transaction_id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    category VARCHAR(50) NOT NULL,
    merchant VARCHAR(100),
    description TEXT,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,

    -- Constraints
    CONSTRAINT positive_amount CHECK (amount >= 0),
    CONSTRAINT valid_transaction_currency CHECK (currency IN ('USD', 'IDR', 'CNY', 'EUR', 'GBP', 'JPY'))
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Transactions indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date);

-- ========================================
-- TRIGGERS
-- ========================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- SAMPLE DATA (OPTIONAL - FOR TESTING)
-- ========================================

-- Insert sample users (passwords are hashed "password123")
INSERT INTO users (user_id, name, email, password_hash, monthly_income, preferred_currency) VALUES
('U00001', 'John Doe', 'john@example.com', 'ef92b778bafe771e89245b89ecbc08153c0cca5c2e2f3c38e0e52a1e8be3b8db', 5000.00, 'USD'),
('U00002', 'Jane Smith', 'jane@example.com', 'ef92b778bafe771e89245b89ecbc08153c0cca5c2e2f3c38e0e52a1e8be3b8db', 7500.00, 'USD'),
('U00003', 'Ahmad Santoso', 'ahmad@example.com', 'ef92b778bafe771e89245b89ecbc08153c0cca5c2e2f3c38e0e52a1e8be3b8db', 15000000.00, 'IDR');

-- Insert sample transactions
INSERT INTO transactions (transaction_id, user_id, amount, currency, category, merchant, description, transaction_date) VALUES
('T00001', 'U00001', 239.84, 'USD', 'Hobbies', 'Sports Store', 'Running shoes', '2024-01-01 10:30:00'),
('T00002', 'U00001', 89.50, 'USD', 'Groceries', 'Whole Foods', 'Weekly groceries', '2024-01-02 14:20:00'),
('T00003', 'U00002', 1200.00, 'USD', 'Housing', 'Rent Payment', 'Monthly rent', '2024-01-01 09:00:00'),
('T00004', 'U00003', 350000.00, 'IDR', 'Food', 'Restaurant', 'Dinner with family', '2024-01-03 19:30:00');

-- ========================================
-- VIEWS FOR ANALYTICS
-- ========================================

-- User spending summary view
CREATE OR REPLACE VIEW user_spending_summary AS
SELECT
    u.user_id,
    u.name,
    u.email,
    u.preferred_currency,
    COUNT(t.transaction_id) as total_transactions,
    COALESCE(SUM(t.amount), 0) as total_spending,
    COALESCE(AVG(t.amount), 0) as avg_transaction,
    COALESCE(MAX(t.amount), 0) as max_transaction,
    COALESCE(MIN(t.amount), 0) as min_transaction
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name, u.email, u.preferred_currency;

-- Category breakdown view
CREATE OR REPLACE VIEW category_breakdown AS
SELECT
    user_id,
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM transactions
GROUP BY user_id, category
ORDER BY user_id, total_amount DESC;

-- ========================================
-- FUNCTIONS
-- ========================================

-- Function to get user's total spending in a date range
CREATE OR REPLACE FUNCTION get_user_spending(
    p_user_id VARCHAR(10),
    p_start_date TIMESTAMP,
    p_end_date TIMESTAMP
)
RETURNS DECIMAL(12, 2) AS $$
DECLARE
    total_spending DECIMAL(12, 2);
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO total_spending
    FROM transactions
    WHERE user_id = p_user_id
    AND transaction_date BETWEEN p_start_date AND p_end_date;

    RETURN total_spending;
END;
$$ LANGUAGE plpgsql;

-- Function to get top spending category for user
CREATE OR REPLACE FUNCTION get_top_category(p_user_id VARCHAR(10))
RETURNS VARCHAR(50) AS $$
DECLARE
    top_cat VARCHAR(50);
BEGIN
    SELECT category INTO top_cat
    FROM transactions
    WHERE user_id = p_user_id
    GROUP BY category
    ORDER BY SUM(amount) DESC
    LIMIT 1;

    RETURN top_cat;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- GRANTS (Security)
-- ========================================

-- Grant permissions to finance_user
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO finance_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON transactions TO finance_user;
GRANT SELECT ON user_spending_summary TO finance_user;
GRANT SELECT ON category_breakdown TO finance_user;
GRANT EXECUTE ON FUNCTION get_user_spending TO finance_user;
GRANT EXECUTE ON FUNCTION get_top_category TO finance_user;

-- ========================================
-- DONE!
-- ========================================

SELECT 'Database schema created successfully!' AS status;
