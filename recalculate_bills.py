#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/kernel00/Codes/Hospital Management System')

from backend.database import engine
import sqlalchemy as sa

# Update all bills to trigger the before_bill_update trigger
with engine.begin() as conn:
    # This will trigger the before_bill_update trigger
    conn.execute(sa.text("""
        UPDATE bills 
        SET paid_amount = paid_amount 
        WHERE bill_id > 0
    """))
    print("✓ All bills updated - payment statuses recalculated!")
