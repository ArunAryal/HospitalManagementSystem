#!/usr/bin/env python3
"""
Recalculate all bill payment statuses by triggering the before_bill_update trigger.
This should be run after fixing the trigger to update existing bills.

Usage: uv run python -m backend.scripts.recalculate_bills
       or from project root: uv run python backend/scripts/recalculate_bills.py
"""

from ..database import engine
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
