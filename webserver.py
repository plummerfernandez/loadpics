from flask import Flask
from png2stl import png2stl
from stl2png import stl2png

app = Flask(__name__)

@app.route("/")
def hello():
    png2stl("tmp/pill-2.png", "tmp/pill-remade.stl")
    return "Hello World!"

if __name__ == "__main__":
    stl2png("tmp/pill.stl", "tmp/pill-2.png")
    app.run()
    
