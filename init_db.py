from app import app, db  # ดึง app และ db จากไฟล์หลักที่คุณสร้างไว้

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully.")
