
from flask_sqlalchemy import SQLAlchemy
from flask import Flask



app = Flask(__name__)
db = SQLAlchemy(app)
app.secret_key = 'dev'

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/scdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



from routes import * 