# Set Matplotlib backend to Agg
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg

from app import app

if __name__ == "__main__":
    app.run(debug=True)