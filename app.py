from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/info', methods=['POST'])
def info():
        error = None
        if request.method == 'POST': 
            if request.form['button'] == 'china':
                return render_template('china.html')
            elif request.form['button'] == 'japan':
                return render_template('japan.html')
            elif request.form['button'] == 'taiwan':
                return render_template('taiwan.html') 
            elif request.form['button'] == 'hongkong':
                return render_template('hongkong.html')  
            elif request.form['button'] == 'vietnam':
                return render_template('vietnam.html')
            elif request.form['button'] == 'singapore':
                return render_template('singapore.html') 
            elif request.form['button'] == 'thailand':
                return render_template('thailand.html')
            elif request.form['button'] == 'malaysia':
                return render_template('malaysia.html')
            elif request.form['button'] == 'laos':
                return render_template('laos.html') 
            elif request.form['button'] == 'mongolia':
                return render_template('mongolia.html') 
            elif request.form['button'] == 'guam':
                return render_template('guam.html')
            elif request.form['button'] == 'saipan':
                return render_template('saipan.html')                                                     
  

if __name__ == '__main__':
    app.run()