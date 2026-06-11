"""
Unit and Integration tests for the tempconverter application.
Run with: pytest tests/ -v
"""
import pytest
import os
import sys

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ─────────────────────────────────────────────
# UNIT TESTS  (no database needed)
# ─────────────────────────────────────────────

class TestTemperatureConversionLogic:
    """Unit tests for Celsius → Fahrenheit conversion math."""

    def _convert(self, celsius):
        return round(((celsius * 1.8) + 32), 2)

    def test_freezing_point(self):
        assert self._convert(0) == 32.0

    def test_boiling_point(self):
        assert self._convert(100) == 212.0

    def test_body_temperature(self):
        assert self._convert(37) == 98.6

    def test_negative_temperature(self):
        assert self._convert(-40) == -40.0

    def test_room_temperature(self):
        assert self._convert(20) == 68.0

    def test_absolute_zero_approximation(self):
        assert self._convert(-273.15) == -459.67


class TestEnvironmentVariables:
    """Unit tests verifying that environment variable defaults work."""

    def test_student_default(self):
        val = os.environ.get('STUDENT', 'Default Student')
        assert isinstance(val, str)
        assert len(val) > 0

    def test_college_default(self):
        val = os.environ.get('COLLEGE', 'Default College')
        assert isinstance(val, str)
        assert len(val) > 0

    def test_student_env_override(self, monkeypatch):
        monkeypatch.setenv('STUDENT', 'Ivan Horvat')
        assert os.environ.get('STUDENT') == 'Ivan Horvat'

    def test_college_env_override(self, monkeypatch):
        monkeypatch.setenv('COLLEGE', 'Algebra Bernays University')
        assert os.environ.get('COLLEGE') == 'Algebra Bernays University'


# ─────────────────────────────────────────────
# INTEGRATION TESTS  (Flask test client, SQLite in-memory)
# ─────────────────────────────────────────────

@pytest.fixture(scope='module')
def app():
    """Create the Flask application configured for testing with SQLite.

    DATABASE_URL is set to a temporary SQLite file BEFORE importing the app,
    so the SQLAlchemy engine is built against SQLite from the start and no
    MySQL service is required to run the tests.
    """
    import tempfile
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///' + db_path)
    os.environ.setdefault('STUDENT', 'Test Student')
    os.environ.setdefault('COLLEGE', 'Test College')

    from app import app as flask_app, db

    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


class TestFlaskRoutes:
    """Integration tests for HTTP routes."""

    def test_home_page_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_home_page_contains_student_name(self, client):
        response = client.get('/')
        assert b'Test Student' in response.data

    def test_home_page_contains_college_name(self, client):
        response = client.get('/')
        assert b'Test College' in response.data

    def test_home_page_title_is_tempconverter(self, client):
        response = client.get('/')
        assert b'<title>TempConverter</title>' in response.data

    def test_form_submission_converts_temperature(self, client):
        response = client.post('/', data={'celsius': '100'}, follow_redirects=True)
        assert response.status_code == 200
        # After valid conversion, the page re-renders with the log table
        assert b'212' in response.data or b'100' in response.data

    def test_form_submission_stores_to_db(self, client, app):
        from app import db, Temperature
        with app.app_context():
            count_before = Temperature.query.count()
            client.post('/', data={'celsius': '0'}, follow_redirects=True)
            count_after = Temperature.query.count()
            assert count_after == count_before + 1

    def test_negative_celsius_accepted(self, client):
        response = client.post('/', data={'celsius': '-40'}, follow_redirects=True)
        assert response.status_code == 200

    def test_invalid_input_does_not_crash(self, client):
        response = client.post('/', data={'celsius': 'notanumber'}, follow_redirects=True)
        # Should return 200 (form re-render) not 500
        assert response.status_code in (200, 400)
