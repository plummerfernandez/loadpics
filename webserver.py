from flask import Flask, request, redirect, url_for, send_file, make_response, abort
from png2stl import png2stl
from stl2png import stl2png
from werkzeug import secure_filename
import os
import io
from tempfile import SpooledTemporaryFile, mkstemp, mktemp

DEBUG = True
UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['stl', 'STL', 'png', 'PNG'])

app = Flask(__name__)


@app.route("/", methods=['GET'])
def serve_upload_form():
    return '''
    <!doctype html>
    <title>PNG <-> STL converter</title>
    <h1>Select a .png or .stl filem</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def replace_suffix(filename, suffix):
    return os.path.splitext(os.path.basename(filename))[0] + suffix

def mk_response(body, content_type, filename):
    response = make_response(body)
    response.headers['Content-Type'] = content_type
    response.headers['Content-Disposition'] = 'attachment; filename=' + filename
    return response

def is_png(content_magic) :
    return content_magic[0] == chr(0x89) and content_magic[1] == chr(0x50) and content_magic[2] == chr(0x4E) and content_magic[3] == chr(0x47) and content_magic[4] == chr(0x0D) and content_magic[5] == chr(0x0A) and content_magic[6] == chr(0x1A) and content_magic[7] == chr(0x0A)

@app.route("/", methods=['POST'])
def convert_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        content_magic = file.stream.read(8)
        file.stream.seek(0)

        tmppath = mktemp()
        file.save(tmppath)
        
        output = io.BytesIO()
        if is_png(content_magic):
            png2stl(tmppath, output)
            mimetype = 'application/sla'
            filesuffix = ".slt"
        else:
            stl2png(tmppath, output)
            mimetype = 'image/png'
            filesuffix = ".png"

        os.remove(tmppath)
        filename = replace_suffix(secure_filename(file.filename), filesuffix)
        output.seek(0)        
        return send_file(
            output,
            as_attachment=True,
            attachment_filename=filename,
            mimetype=mimetype)
    abort(400)

#@app.route("/")
#def hello():
#    png2stl("tmp/pill-2.png", "tmp/pill-remade.stl")
#    return "Hello World!"

if __name__ == "__main__":
#    stl2png("tmp/pill.stl", "tmp/pill-2.png")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(debug=DEBUG)
