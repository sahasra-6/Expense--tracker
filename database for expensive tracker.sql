USE expense_tracker;

DROP TABLE IF EXISTS expenses;

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    category VARCHAR(50),
    amount DECIMAL(10,2),
    monthly_budget DECIMAL(10,2)
);