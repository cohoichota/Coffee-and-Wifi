from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL


app = Flask(__name__)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
db = SQLAlchemy(app)

Bootstrap(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    img_url = StringField('Cafe Images (URL)', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    seats = SelectField('Number of seats', choices=["0 - 10", "10-20", "20-30", "30-40", "40-50", "50+"])
    has_toilet = SelectField('Has Toilet', choices=["True", "False"])
    has_wifi = SelectField('Has Wifi', choices=["True", "False"])
    has_sockets = SelectField('Has Sockets', choices=["True", "False"])
    can_take_calls = SelectField('Can Take Calls', choices=["True", "False"])
    coffee_price = StringField('Coffee Price (e.g: £2.50)', validators=[DataRequired()])
    submit = SubmitField('Submit')


# HTML Part
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=bool(form.has_sockets.data),
            has_toilet=bool(form.has_toilet.data),
            has_wifi=bool(form.has_wifi.data),
            can_take_calls=bool(form.can_take_calls.data),
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    cafes = db.session.query(Cafe).all()
    return render_template('cafes.html', cafes=cafes)



# API Part
# HTTP GET - A Random Cafe
@app.route("/api/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


# HTTP GET - All Cafe
@app.route("/api/get")
def get_all_cafe():
    cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in cafes:
        cafe_list.append(cafe.to_dict())
    return jsonify(cafes=cafe_list)


# HTTP GET - Search Record
@app.route("/api/search", methods=["GET", "POST"])
def search_cafe():
    search_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=search_location).all()
    cafe_list = []
    for cafe in cafes:
        cafe_list.append(cafe.to_dict())
    if cafes:
        return jsonify(cafe=cafe_list)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at the location."})


# HTTP POST - Create Record
@app.route("/api/add", methods=["POST"])
def post_new_cafe():
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        new_cafe = Cafe(
            name=request.args.get("name"),
            map_url=request.args.get("map_url"),
            img_url=request.args.get("img_url"),
            location=request.args.get("loc"),
            has_sockets=bool(request.args.get("sockets")),
            has_toilet=bool(request.args.get("toilet")),
            has_wifi=bool(request.args.get("wifi")),
            can_take_calls=bool(request.args.get("calls")),
            seats=request.args.get("seats"),
            coffee_price=request.args.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."}), 200
    else:
        return jsonify(error={"Sorry": "That's not allowed. Make sure you have the correct api_key."}), 403


# HTTP PUT/PATCH - Update Record
@app.route("/api/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("coffee_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


# HTTP DELETE - Delete Record
@app.route("/api/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        cafe_to_delete = db.session.query(Cafe).get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Sorry": "That's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
