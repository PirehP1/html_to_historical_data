from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/getfile', methods=['GET', 'POST'])
def getfile():
    if request.method == 'POST':
        f = request.files['file']
        fname = os.path.splitext(f.filename)
        fext = fname[1]
        if fext == ".html":
            f.save(secure_filename(f.filename))
            return redirect(url_for('getdata', name=f.filename))
        else:
            print("Ce n'est pas un fichier HTML.")


@app.route('/getdata/<name>')
def getdata(name):
    html = open(name, "r")
    content = html.read()
    soup = BeautifulSoup(content, "lxml")

    biographies = []

    liens = soup.findAll("a")
    for lien in liens:
        url = lien.get("href")
        if url is not None and url.startswith("https://www.idref.fr/") is True:
            data_bio = {}
            rdf = str(url) + ".rdf"

            req = Request(rdf)
            xml = urlopen(req).read()
            soup_rdf = BeautifulSoup(xml, "xml")

            bio = soup_rdf.findAll("foaf:Person")
            for b in bio:
                fname = b.find("foaf:familyName")
                data_bio["fname"] = fname.text
                sname = b.find("foaf:givenName")
                data_bio["sname"] = sname.text
                gender = b.find("foaf:gender")
                if gender is not None:
                    data_bio["gender"] = gender.text
                else:
                    data_bio["gender"] = "NA"
                birth = b.findAll("bio:Birth")
                for i in birth:
                    birthd = i.find("bio:date")
                    data_bio["birthd"] = birthd.text
                death = b.findAll("bio:Death")
                for i in death:
                    deathd = i.find("bio:date")
                    data_bio["deathd"] = deathd.text
                career = b.find("rdau:P60492")
                if career is not None:
                    data_bio["career"] = career.text
                elif b.find("skos:note") is not None:
                    career = b.find("skos:note")
                    data_bio["career"] = career.text
                else:
                    data_bio["career"] = "NA"
            biblio = soup_rdf.findAll("bibo:Document")
            notices = len(biblio)
            data_bio["notices"] = notices

            biographies.append(data_bio)

    os.remove(name)

    return render_template('results.html', result=biographies)


if __name__ == '__main__':
    app.run(debug=True)
