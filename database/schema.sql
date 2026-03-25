-- Hospital Management System Database Schema

-- Create Database
CREATE DATABASE IF NOT EXISTS hospital_management;
USE hospital_management;

-- Patients Table
CREATE TABLE patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group VARCHAR(5),
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(15),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient_name (first_name, last_name),
    INDEX idx_patient_phone (phone)
);

-- Doctors Table
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(200),
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    consultation_fee DECIMAL(10, 2) NOT NULL,
    experience_years INT,
    joined_date DATE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    INDEX idx_doctor_specialization (specialization)
);

-- Departments Table
CREATE TABLE departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    head_doctor_id INT,
    FOREIGN KEY (head_doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
);

-- Appointments Table
CREATE TABLE appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'No-Show') DEFAULT 'Scheduled',
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_appointment_status (status)
);

-- Medical Records Table
CREATE TABLE medical_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT,
    diagnosis TEXT NOT NULL,
    symptoms TEXT,
    treatment TEXT,
    notes TEXT,
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
);

-- Medicines Table
CREATE TABLE medicines (
    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
    medicine_name VARCHAR(100) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(100),
    unit_price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 10,
    expiry_date DATE,
    INDEX idx_medicine_name (medicine_name),
    CHECK (stock_quantity >= 0),
    CHECK (unit_price > 0)
);

-- Prescriptions Table
CREATE TABLE prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    medical_record_id INT NOT NULL,
    medicine_id INT NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    instructions TEXT,
    FOREIGN KEY (medical_record_id) REFERENCES medical_records(record_id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    CHECK (quantity > 0)
);

-- Rooms Table
CREATE TABLE rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    room_type ENUM('General', 'Private', 'ICU', 'Emergency') NOT NULL,
    capacity INT NOT NULL,
    current_occupancy INT DEFAULT 0,
    charge_per_day DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    CHECK (current_occupancy <= capacity),
    CHECK (charge_per_day > 0)
);

-- Admissions Table
CREATE TABLE admissions (
    admission_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    room_id INT NOT NULL,
    doctor_id INT NOT NULL,
    admission_date DATETIME NOT NULL,
    discharge_date DATETIME,
    reason TEXT NOT NULL,
    status ENUM('Active', 'Discharged') DEFAULT 'Active',
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Bills Table
CREATE TABLE bills (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    admission_id INT,
    appointment_id INT,
    consultation_fee DECIMAL(10, 2) DEFAULT 0,
    medicine_charges DECIMAL(10, 2) DEFAULT 0,
    room_charges DECIMAL(10, 2) DEFAULT 0,
    other_charges DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('Pending', 'Paid', 'Partially Paid') DEFAULT 'Pending',
    payment_method ENUM('Cash', 'Card', 'Insurance', 'Online') DEFAULT NULL,
    bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_amount DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (admission_id) REFERENCES admissions(admission_id) ON DELETE SET NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL,
    CHECK (total_amount >= 0),
    CHECK (paid_amount >= 0)
);

-- Staff Table
CREATE TABLE staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role ENUM('Nurse', 'Technician', 'Administrator', 'Receptionist') NOT NULL,
    department_id INT,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    salary DECIMAL(10, 2),
    hire_date DATE NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
);

-- Triggers
DELIMITER //

-- Trigger to update room occupancy on admission
CREATE TRIGGER after_admission_insert
AFTER INSERT ON admissions
FOR EACH ROW
BEGIN
    IF NEW.status = 'Active' THEN
        UPDATE rooms 
        SET current_occupancy = current_occupancy + 1,
            is_available = IF(current_occupancy + 1 >= capacity, FALSE, TRUE)
        WHERE room_id = NEW.room_id;
    END IF;
END//

-- Trigger to update room occupancy on discharge
CREATE TRIGGER after_admission_update
AFTER UPDATE ON admissions
FOR EACH ROW
BEGIN
    IF OLD.status = 'Active' AND NEW.status = 'Discharged' THEN
        UPDATE rooms 
        SET current_occupancy = current_occupancy - 1,
            is_available = TRUE
        WHERE room_id = NEW.room_id;
    END IF;
