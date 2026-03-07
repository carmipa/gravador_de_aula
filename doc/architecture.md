# 🏗️ Arquitetura do sistema

Este documento descreve a arquitetura do **Gravador de Aula — Teams FIAP** em detalhe: módulos, responsabilidades, dependências e diagramas (Mermaid) para visualização no GitHub.

---

## 1. Visão geral em camadas

```
┌──────────────────────────────────────────────────────────────────────────┐
│  CAMADA DE ENTRADA (main.py)                                              │
│  Orquestração, signals, health check, upload em background                 │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CAMADA DE NEGÓCIO                                                        │
│  gravador.py (RecorderInterface → TeamsRecorder)  │  upload_gdrive.py    │
│  file_manager.py (hash, cópia, integridade)                               │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  INFRAESTRUTURA                                                           │
│  config.py (env)  │  logger_config.py (Loguru + Rich)  │  FFmpeg (subprocess)  │  pygetwindow  │  Google Drive API
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama de contexto (Host → Processo → GRC → Nuvem)

Visão voltada para **GitHub** e **GRC**: separação em Host Windows, processo Python, controles de segurança e nuvem. O GitHub renderiza o Mermaid abaixo nativamente.

```mermaid
graph TD
    subgraph Host_Windows["🖥️ Host Windows"]
        Teams["Microsoft Teams App"]
        Audio["Áudio DShow (opcional)"]
    end

    subgraph Processo_Python["🐍 Processo Python"]
        Main["main.py"] --> Recorder["TeamsRecorder"]
        Recorder --> FFmpeg["FFmpeg Engine"]
        FFmpeg --> Codec["AV1 / HEVC / H.264"]
    end

    subgraph Security_GRC["🔒 Security & GRC"]
        FileMgr["FileManager"] --> Hash["SHA-256 Integrity"]
        FileMgr --> Logs["Loguru Audit Trail"]
    end

    subgraph Cloud["☁️ Nuvem"]
        Upload["upload_gdrive.py"] --> GDrive["Google Drive API"]
    end

    FFmpeg -- "Escreve" --> LocalDisk[("Local .mkv/.mp4")]
    LocalDisk --> FileMgr
    FileMgr --> Upload
    Teams --> Recorder
```

---

## 3. Diagrama de componentes (Mermaid)

O diagrama abaixo mostra os módulos e suas dependências. Renderize no GitHub ou em [Mermaid Live](https://mermaid.live/).

```mermaid
flowchart TB
    subgraph Entrada["🎬 Entrada"]
        MAIN["main.py\nOrquestração"]
    end

    subgraph Nucleo["⚙️ Núcleo"]
        GRAV["gravador.py\nTeamsRecorder\nparar_gravacao"]
        FM["file_manager.py\nFileManager\nSHA-256, cópia"]
        UPL["upload_gdrive.py\nUpload API"]
    end

    subgraph Infra["🔧 Infraestrutura"]
        CFG["config.py\nVariáveis de ambiente"]
        LOG["logger_config.py\nLoguru + Rich"]
    end

    subgraph Externos["🌐 Externos"]
        FF["FFmpeg\n(subprocess)"]
        GW["pygetwindow"]
        GAPI["Google Drive API"]
    end

    MAIN --> GRAV
    MAIN --> FM
    MAIN --> UPL
    MAIN --> LOG
    MAIN --> CFG

    GRAV --> CFG
    GRAV --> FF
    GRAV --> GW

    UPL --> CFG
    UPL --> FM
    UPL --> GAPI

    FM --> CFG
    FM --> LOG
