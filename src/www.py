from application import app
from controllers.users import user
from controllers.chats import chat

app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(chat, url_prefix="/chat")
