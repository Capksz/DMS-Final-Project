from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Define a route for the root URL
@app.route('/')
def home():
    return "Hello, Flask!"

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
