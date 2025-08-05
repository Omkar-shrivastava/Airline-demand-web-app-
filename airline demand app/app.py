from flask import Flask, render_template, request
import requests
import pandas as pd
from api_analysis import generate_summary

app = Flask(__name__)

API_KEY = 'aae4db27af1a6ee609ce5cea2f4f6dd4'

def fetch_live_flight_data():
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&limit=100"
    try:
        response = requests.get(url)
        data = response.json()
        flights = data.get('data', [])

        processed = []
        for flight in flights:
            dep = flight.get('departure', {})
            arr = flight.get('arrival', {})
            price = 100 + hash(flight['flight']['iata']) % 200  # mock pricing
            demand = 50 + hash(dep.get('airport', '')) % 150     # mock demand

            if dep and arr and dep.get('airport') and arr.get('airport'):
                route = f"{dep.get('airport')} - {arr.get('airport')}"
                processed.append({
                    "route": route,
                    "source": dep.get('airport'),
                    "destination": arr.get('airport'),
                    "price": price,
                    "demand": demand,
                    "timestamp": dep.get('scheduled')
                })

        df = pd.DataFrame(processed)
        return df

    except Exception as e:
        print("❌ API failed, using fallback.")
        fallback_data = [
            {"route": "SYD - MEL", "price": 150, "demand": 120, "timestamp": "2025-08-01T09:00:00"},
            {"route": "MEL - BNE", "price": 180, "demand": 95, "timestamp": "2025-08-02T12:00:00"},
            {"route": "SYD - BNE", "price": 170, "demand": 110, "timestamp": "2025-08-02T08:00:00"},
            {"route": "PER - SYD", "price": 200, "demand": 90,  "timestamp": "2025-08-03T10:00:00"},
            {"route": "ADL - MEL", "price": 140, "demand": 130, "timestamp": "2025-08-04T11:00:00"},
            {"route": "BNE - PER", "price": 210, "demand": 85,  "timestamp": "2025-08-05T13:00:00"}
        ]
        df = pd.DataFrame(fallback_data)
        df[['source', 'destination']] = df['route'].str.split(' - ', expand=True)
        return df


@app.route('/', methods=['GET', 'POST'])
def index():
    df = fetch_live_flight_data()

    selected_source = request.form.get('source')
    selected_dest = request.form.get('destination')

    if selected_source:
        df = df[df['source'] == selected_source]
    if selected_dest:
        df = df[df['destination'] == selected_dest]

    summary = generate_summary(df)
    sources = sorted(df['source'].dropna().unique())
    destinations = sorted(df['destination'].dropna().unique())
    chart_data = df[['route', 'price', 'demand', 'timestamp']].to_dict('records')

    return render_template(
        'index.html',
        table=df.to_html(classes='table table-bordered', index=False),
        chart_data=chart_data,
        summary=summary,
        sources=sources,
        destinations=destinations,
        selected_source=selected_source,
        selected_dest=selected_dest
    )


if __name__ == '__main__':
    app.run(debug=True)
