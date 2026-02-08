#!/usr/bin/env python
"""
Debug version to track button clicks and data flow.
"""
import sys
sys.path.insert(0, 'src')

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Patch the dashboard callbacks to add logging
from candle_patterns import dashboard

# Store original functions
original_load_sample = None
original_apply_filters = None

def create_logging_wrapper():
    """Create wrapper that logs when callbacks are called."""
    from candle_patterns.dashboard import app
    
    # Find the load_sample_data callback
    for callback in app.server.app_callback_map.values():
        if hasattr(callback, '__name__') and 'load_sample' in callback.__name__:
            print(f"\n✅ Found load_sample_data callback")
    
    print(f"\nTotal callbacks registered: {len(app.server.app_callback_map)}")

logger.info("=" * 80)
logger.info("STARTING DASHBOARD - WATCH FOR ERRORS")
logger.info("=" * 80)

from candle_patterns.dashboard import app

create_logging_wrapper()

logger.info("\n✅ Dashboard module loaded successfully")
logger.info("🌐 Visit: http://127.0.0.1:8050")
logger.info("📢 Watch this console for errors when you click 'Load Sample Data'")
logger.info("=" * 80 + "\n")

app.run(debug=False, host='127.0.0.1', port=8050, use_reloader=False)
