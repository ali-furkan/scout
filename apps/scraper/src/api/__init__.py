from flask import Flask
from sqlalchemy.orm import Session

def create_app(db_session: Session):
    app = Flask(__name__)

    from api.routes import main_bp

    app.register_blueprint(main_bp)
    main_bp.db_session = db_session

    return app

from . import routes
from .dto import TeamSchema