END//

-- Trigger to reduce medicine stock when prescribed
CREATE TRIGGER after_prescription_insert
AFTER INSERT ON prescriptions
FOR EACH ROW
BEGIN
    UPDATE medicines 
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE medicine_id = NEW.medicine_id;
END//

-- Trigger to restore medicine stock when prescription is deleted
CREATE TRIGGER after_prescription_delete
AFTER DELETE ON prescriptions
FOR EACH ROW
BEGIN
    UPDATE medicines 
    SET stock_quantity = stock_quantity + OLD.quantity
    WHERE medicine_id = OLD.medicine_id;
END//

-- Trigger to auto-update payment status based on paid amount
CREATE TRIGGER before_bill_update
BEFORE UPDATE ON bills
FOR EACH ROW
BEGIN
    IF NEW.paid_amount IS NOT NULL THEN
        IF NEW.paid_amount >= NEW.total_amount THEN
            SET NEW.payment_status = 'Paid';
        ELSEIF NEW.paid_amount > 0 THEN
            SET NEW.payment_status = 'Partially Paid';
        ELSEIF NEW.paid_amount = 0 THEN
            SET NEW.payment_status = 'Pending';
        END IF;
    END IF;
END//

-- Trigger to auto-create bill when admission is created
CREATE TRIGGER after_admission_insert_bill
AFTER INSERT ON admissions
FOR EACH ROW
BEGIN
    DECLARE v_room_charges DECIMAL(10,2) DEFAULT 0;
    DECLARE v_daily_rate DECIMAL(10,2) DEFAULT 0;
    
    -- Get room daily rate
    SELECT charge_per_day INTO v_daily_rate
    FROM rooms
    WHERE room_id = NEW.room_id;
    
    -- Initial room charges (1 day by default)
    SET v_room_charges = COALESCE(v_daily_rate, 0);
    
    -- Create bill for admission
    INSERT INTO bills (
        patient_id,
        admission_id,
        consultation_fee,
        medicine_charges,
        room_charges,
        other_charges,
        total_amount,
        payment_status,
        bill_date,
        paid_amount
    ) VALUES (
        NEW.patient_id,
        NEW.admission_id,
        0,
        0,
        v_room_charges,
        0,
        v_room_charges,
        'Pending',
        NOW(),
        0
    );
END//

-- Trigger to update bill medicine charges when prescription is added
CREATE TRIGGER after_prescription_insert_bill
AFTER INSERT ON prescriptions
FOR EACH ROW
BEGIN
    DECLARE v_patient_id INT DEFAULT 0;
    DECLARE v_medicine_price DECIMAL(10,2) DEFAULT 0;
    DECLARE v_prescription_cost DECIMAL(10,2) DEFAULT 0;
    DECLARE v_existing_bill_id INT DEFAULT NULL;
    DECLARE v_admission_id INT DEFAULT NULL;
    
    -- Get medicine price and subscription cost
    SELECT unit_price INTO v_medicine_price
    FROM medicines
    WHERE medicine_id = NEW.medicine_id;
    
    SET v_prescription_cost = v_medicine_price * NEW.quantity;
    
    -- Get patient and admission from medical record
    SELECT patient_id, appointment_id INTO v_patient_id, v_admission_id
    FROM medical_records
    WHERE record_id = NEW.medical_record_id;
    
    -- Find existing bill for this patient's admission
    SELECT bill_id INTO v_existing_bill_id
    FROM bills
    WHERE patient_id = v_patient_id
    AND admission_id = v_admission_id
    LIMIT 1;
    
    -- Update bill if it exists
    IF v_existing_bill_id IS NOT NULL THEN
        UPDATE bills
        SET medicine_charges = medicine_charges + v_prescription_cost,
            total_amount = total_amount + v_prescription_cost
        WHERE bill_id = v_existing_bill_id;
    END IF;
END//

