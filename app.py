from flask import Flask, render_template, request, redirect, url_for
import bus_items as bus

app = Flask(__name__)
app.config.from_object('flask_config.Config')

@app.route('/')
def index():
    return render_template('index.html', bus_stops=bus.get_stops())

if __name__ == '__main__':
    app.run()
