import json

from flask import Flask, request
import rethinkdb as r

from .utils.db import Database

index = """
<!doctype html>

<html>
<head>
    <title>Strawpoll?</title>
</head>
<body>
    <h1>Add an option!</h1>
    <form action="addoption" method="GET">
    <p>Anime name: <input type="text" name="option"></p>
    <p><input type="submit" value="Submit your option!"></p>
    </form>
    <h2>Options</h2>
    {options}
</body>
</html>
"""

redirect = """
<!doctype html>

<html>
<head>

</head>
<body>
    <script type="text/javascript">
        window.location.href = "https://www.fwiedwice.me/strawpoll/";
    </script>
</body>
</html>
"""

href = """
<a href="https://www.fwiedwice.me/poll">Back</a>
"""


db = Database()

app = Flask(__name__)


@app.route("/test")
def test():
    return "This works? Testing python backend webserver."


@app.route("/")             # "/" will refer to www.fwiedwice.me/strawpoll/
@app.route("/poll")
def poll():
    options = db.get_options()
    print(options)
    option_message = ""
    option_message += """<form action="vote" method="GET">"""
    for option, votes in options.items():
        option_message += '<input type="radio" name="option" value="' + option + '"/>'
        option_message += "{option:>20}:{votes:>5}<br />".format(option=option,
                                                                 votes=votes)
        stuff = ""
        option_message += "<br />{}<br />".format(stuff)
    if len(options) > 0:
        option_message += """<p><input type="submit" value="Submit your vote!"></form>"""
    return index.format(options=option_message)


@app.route("/results")
def results():
    return "No results yet."


@app.route("/vote", methods=["GET"])
def vote():
    args = {k: v[0] for k, v in dict(request.args).items()}
    if request.method != "GET" or len(args) == 0:
        return "Invalid!" + href

    print(str(args))

    option = args['option']

    if not db.already_exists(option):
        return "Option doesn't exist<br />" + href
    db.add_vote(option)
    votes = db.get_votes(option)
    return "{option} now has {votes} votes<br />".format(option=option,
                                                         votes=votes) + href


@app.route("/addoption", methods=["GET"])
def addoption():
    args = {k: v[0] for k, v in dict(request.args).items()}
    if request.method != "GET" or len(args) == 0:
        return "Invalid!<br />" + href

    print(str(args))

    option = args['option']

    if db.already_exists(option):
        return "Already exists<br />" + href
    else:
        db.create_option(option)
        return "Option created<br />" + href


if __name__ == "__main__":
    app.run()