-- Trigger to update bill when admission is discharged (finalize room charges)
CREATE TRIGGER after_admission_update_bill
AFTER UPDATE ON admissions
FOR EACH ROW
BEGIN
    DECLARE v_days INT DEFAULT 1;
    DECLARE v_room_charge DECIMAL(10,2) DEFAULT 0;
    DECLARE v_existing_bill_id INT DEFAULT NULL;
    DECLARE v_old_room_charges DECIMAL(10,2) DEFAULT 0;
    DECLARE v_new_room_charges DECIMAL(10,2) DEFAULT 0;
    
    -- Only update bill when discharged (status changes from Active to Discharged)
    IF OLD.status = 'Active' AND NEW.status = 'Discharged' THEN
        -- Calculate number of days
        SET v_days = DATEDIFF(NEW.discharge_date, OLD.admission_date);
        IF v_days < 1 THEN SET v_days = 1; END IF;
        
        -- Get room daily rate
        SELECT charge_per_day INTO v_room_charge
        FROM rooms
        WHERE room_id = NEW.room_id;
        
        -- Calculate new room charges
        SET v_new_room_charges = v_days * COALESCE(v_room_charge, 0);
        
        -- Find and update the bill
        SELECT bill_id INTO v_existing_bill_id
        FROM bills
        WHERE admission_id = NEW.admission_id
        LIMIT 1;
        
        IF v_existing_bill_id IS NOT NULL THEN
            -- Get old room charges to subtract
            SELECT room_charges INTO v_old_room_charges
            FROM bills
            WHERE bill_id = v_existing_bill_id;
            
            -- Update bill with accurate room charges
            UPDATE bills
            SET room_charges = v_new_room_charges,
                total_amount = total_amount - v_old_room_charges + v_new_room_charges
            WHERE bill_id = v_existing_bill_id;
        END IF;
    END IF;
END//

-- Trigger to restore medicine charges when prescription is deleted
CREATE TRIGGER after_prescription_delete_bill
AFTER DELETE ON prescriptions
FOR EACH ROW
BEGIN
    DECLARE v_patient_id INT DEFAULT 0;
    DECLARE v_medicine_price DECIMAL(10,2) DEFAULT 0;
    DECLARE v_prescription_cost DECIMAL(10,2) DEFAULT 0;
    DECLARE v_existing_bill_id INT DEFAULT NULL;
    DECLARE v_admission_id INT DEFAULT NULL;
    
    -- Get medicine price and subscription cost
    SELECT unit_price INTO v_medicine_price
    FROM medicines
    WHERE medicine_id = OLD.medicine_id;
    
    SET v_prescription_cost = v_medicine_price * OLD.quantity;
    
    -- Get patient and admission from medical record
    SELECT patient_id, appointment_id INTO v_patient_id, v_admission_id
    FROM medical_records
    WHERE record_id = OLD.medical_record_id;
    
    -- Find existing bill for this patient's admission
    SELECT bill_id INTO v_existing_bill_id
    FROM bills
    WHERE patient_id = v_patient_id
    AND admission_id = v_admission_id
    LIMIT 1;
    
    -- Update bill if it exists
    IF v_existing_bill_id IS NOT NULL THEN
        UPDATE bills
        SET medicine_charges = medicine_charges - v_prescription_cost,
            total_amount = total_amount - v_prescription_cost
        WHERE bill_id = v_existing_bill_id;
    END IF;
END//

DELIMITER ;

-- Stored Procedure: Calculate Bill Amount
DELIMITER //

