from flask import Flask, render_template_string, request
from scrape import scrape_elections  # Import your scrape_elections function

app = Flask(__name__)


@app.route('/')
def display_elections():
    url = 'https://en.wikipedia.org/wiki/List_of_elections_in_2024'
    elections = scrape_elections(url)

    # Retrieve the search query from the URL parameters
    search_query = request.args.get('q', '').lower()

    if search_query:
        # Filter elections based on the search query
        # You can customize the fields you want to search in
        elections = [
            election for election in elections
            if search_query in election['date'].lower()
               or search_query in election['election'].lower()
               or search_query in election['region'].lower()
        ]

    # HTML template for displaying elections with a search bar
    template = '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Upcoming Elections in 2024</title>
        <style>
            /* Optional: Some basic styling for better appearance */
            body { font-family: Arial, sans-serif; margin: 40px; }
            .search-bar { margin-bottom: 20px; }
            .search-input { padding: 8px; width: 300px; }
            .search-button { padding: 8px 16px; }
            .election-item { margin-bottom: 15px; }
            hr { border: 0; border-top: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>Upcoming Elections in 2024</h1>

        <!-- Search Form -->
        <div class="search-bar">
            <form method="get" action="/">
                <input type="text" name="q" class="search-input" placeholder="Search elections..." value="{{ request.args.get('q', '') }}">
                <button type="submit" class="search-button">Search</button>
            </form>
        </div>

        {% if elections %}
            <ul>
            {% for election in elections %}
                <li class="election-item">
                    <strong>Date:</strong> {{ election['date'] }}<br>
                    <strong>Election:</strong> {{ election['election'] }}<br>
                    <strong>Region:</strong> {{ election['region'] }}<br>
                    <a href="{{ election['link'] }}" target="_blank">More Info</a>
                </li>
                <hr>
            {% endfor %}
            </ul>
        {% else %}
            <p>No upcoming elections found matching your search.</p>
        {% endif %}
    </body>
    </html>
    '''

    return render_template_string(template, elections=elections, request=request)


if __name__ == '__main__':
    app.run(debug=True)
