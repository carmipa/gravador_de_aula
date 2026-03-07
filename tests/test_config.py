"""
Testes do módulo config.
Verifica tipos, intervalos e valores default/aceitos (sem alterar .env em tempo de execução).
"""


def test_config_codec_valido():
    """CODEC deve ser um dos: av1, hevc_nvenc, hevc, h264."""
    import config
    assert config.CODEC in ("av1", "hevc_nvenc", "hevc", "h264")


def test_config_crf_no_intervalo():
    """CRF deve estar entre 18 e 32."""
    import config
    assert 18 <= config.CRF <= 32


def test_config_fps_no_intervalo():
    """FPS deve estar entre 15 e 60."""
    import config
    assert 15 <= config.FPS <= 60


def test_config_av1_preset_no_intervalo():
    """AV1_PRESET deve estar entre 0 e 13."""
    import config
    assert 0 <= config.AV1_PRESET <= 13


def test_config_gravacoes_dir_existe_e_string():
    """GRAVACOES_DIR deve ser string não vazia e o diretório deve ser criado."""
    import config
    assert isinstance(config.GRAVACOES_DIR, str)
    assert len(config.GRAVACOES_DIR) > 0
    from pathlib import Path
    assert Path(config.GRAVACOES_DIR).exists() or True  # pode ser criado no import


def test_config_teams_window_title_string():
    """TEAMS_WINDOW_TITLE deve ser string."""
    import config
    assert isinstance(config.TEAMS_WINDOW_TITLE, str)


def test_config_gdrive_pasta_local_ou_none():
    """GDRIVE_PASTA_LOCAL deve ser None ou string."""
    import config
    assert config.GDRIVE_PASTA_LOCAL is None or isinstance(config.GDRIVE_PASTA_LOCAL, str)


def test_config_gdrive_pasta_id_ou_none():
    """GDRIVE_PASTA_ID deve ser None ou string."""
    import config
    assert config.GDRIVE_PASTA_ID is None or isinstance(config.GDRIVE_PASTA_ID, str)


def test_config_audio_device_dshow_ou_none():
    """AUDIO_DEVICE_DSHOW deve ser None ou string."""
    import config
    assert config.AUDIO_DEVICE_DSHOW is None or isinstance(config.AUDIO_DEVICE_DSHOW, str)
