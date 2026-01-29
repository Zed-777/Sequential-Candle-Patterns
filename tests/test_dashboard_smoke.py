def test_dashboard_app_importable():
    from candle_patterns import dashboard

    # Ensure the Dash app object exists and server is accessible
    assert hasattr(dashboard, "app")
    assert hasattr(dashboard, "server")
