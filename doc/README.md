<p align="center">
  <img src="../assets/Gemini_Generated_Image_v1insnv1insnv1in.png" alt="Ícone do projeto — Gravador de Aula Teams FIAP" width="120" />
</p>

# 📚 Documentação — Gravador de Aula Teams FIAP

> Documentação técnica completa: arquitetura, configuração, fluxos, GRC e desenvolvimento.  
> **README principal do projeto:** [../README.md](../README.md)

---

## 🛡️ Badges (GitHub)

| Badge | Descrição |
|-------|-----------|
| [![Tests & Lint](https://img.shields.io/github/actions/workflow/status/carmipa/gravador_de_aula/tests.yml?branch=main&label=Tests%20%26%20Lint&logo=github)](https://github.com/carmipa/gravador_de_aula/actions/workflows/tests.yml) | CI: testes + Ruff |
| [![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/) | Versões suportadas |
| [![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)](https://www.microsoft.com/windows) | Plataforma alvo |
| [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE) | Licença |

---

## 📑 Índice da documentação

| Ícone | Documento | Conteúdo |
|-------|-----------|----------|
| 🏗️ | [**Arquitetura**](architecture.md) | Visão do sistema, diagramas de componentes, sequência e deployment (Mermaid). |
| ⚙️ | [**Configuração**](configuration.md) | Todas as variáveis de ambiente, defaults e opções avançadas. |
| 🔀 | [**Fluxos**](flows.md) | Fluxo de gravação, health check, encerramento gracioso e upload em background. |
| 🔒 | [**GRC e Segurança**](grc-security.md) | Leak prevention, credential scrubbing, integridade (SHA-256/MD5), auditoria. |
| 🧪 | [**Desenvolvimento**](development.md) | Testes (pytest), CI/CD (GitHub Actions), lint (Ruff), cobertura. |
| 📐 | [**Diagramas**](diagrams/README.md) | Referência dos diagramas Mermaid (componentes, sequência, classes, deployment). |

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
