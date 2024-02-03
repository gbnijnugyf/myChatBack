from application import app
from controllers.users import user

app.register_blueprint(user, url_prefix="/user")
