import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(
    os.path.join(BASE_DIR, 'config/firebase_service_account.json')
)
default_app = firebase_admin.initialize_app(cred)
