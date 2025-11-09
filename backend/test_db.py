from app.database import engine, Base
from app.models.models import User, Email

Base.metadata.create_all(bind=engine)
print("Successful")