CREATE PROCEDURE calculate_bill(
    IN p_patient_id INT,
    IN p_admission_id INT,
    IN p_appointment_id INT,
    OUT p_total_amount DECIMAL(10,2)
)
BEGIN
    DECLARE v_consultation_fee DECIMAL(10,2) DEFAULT 0;
    DECLARE v_medicine_charges DECIMAL(10,2) DEFAULT 0;
    DECLARE v_room_charges DECIMAL(10,2) DEFAULT 0;
    DECLARE v_days INT DEFAULT 0;
    DECLARE v_daily_rate DECIMAL(10,2) DEFAULT 0;
    
    -- Get consultation fee if appointment exists
    IF p_appointment_id IS NOT NULL THEN
        SELECT d.consultation_fee INTO v_consultation_fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = p_appointment_id;
    END IF;
    
    -- Calculate room charges if admission exists
    IF p_admission_id IS NOT NULL THEN
        SELECT 
            DATEDIFF(COALESCE(discharge_date, NOW()), admission_date),
            r.charge_per_day
        INTO v_days, v_daily_rate
        FROM admissions ad
        JOIN rooms r ON ad.room_id = r.room_id
        WHERE ad.admission_id = p_admission_id;
        
        SET v_room_charges = v_days * v_daily_rate;
    END IF;
    
    -- Calculate medicine charges (from prescriptions through medical records)
    SELECT COALESCE(SUM(m.unit_price * p.quantity), 0) INTO v_medicine_charges
    FROM prescriptions p
    JOIN medicines m ON p.medicine_id = m.medicine_id
    JOIN medical_records mr ON p.medical_record_id = mr.record_id
    WHERE mr.patient_id = p_patient_id
    AND (mr.appointment_id = p_appointment_id OR p_appointment_id IS NULL);
    
    SET p_total_amount = v_consultation_fee + v_medicine_charges + v_room_charges;
END//

DELIMITER ;

-- Views
-- View: Patient Appointment History
CREATE VIEW patient_appointment_history AS
SELECT 
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    a.appointment_id,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization,
    a.appointment_date,
    a.appointment_time,
    a.status,
    a.reason
FROM patients p
JOIN appointments a ON p.patient_id = a.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id;

-- View: Doctor Schedule
CREATE VIEW doctor_schedule AS
SELECT 
    d.doctor_id,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization,
    a.appointment_date,
    a.appointment_time,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    a.status
FROM doctors d
JOIN appointments a ON d.doctor_id = a.doctor_id
JOIN patients p ON a.patient_id = p.patient_id
WHERE a.status != 'Cancelled'
ORDER BY a.appointment_date, a.appointment_time;

-- View: Low Stock Medicines
CREATE VIEW low_stock_medicines AS
SELECT 
    medicine_id,
    medicine_name,
    stock_quantity,
    reorder_level,
    unit_price,
    manufacturer
FROM medicines
WHERE stock_quantity <= reorder_level;

-- View: Room Availability
CREATE VIEW room_availability AS
SELECT 
    room_number,
    room_type,
    capacity,
    current_occupancy,
    charge_per_day,
    is_available,
    (capacity - current_occupancy) AS available_beds
FROM rooms;

-- Sample Data (Optional)
INSERT INTO doctors (first_name, last_name, specialization, qualification, phone, email, consultation_fee, experience_years, joined_date) VALUES
('John', 'Smith', 'Cardiology', 'MD, FACC', '1234567890', 'john.smith@hospital.com', 150.00, 15, '2020-01-15'),
('Sarah', 'Johnson', 'Pediatrics', 'MD, FAAP', '1234567891', 'sarah.johnson@hospital.com', 120.00, 10, '2021-03-20'),
('Michael', 'Brown', 'Orthopedics', 'MD, MS Ortho', '1234567892', 'michael.brown@hospital.com', 140.00, 12, '2019-06-10');

INSERT INTO rooms (room_number, room_type, capacity, charge_per_day) VALUES
('101', 'General', 4, 50.00),
('102', 'General', 4, 50.00),
('201', 'Private', 1, 150.00),
('301', 'ICU', 1, 500.00);

INSERT INTO medicines (medicine_name, description, manufacturer, unit_price, stock_quantity, reorder_level) VALUES
('Paracetamol', 'Pain reliever and fever reducer', 'PharmaCo', 0.50, 1000, 100),
('Amoxicillin', 'Antibiotic', 'MediLife', 2.50, 500, 50),
('Ibuprofen', 'Anti-inflammatory', 'HealthCare Ltd', 1.00, 750, 75);
