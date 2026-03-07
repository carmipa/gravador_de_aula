# 📐 Diagramas

Os diagramas de arquitetura e fluxo estão **incorporados** nos documentos da pasta `doc/` em formato **Mermaid**. O **GitHub** renderiza Mermaid automaticamente ao visualizar os arquivos `.md`.

---

## Onde encontrar cada diagrama

| Diagrama | Arquivo | Descrição |
|----------|---------|-----------|
| Componentes | [../architecture.md](../architecture.md#2-diagrama-de-componentes-mermaid) | Módulos e dependências (main, gravador, file_manager, upload_gdrive, config, logger, FFmpeg, pygetwindow, Drive API). |
| Sequência — Gravação e encerramento | [../architecture.md](../architecture.md#3-diagrama-de-sequência--gravação-e-encerramento) | Fluxo desde `main.py` até Ctrl+C e upload em background. |
| Classes (gravador) | [../architecture.md](../architecture.md#4-diagrama-de-classes-gravador) | `RecorderInterface`, `TeamsRecorder`, `FileManager`. |
| Deployment | [../architecture.md](../architecture.md#5-diagrama-de-deployment-contexto-de-execução) | Processo Python, threads (health check, upload), subprocesso FFmpeg. |
| Fluxo geral | [../flows.md](../flows.md#1-fluxo-geral-alto-nível) | Fluxo alto nível: início → gravação → encerramento → upload. |
| Sequência — Health check | [../flows.md](../flows.md#6-diagrama-de-sequência--health-check) | Thread de monitoramento do crescimento do arquivo. |

---

## Renderizar localmente

- **[Mermaid Live Editor](https://mermaid.live/):** copie o bloco de código Mermaid do `.md` e cole no editor para ver ou exportar (PNG/SVG).
- **VS Code:** extensões como "Markdown Preview Mermaid Support" permitem visualizar os diagramas no preview do Markdown.

---

[⬆️ Voltar ao índice da documentação](../README.md)
