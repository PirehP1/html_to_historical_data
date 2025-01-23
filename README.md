# html_to_historical_data

Service python en Flask qui récupère tous les liens vers des notices d'autorité [IdRef](https://www.idref.fr/) présents dans un fichier HTML ou XML transmis par l'utilisateur afin de produire un tableau de synthèse des données disponibles dans les notices en question. Le tableu de synthèse est créé à partir de requêtes SPARQL adressées au [endpoint d'IdRef](https://data.idref.fr/sparql).

Dans l'état actuel du script (février 2024) les chaînes de caractères à chercher doivent être balisées par un élément `<nom>` dans lequel un attribut `sameAS` doit contenir l'URI de la notice d'autorité IdRef correspondante. Par exemple :

```xml
<nom type="personne" valeur="Broglie (de), Albert" sameAs="http://www.idref.fr/029795370/id">Broglie</nom>
```
Le service peut être testé ici : https://l1histinfo.eu.pythonanywhere.com/ avec le fichier `pasteur.xml` dans le présent dépôt.

Il s'agit d'un développement réalisé dans le contexte de l'[enseignement de L1 les écritures numériques de l'histoire dispensé à l'Université Paris Panthéon-Sorbonne](https://formations.pantheonsorbonne.fr/fr/catalogue-des-formations/licence-L/licence-histoire-KBTGNAF1/licence-histoire-KBTGZNNY/ue-methodologie-KBTH09K4/histoire-et-informatique-s2-KBT8GMRW.html). L'objectif étant de faire comprendre aux étudiants comment il est possible de récupérer automatiquement des données historiques à partir de l'édition numérique de documents anciens numérisés.
