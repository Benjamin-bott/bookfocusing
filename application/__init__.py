
from flask import Flask
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["SECRET_KEY"] = "81185101eb0ebc8a409352fd778528e2ac355daa"
app.config["MONGO_URI"] = "mongodb+srv://cutetina329:seungbin0329%40@seungbin.2rwvbzs.mongodb.net/searchDB?retryWrites=true&w=majority"


# setup mongodb
mongodb_clinet = PyMongo(app)
db = mongodb_clinet.db

# Blueprint
from application.bookfocusing import routes as bookfocus_route
app.register_blueprint(bookfocus_route.bookfocusing, url_prefix="/bookfocusing")
from application.search import routes as search_route
app.register_blueprint(search_route.search, url_prefix="/search")

