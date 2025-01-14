from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from SPARQLWrapper import SPARQLWrapper, JSON
from bs4 import BeautifulSoup
# from urllib.request import Request, urlopen
import os
import re
import sys


app = Flask(__name__)

# URL du sparql endpoint
endpoint_url = "https://data.idref.fr/sparql"


def get_results(endpoint_url, query):
    # from Wikidata Query Service example
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0],
                                                sys.version_info[1])
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def getbio(urlid):
    query = f"""
    PREFIX bio: <http://purl.org/vocab/bio/0.1/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    select * where {{
    BIND(<{urlid}> AS ?person)
    optional {{ ?person foaf:name ?nom_plein. }}
    optional {{ ?person foaf:givenName ?prenom. }}
    optional {{ ?person foaf:familyName ?nom . }}
    optional {{ ?person bio:event [a bio:Birth ; bio:date ?naissance] }}
    optional {{ ?person bio:event [a bio:Death ; bio:date ?mort] }} .
    optional {{ ?person skos:note ?bio }}
    }}
    """
    person = {}
    results = get_results(endpoint_url, query)
    for result in results["results"]["bindings"]:
        person["nom_plein"] = result["nom_plein"]["value"] if ("nom_plein" in result) else None
        person["prenom"] = result["prenom"]["value"] if ("prenom" in result) else None
        person["nom"] = result["nom"]["value"] if ("nom" in result) else None
        person["naissance"] = result["naissance"]["value"] if ("naissance" in result) else None
        person["mort"] = result["mort"]["value"] if ("mort" in result) else None
        person["bio"] = result["bio"]["value"] if ("bio" in result) else None

    return (person)


def getpubli(urlid):
    query = f"""
    PREFIX dcterms: <http://purl.org/dc/terms/>

    select (count(?titre) as ?eff)
    where {{
      BIND(<{urlid}> AS ?person)
      optional {{ ?doc ?relator ?person ;
                 dcterms:bibliographicCitation ?titre.
    }}
    }}
    """
    results = get_results(endpoint_url, query)
    for result in results["results"]["bindings"]:
        effectif = result["eff"]["value"] if ("eff" in result) else None

    return (effectif)


def geturis(urlid):
    query = f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    select distinct ?uris where {{
    optional {{<{urlid}> owl:sameAs ?uris}}
    }}
    """
    uris = []
    results = get_results(endpoint_url, query)
    for result in results["results"]["bindings"]:
        uris.append(result["uris"]["value"] if ("uris" in result) else None)
    
    return (uris)

    
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/getfile', methods=['GET', 'POST'])
def getfile():
    if request.method == 'POST':
        f = request.files['file']
        fname = os.path.splitext(f.filename)
        fext = fname[1]
        if fext == ".html" or fext == ".xml":
            filename = secure_filename(f.filename)
            f.save(filename)
            return redirect(url_for('getdata', name=filename))
        else:
            print("Ce n'est pas un fichier HTML ou un fichier XML.")


@app.route('/getdata/<name>')
def getdata(name):
    html = open(name, "r")
    # html = open(os.path.join(app.instance_path, name), "r")
    content = html.read()
    soup = BeautifulSoup(content, "lxml")

    biographies = []

    liens = soup.findAll("nom")
    for lien in liens:
        url = lien.get("sameas")
        if url is not None and "www.idref.fr" in url:
            id_regex = re.search(r"\.fr/(.*)/?", url)
            if id_regex is not None:
                id_content = id_regex.group(1)
                if url.endswith("/id"):
                    urlid = "http://www.idref.fr/" + str(id_content)
                else:
                    urlid = "http://www.idref.fr/" + str(id_content) + "/id"
                print("    {}".format(urlid))
                bio = getbio(urlid)
                eff_publi = getpubli(urlid)
                bio["publis"] = eff_publi
                uris = geturis(urlid)
                bio["uris"] = uris
                print(bio)
                biographies.append(bio)

        else:
            print("Erreur URL :\n{}\n---".format(url))
    # return (biographies)

    os.remove(name)

    return render_template('results.html', result=biographies)


if __name__ == '__main__':
    app.run(debug=True)
