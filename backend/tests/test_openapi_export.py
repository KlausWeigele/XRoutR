def test_openapi_importable():
    from app.main import app
    schema = app.openapi()
    assert "openapi" in schema

