#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/kernel00/Codes/Hospital Management System')

from backend.database import engine
import sqlalchemy as sa

# Drop old trigger
with engine.begin() as conn:
    conn.execute(sa.text("DROP TRIGGER IF EXISTS after_bill_update"))
    conn.execute(sa.text("DROP TRIGGER IF EXISTS before_bill_update"))
    
    # Create new BEFORE UPDATE trigger
    trigger_sql = """CREATE TRIGGER before_bill_update
    BEFORE UPDATE ON bills
    FOR EACH ROW
    BEGIN
        IF NEW.paid_amount IS NOT NULL THEN
            IF NEW.paid_amount >= NEW.total_amount THEN
                SET NEW.payment_status = 'Paid';
            ELSEIF NEW.paid_amount > 0 THEN
                SET NEW.payment_status = 'Partially Paid';
            ELSE
                SET NEW.payment_status = 'Pending';
            END IF;
        END IF;
    END"""
    conn.execute(sa.text(trigger_sql))
    print("✓ Trigger updated successfully!")
