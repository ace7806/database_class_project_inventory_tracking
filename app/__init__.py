from flask import Flask, jsonify, request
from flask_cors import CORS

# Activate
app = Flask(__name__)
# Apply CORS to this app
CORS(app)

from app.routes import parts, test2, warehouse, statistics, rack, supplier, user, transaction

print('imported routes')
