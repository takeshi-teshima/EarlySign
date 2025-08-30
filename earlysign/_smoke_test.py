def test_import_package() -> None:
    import earlysign

    assert hasattr(earlysign, "core")
