"""Test Configuration"""
import os
import tempfile
from app.config import Settings


def test_settings_defaults():
    """Test default settings values"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("""
SUPABASE_URL=https://test.supabase.co
SUPABASE_ANON_KEY=test-anon-key
SUPABASE_SERVICE_ROLE_KEY=test-service-key
""")
        f.flush()
        os.environ['ENV_FILE'] = f.name

    try:
        settings = Settings(_env_file=f.name)
        assert settings.APP_NAME == "ELE Agent"
        assert settings.VERSION == "1.0.0"
        assert settings.DEBUG is True
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRY_HOURS == 24
    finally:
        os.unlink(f.name)
        if 'ENV_FILE' in os.environ:
            del os.environ['ENV_FILE']


def test_settings_from_env():
    """Test settings loaded from environment"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("""
SUPABASE_URL=https://custom.supabase.co
SUPABASE_ANON_KEY=custom-anon
SUPABASE_SERVICE_ROLE_KEY=custom-service
JWT_SECRET=custom-secret
DEBUG=false
RATE_LIMIT_FREE_RPM=60
""")
        f.flush()

    try:
        settings = Settings(_env_file=f.name)
        assert settings.SUPABASE_URL == "https://custom.supabase.co"
        assert settings.SUPABASE_ANON_KEY == "custom-anon"
        assert settings.JWT_SECRET == "custom-secret"
        assert settings.DEBUG is False
        assert settings.RATE_LIMIT_FREE_RPM == 60
    finally:
        os.unlink(f.name)