from app.core.db import engine, get_session


def test_engine_targets_configured_database():
    # Importing the engine must not require a live connection.
    assert "penguwave" in str(engine.url)


def test_get_session_yields_a_session():
    gen = get_session()
    try:
        session = next(gen)
        # Session is constructed lazily; this does not open a connection.
        assert session.get_bind() is engine
    finally:
        gen.close()
