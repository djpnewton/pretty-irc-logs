from flask import Flask, url_for, render_template, Markup
import os
import re
import requests
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

base_url = os.environ['BASE_URL']
base_path = os.environ['BASE_PATH']
channels = os.environ['CHANNELS'].split(',')
timeout = int(os.environ['TIMEOUT']) if 'TIMEOUT' in os.environ else 10

def get(url):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.content.decode('utf-8')

@app.route('/')
def index():
    title = "%s" % base_url
    page_title = "Log Highlighter"
    body = Markup("<p>Use the top menu to select a channel.</p>")
    return render_template('bootstrap.html', page_title=page_title, lead=title, title=title, channels=channels, body=body)


@app.route('/<channel>')
def show_channel(channel):
    output = ""

    log_path = "/%s/%s/" % (base_path, channel)
    log_index = get(base_url + log_path)

    print(log_index)

    file_finder = re.compile(r'<a href="([\d]{4}-[\d]{2}-[\d]{2}.log)"')
    for match in file_finder.finditer(log_index):
        output += "<a href=\"%s\">%s</a><br />" % (url_for('show_log', channel=channel, log_file=match.group(1)), match.group(1))

    page_title = "#%s" % channel
    title = "Channel: %s" % channel
    body = Markup(output)
    return render_template('bootstrap.html', page_title=page_title, title=title, channels=channels, body=body)


@app.route('/<channel>/<log_file>')
def show_log(channel, log_file):
    log_path = "/%s/%s/%s" % (base_path, channel, log_file)
    log_body = get(base_url + log_path)

    body = Markup(highlight(log_body, get_lexer_by_name('irc'), HtmlFormatter()))
    title = "Channel: %s" % channel
    page_title = "#%s" % channel
    lead = "Log: %s" % log_file
    return render_template('bootstrap.html', title=title, page_title=page_title, lead=lead, channel=channel, channels=channels, body=body)


if __name__ == '__main__':
    app.debug = 'DEBUG' in os.environ
    port = int(os.environ['PORT']) if 'PORT' in os.environ else 5000
    app.run(host='0.0.0.0', port=port)
