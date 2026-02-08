#!/usr/bin/env python
"""
Standalone server with test endpoint to load sample data.
"""
import sys
sys.path.insert(0, 'src')

from flask import Flask, jsonify
from candle_patterns.dashboard import app as dash_app

# Get the Flask server from Dash
server = dash_app.server

@server.route('/api/load-sample', methods=['GET'])
def load_sample():
    """Load sample data via REST API."""
    try:
        from candle_patterns.dashboard import load_sample_data
        data, msg = load_sample_data(1)
        
        if data:
            return jsonify({
                'status': 'success',
                'message': msg,
                'records': len(data['df']),
                'patterns': len(data['patterns'])
            })
        else:
            return jsonify({'status': 'error', 'message': 'No data'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("DASHBOARD WITH TEST ENDPOINT")
    print("="*80)
    print("\nMain app: http://127.0.0.1:8050")
    print("Test endpoint: http://127.0.0.1:8050/api/load-sample")
    print("\nTry this in your browser:")
    print("  curl http://127.0.0.1:8050/api/load-sample")
    print("="*80 + "\n")
    
    # Run the Dash app
    dash_app.run(debug=False, host='127.0.0.1', port=8050, use_reloader=False)
