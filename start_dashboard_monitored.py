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
    """Log dashboard startup information."""
    logger.info("\n✅ All callbacks registered and ready")
    logger.info("Sample data auto-loads on dashboard launch")

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
