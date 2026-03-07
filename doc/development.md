# 🧪 Desenvolvimento

Guia para quem for **desenvolver** ou **contribuir** no projeto: testes, CI/CD, lint e cobertura.

---

## 1. Testes (pytest)

### 1.1 Executar todos os testes

```bash
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

### 1.2 Com cobertura

```bash
pytest --cov=config --cov=file_manager --cov=gravador --cov=logger_config --cov=main --cov=upload_gdrive --cov-report=term-missing
```

### 1.3 Estrutura de testes

| Pasta/Arquivo | Conteúdo |
|---------------|----------|
| `tests/conftest.py` | Fixtures: `tmp_gravacoes_dir`, `sample_video_file`, `sample_large_file`, mocks de janela e Popen. |
| `tests/test_config.py` | Validação de tipos e intervalos das variáveis de `config`. |
| `tests/test_file_manager.py` | Hash SHA-256/MD5, cópia para Drive local, verificação de integridade. |
| `tests/test_gravador.py` | `_build_ffmpeg_cmd` (todos os codecs), `_find_teams_window`, `_janela_em_foco`, `parar_gravacao`, `TeamsRecorder`, `gravar`, `copiar_para_gdrive`. |
| `tests/test_logger_config.py` | `setup_logging`, `get_console`, criação do diretório `logs/`. |
| `tests/test_main.py` | Fluxo de `main`: janela não encontrada, start falha, KeyboardInterrupt, finally (upload/cópia), handler SIGTERM. |
| `tests/test_upload_gdrive.py` | `_safe_auth_message`, upload sem pasta ID, mock de `build()` e HttpError 403/500, integridade. |

### 1.4 Mocks

- **pygetwindow:** `gw.getAllWindows()` mockado para retornar lista vazia ou janela fake.
- **subprocess.Popen:** Processo fake com `poll()`, `communicate()`, `kill()`, `wait()`.
- **config:** `patch("gravador.config")` ou `patch.object(main_mod.config, "GDRIVE_PASTA_ID", ...)` conforme o caso.
- **Google API:** `patch("googleapiclient.discovery.build")` e `patch("file_manager.FileManager")` nos testes de upload.

---

## 2. CI/CD (GitHub Actions)

### 2.1 Workflow

O arquivo **`.github/workflows/tests.yml`** é executado em **push** e **pull_request** nas branches `main` e `master`.

### 2.2 Jobs

| Job | Descrição |
|-----|------------|
| **Testes + Cobertura** | Matrix Python 3.10, 3.11, 3.12; `pip install -r requirements.txt` + pytest; cobertura apenas dos módulos da aplicação; **falha se cobertura < 85%**. |
| **Lint (Ruff)** | `ruff check` em todos os `.py` da aplicação e da pasta `tests/`. |

### 2.3 Badge

O README na raiz e o índice em `doc/README.md` usam o badge do workflow:

```markdown
[![Tests & Lint](https://img.shields.io/github/actions/workflow/status/carmipa/gravador_de_aula/tests.yml?branch=main&label=Tests%20%26%20Lint&logo=github)](https://github.com/carmipa/gravador_de_aula/actions/workflows/tests.yml)
```

---

## 3. Lint (Ruff)

### 3.1 Verificar o código

```bash
ruff check config.py file_manager.py gravador.py logger_config.py main.py upload_gdrive.py tests/
```

### 3.2 Formatação (opcional)

```bash
ruff format config.py file_manager.py gravador.py logger_config.py main.py upload_gdrive.py tests/
```

O CI **não** exige `ruff format --check` para evitar falha em projetos já existentes; você pode habilitar depois se quiser.

---

## 4. Cobertura mínima

- **CI:** `--cov-fail-under=85` (meta futura: 90%).
- **Módulos medidos:** `config`, `file_manager`, `gravador`, `logger_config`, `main`, `upload_gdrive` (não a pasta `tests/`).

---

## 5. Dependências de desenvolvimento

Incluídas em **requirements.txt**:

- `pytest`
- `pytest-cov`

Para lint local (opcional):

- `ruff`

---

[⬆️ Voltar ao índice](README.md)
