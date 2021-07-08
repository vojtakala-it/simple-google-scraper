import io
import requests
from flask import Flask, render_template, request, send_file
from urllib import parse
from requests_html import HTMLSession
from datetime import datetime



app = Flask(__name__)


def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as err:
        print(err)


def get_results(query):
    query = parse.quote_plus(query)
    response = get_source("https://www.google.com/search?q=" + query)

    return response


def parse_results(response):
    css_identifier_div_result = ".tF2Cxc"
    css_identifier_title_result = "h3"
    css_identifier_link_result = ".yuRUbf a"
    css_identifier_text_result = ".IsZvec > div"

    results = response.html.find(css_identifier_div_result)

    output = []
    for result in results:

        item = {
            "title": result.find(css_identifier_title_result, first=True).text,
            "link": result.find(css_identifier_link_result, first=True).attrs["href"],
            "text": result.find(css_identifier_text_result, first=True).text
        }

        output.append(item)
    return output


def google_search(query):
    response = get_results(query)
    return parse_results(response)




@app.route("/post_field", methods=["GET", "POST"])
def need_input():
    for key, value in request.form.items():
        print("key: {0}, value: {1}".format(key, value))


@app.route("/form", methods=["GET"])
def get_form():
    return render_template('index.html')



@app.route("/", methods=["GET", "POST"])
def get_string():
    current_year = datetime.today().year

    if request.method == "POST":
        string = request.form.get("user_string")
        results = google_search(string)

        new_file = []
        for string in results:
            formatted_string = f"title: {string['title']}\ntext: {string['text']}\nlink: {string['link']}"
            formatted_string.replace("{}'", "").replace('\n', "")
            new_file.append(formatted_string)

        text_file = io.open("scraped_page.txt", "w", encoding="utf-8")
        for element in new_file:
            text_file.write(element + "\n\n")

        files_to_be_sent = open("scraped_page.txt", 'rb')
        return send_file(path_or_file=files_to_be_sent,
                         as_attachment=True, max_age=0, download_name="scraped_page.txt")

    return render_template("index.html", year=current_year)



if __name__ == "__main__":
    app.run(debug=True)






