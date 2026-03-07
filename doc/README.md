# 📚 Documentação — Gravador de Aula Teams FIAP

<p align="center">
  <img src="https://raw.githubusercontent.com/carmipa/gravador_de_aula/main/assets/icon.png" alt="Ícone do projeto — Gravador de Aula Teams FIAP" width="128" />
</p>

<p align="center">
  <a href="https://github.com/carmipa/gravador_de_aula/actions/workflows/tests.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/carmipa/gravador_de_aula/tests.yml?branch=main&label=Tests%20%26%20Lint&logo=github" alt="Tests & Lint" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white" alt="Python" />
  </a>
  <a href="https://www.microsoft.com/windows">
    <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Platform Windows" />
  </a>
  <a href="../LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License MIT" />
  </a>
</p>

> Documentação técnica completa: arquitetura, configuração, fluxos, GRC e desenvolvimento.  
> **README principal do projeto:** [../README.md](../README.md)

---

## 🏗️ Diagrama de arquitetura

Visão dos módulos e dependências (o GitHub renderiza o Mermaid abaixo automaticamente):

```mermaid
flowchart TB
    subgraph Entrada["🎬 Entrada"]
        MAIN["main.py\nOrquestração"]
    end

    subgraph Nucleo["⚙️ Núcleo"]
        GRAV["gravador.py\nTeamsRecorder"]
        FM["file_manager.py\nFileManager"]
        UPL["upload_gdrive.py\nUpload API"]
    end

    subgraph Infra["🔧 Infraestrutura"]
        CFG["config.py"]
        LOG["logger_config.py"]
    end

    subgraph Externos["🌐 Externos"]
        FF["FFmpeg"]
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

Mais diagramas (sequência, classes, deployment): **[Arquitetura (detalhes)](architecture.md)**.

---

## 📑 Índice da documentação

| Ícone | Documento | Conteúdo |
|-------|-----------|----------|
| 🏗️ | [**Arquitetura**](architecture.md) | Diagramas de componentes, sequência, classes e deployment (Mermaid). |
| ⚙️ | [**Configuração**](configuration.md) | Todas as variáveis de ambiente, defaults e opções avançadas. |
| 🔀 | [**Fluxos**](flows.md) | Fluxo de gravação, health check, encerramento gracioso e upload em background. |
| 🔒 | [**GRC e Segurança**](grc-security.md) | Leak prevention, credential scrubbing, integridade (SHA-256/MD5), auditoria. |
| 🧪 | [**Desenvolvimento**](development.md) | Testes (pytest), CI/CD (GitHub Actions), lint (Ruff), cobertura. |
| 📐 | [**Diagramas**](diagrams/README.md) | Referência de todos os diagramas Mermaid. |

---

## 🎯 Visão geral do projeto

```
┌─────────────────────────────────────────────────────────────────┐
│  Gravador de Aula — Teams FIAP                                   │
│  Grava a janela do Microsoft Teams (gdigrab + FFmpeg)            │
│  com codecs AV1/HEVC/H.264 e opcional upload para Google Drive.  │
└─────────────────────────────────────────────────────────────────┘
```

- **Entrada:** janela do Teams (título configurável), opcional áudio DShow.
- **Saída:** arquivo de vídeo em `gravacoes/` (ou `GRAVACOES_DIR`), opcional cópia/upload para Drive.
- **Controles:** Health check (arquivo crescendo), encerramento gracioso (`q` no FFmpeg), upload em thread.

Para **instalação e uso rápido**, use o [README na raiz](../README.md).
