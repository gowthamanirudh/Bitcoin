from flask import render_template, request
from app import app
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Set Matplotlib backend to Agg
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tx_id = request.form['tx_id']
        data = fetch_transaction_data(tx_id)
        if data:
            bar_chart, pie_chart = visualize_transaction(data)
            if bar_chart and pie_chart:
                return render_template('index.html', bar_chart=bar_chart, pie_chart=pie_chart, tx_id=tx_id)
            else:
                return render_template('index.html', error="No valid inputs or outputs found in transaction data.")
        else:
            return render_template('index.html', error="Invalid Transaction ID")
    return render_template('index.html')

def fetch_transaction_data(tx_id):
    url = f"https://blockstream.info/api/tx/{tx_id}"
    response = requests.get(url)
    print(f"API Response: {response.status_code}, {response.text}")  # Debugging
    if response.status_code == 200:
        return response.json()
    return None

def visualize_transaction(data):
    inputs = data.get('vin', [])
    outputs = data.get('vout', [])
    
    # Handle empty inputs or outputs
    if not inputs or not outputs:
        print("No inputs or outputs found in transaction data.")  # Debugging
        return None, None
    
    # Calculate total input and output values
    total_input = sum(input_tx.get('prevout', {}).get('value', 0) for input_tx in inputs) / 1e8  # Convert to BTC
    total_output = sum(output.get('value', 0) for output in outputs) / 1e8  # Convert to BTC
    
    print(f"Total Input: {total_input} BTC")  # Debugging
    print(f"Total Output: {total_output} BTC")  # Debugging
    
    # Create a bar chart
    plt.figure(figsize=(8, 6))
    labels_bar = ['Total Input (BTC)', 'Total Output (BTC)']
    values_bar = [total_input, total_output]
    plt.bar(labels_bar, values_bar, color=['blue', 'green'])
    plt.title('Bitcoin Transaction Overview')
    plt.ylabel('Amount (BTC)')
    
    # Save the bar chart to a BytesIO object
    buf_bar = BytesIO()
    plt.savefig(buf_bar, format='png')
    plt.close()
    buf_bar.seek(0)
    bar_chart = base64.b64encode(buf_bar.getvalue()).decode('utf-8')
    
    # Create a pie chart
    plt.figure(figsize=(8, 6))
    values_pie = [output['value'] / 1e8 for output in outputs]  # Convert to BTC
    labels_pie = [output.get('scriptpubkey_address', 'Unknown') for output in outputs]
    plt.pie(values_pie, labels=labels_pie, autopct='%1.1f%%', startangle=140)
    plt.title('Bitcoin Transaction Output Distribution')
    
    # Save the pie chart to a BytesIO object
    buf_pie = BytesIO()
    plt.savefig(buf_pie, format='png')
    plt.close()
    buf_pie.seek(0)
    pie_chart = base64.b64encode(buf_pie.getvalue()).decode('utf-8')
    
    return bar_chart, pie_chart