```

---

## 4. Diagrama de sequência — Gravação e encerramento

Fluxo desde o início da gravação até o encerramento (Ctrl+C) e upload em background.

```mermaid
sequenceDiagram
    participant U as Usuário
    participant M as main.py
    participant R as TeamsRecorder
    participant FF as FFmpeg
    participant H as Health Check (thread)
    participant UP as Upload (thread)

    U->>M: python main.py
    M->>M: setup_logging()
    M->>R: find_window()
    R->>R: pygetwindow.getAllWindows()
    alt Janela não encontrada
        R-->>M: None
        M-->>U: sys.exit(1)
    end
    M->>R: start()
    R->>R: _detect_teams_mode(title)
    R->>R: _build_ffmpeg_cmd(..., mode)
    R->>FF: Popen(cmd, stdin=PIPE)
    FF-->>R: processo
    R-->>M: (processo, out_path)

    M->>H: Thread( _monitor_health )
    H->>H: loop: tamanho do arquivo a cada N s
    M->>M: processo.wait()

    Note over U,FF: Usuário pressiona Ctrl+C
    U->>M: SIGINT / KeyboardInterrupt
    M->>FF: parar_gravacao() → communicate(input=b'q')
    FF->>FF: fecha container graciosamente
    M->>UP: Thread( _upload_em_background )
    M-->>U: "Gravação encerrada. Cópia/upload em background."
    UP->>UP: copiar_para_gdrive + upload_para_drive_api
    UP-->>U: "Upload/cópia em background concluídos."
```

---

## 5. Diagrama de classes (gravador)

Interface e implementação do gravador (padrão Strategy/Interface).

```mermaid
classDiagram
    class RecorderInterface {
        <<abstract>>
        +find_window()
        +start(sufixo) (processo, path)
    }

    class TeamsRecorder {
        +find_window() → _find_teams_window()
        +start(sufixo) → FFmpeg Popen + out_path
    }

    class FileManager {
        <<static>>
        +hash_sha256(path, show_progress)
        +hash_md5(path)
        +copy_to_gdrive_local(path)
        +verify_integrity_sha256(path, expected)
    }

    RecorderInterface <|-- TeamsRecorder
    TeamsRecorder ..> FileManager : copiar_para_gdrive
```

---

## 6. Diagrama de deployment (contexto de execução)

Onde cada parte roda: processo Python, subprocesso FFmpeg, threads.

```mermaid
flowchart LR
    subgraph Processo["Processo Python (main)"]
        T1["Thread principal\n(wait FFmpeg)"]
        T2["Thread Health Check\ndaemon"]
        T3["Thread Upload\nnão-daemon"]
    end

    subprocess["Subprocesso\nFFmpeg\n(gdigrab → AV1/HEVC/H.264)"]

    Processo --> subprocess
    T1 --> subprocess
    T2 --> arquivo["Arquivo .mkv/.mp4\n(out_path)"]
    T3 --> gdrive["Google Drive\n(cópia ou API)"]
```

---

## 7. Mapa de arquivos do projeto

| Caminho | Responsabilidade |
|---------|------------------|
| `main.py` | Ponto de entrada; setup logging; busca janela; inicia gravação; health check (thread); trata Ctrl+C/SIGTERM; dispara upload em thread. |
| `gravador.py` | `RecorderInterface`, `TeamsRecorder`; `_find_teams_window`, `_detect_teams_mode`, `_build_ffmpeg_cmd`, `_janela_em_foco`; `parar_gravacao`; `gravar()`, `copiar_para_gdrive()`. |
| `file_manager.py` | `FileManager`: hash SHA-256/MD5, cópia para pasta Drive local, verificação de integridade. |
| `upload_gdrive.py` | Autenticação OAuth; upload para Drive API; verificação de integridade pós-upload; credential scrubbing. |
| `config.py` | Leitura de `.env`; constantes (GRAVACOES_DIR, CODEC, CRF, FPS, health check, screen-share, etc.). |
| `logger_config.py` | Configuração Loguru: handler Rich (terminal), handler arquivo (auditoria em `logs/`). |
| `tests/` | Testes pytest (config, file_manager, gravador, logger_config, main, upload_gdrive). |
| `.github/workflows/tests.yml` | CI: pytest (Python 3.10–3.12), Ruff, cobertura mínima. |

---

## 8. Dependências externas

| Dependência | Uso |
|-------------|-----|
| **FFmpeg** | Captura (gdigrab), encoding (libsvtav1, libx265, libx264, hevc_nvenc), áudio (libopus). Obrigatório no PATH. |
| **pygetwindow** | Listar janelas e obter título/HWND para localizar a janela do Teams. |
| **python-dotenv** | Carregar `.env` em `config.py`. |
| **Loguru** | Logs estruturados. |
| **Rich** | Console colorido e handler de log no terminal. |
| **Google API (opcional)** | Upload para Drive (OAuth2 + Drive API). |

---

[⬆️ Voltar ao índice](README.md)
