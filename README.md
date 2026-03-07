<p align="center">
  <img src="https://raw.githubusercontent.com/carmipa/gravador_de_aula/main/assets/icon.png" alt="Gravador de Aula Teams FIAP" width="200" />
</p>

# 🎥 FIAP Class Recorder | Cybersecurity & GRC Automation

<p align="center">
  <a href="https://github.com/carmipa/gravador_de_aula/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/carmipa/gravador_de_aula/tests.yml?branch=main&style=for-the-badge&logo=github" alt="Tests & Lint" /></a>
  <img src="https://img.shields.io/badge/Coverage-85%25-brightgreen?style=for-the-badge&logo=pytest" alt="Coverage" />
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?style=for-the-badge&logo=python" alt="Python" /></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/Code%20Style-Ruff-000000?style=for-the-badge&logo=ruff" alt="Ruff" /></a>
  <a href="https://www.microsoft.com/windows"><img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows" alt="Platform Windows" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License MIT" /></a>
</p>

Bot para gravar a janela do **Microsoft Teams (app desktop)** durante aulas online, com arquivos pequenos e boa qualidade (AV1/HEVC/H.264). Uso pessoal: não perder nada da aula.

> **📚 Documentação completa (arquitetura, configuração, fluxos, GRC, desenvolvimento):** [doc/](doc/README.md)

- **Requisitos:** Windows, FFmpeg no PATH, app Teams aberto (janela da reunião visível).
- **Uso:** rode o script antes ou durante a aula; para parar: **Ctrl+C**.
- **Saída:** vídeo na pasta `gravacoes/` (ou em `GRAVACOES_DIR`). Opcional: cópia para pasta do Google Drive ou upload via API.

---

## Instalação rápida

1. **FFmpeg**  
   Baixe em [ffmpeg.org](https://ffmpeg.org/download.html) (Windows builds) e coloque a pasta `bin` no PATH. Para **AV1** (arquivos menores), use um build com **libsvtav1** (ex.: [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases)).

2. **Python e dependências**
   ```bash
   cd gravador_de_aula
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Inclui **Rich** (interface no terminal) e **Loguru** (logs e auditoria).

3. **Configuração (opcional)**  
   Copie `.env.example` para `.env` e ajuste:
   - `GRAVACOES_DIR` – pasta das gravações (vazio = `gravacoes/` no projeto).
   - `CODEC` – `av1` (recomendado), `hevc_nvenc` (GPU NVIDIA), `hevc`, ou `h264`.
   - `CRF` – qualidade (28–30 para aulas).
   - `TEAMS_WINDOW_TITLE` – trecho do título da janela do Teams (default: `Teams`).

---

## Como usar

1. Abra o **Microsoft Teams** e entre na reunião da aula (ou deixe a janela pronta para entrar).
2. No terminal (com o venv ativado):
   ```bash
   python main.py
   ```
3. O bot detecta a janela do Teams e inicia a gravação. Para **parar**: **Ctrl+C** no terminal.
4. O arquivo fica em `gravacoes/` (ex.: `aula_2026-03-06_14-30.mkv`).

---

## Salvar no Google Drive

**Opção A – Pasta local (mais simples)**  
Se você usa **Google Drive para Desktop**, defina no `.env`:

```env
GDRIVE_PASTA_LOCAL=C:\Users\SeuUsuario\Google Drive\Meu Drive\Aulas FIAP
```

Ao encerrar a gravação (Ctrl+C), o script **copia** o arquivo para essa pasta; o Drive faz o upload automático.

**Opção B – Upload via API**  
Para enviar direto pela API do Google Drive:

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com), ative a **Google Drive API** e crie credenciais **OAuth 2.0 (aplicativo desktop)**.
2. Baixe o JSON e renomeie para `credentials.json` na pasta do projeto.
3. No `.env`, defina o ID da pasta do Drive onde quer salvar:
   ```env
   GDRIVE_PASTA_ID=1abc...xyz
   ```
   (O ID está na URL ao abrir a pasta no Drive.)
4. Na primeira execução com upload, o navegador abrirá para você autorizar; depois o script usa `token.json` automaticamente.

---

## Codecs e qualidade

| Codec        | Uso recomendado              | Tamanho ~1h (1080p) |
|-------------|-------------------------------|----------------------|
| **av1**     | Menor arquivo, ótima qualidade | ~400 MB              |
| **hevc_nvenc** | GPU NVIDIA, rápido          | ~600 MB              |
| **hevc**    | CPU (libx265)                 | ~600 MB              |
| **h264**    | Máxima compatibilidade        | ~1,5 GB              |

Ajuste `CRF` no `.env`: **18–22** = mais qualidade (arquivo maior), **28–30** = equilíbrio para aula.

---

## Observações

- **Encerramento:** ao dar **Ctrl+C**, o script envia `q` ao FFmpeg para fechar o container graciosamente (evita arquivo corrompido por cabeçalho não finalizado).
- **Áudio:** a captura é da **janela** (gdigrab). Para áudio interno (ex.: saída do Teams), configure no `.env` o dispositivo DShow: `AUDIO_DEVICE_DSHOW=audio=...`. Liste dispositivos com: `ffmpeg -list_devices true -f dshow -i dummy`.
- **AV1:** preset padrão 10 (mais lento, arquivos menores para aulas). Ajuste com `AV1_PRESET` (0–13) no `.env`.
- **Health check:** o bot verifica se o arquivo de saída está crescendo; se parar por 30 s (configurável), dispara alerta crítico (codec pode ter travado).
- **Upload em background:** cópia para Drive e upload via API rodam em thread separada; o terminal libera logo após encerrar a gravação.
- **Bitrate dinâmico:** se o título da janela indicar compartilhamento de tela (ex.: "Compartilhando"), o CRF é aumentado para gerar arquivo menor. Configure `TEAMS_SCREEN_SHARE_KEYWORDS` e `CRF_OFFSET_SCREEN_SHARE` no `.env`.
- **Segurança (GRC):** o bot avisa se a janela do Teams não está em foco (evitar gravar notificações de outras janelas). Upload via API não imprime credenciais em erros; após upload é feita verificação de integridade (SHA-256/MD5 local vs Drive).
- **Observabilidade:** logs no terminal via **Rich** (cores, ícones); auditoria em `logs/audit_YYYY-MM-DD.log` (rotação 100 MB, retenção 30 dias). Exceções não tratadas são capturadas e logadas com traceback (`@logger.catch`).
- **Política de uso:** use apenas para estudo pessoal e respeite os termos da FIAP e do Microsoft Teams.

---

## Testes

O projeto tem suíte de testes com **pytest**. Para rodar:

```bash
.venv\Scripts\activate
pip install -r requirements.txt   # inclui pytest e pytest-cov
pytest
```

Para relatório de cobertura: `pytest --cov=. --cov-report=term-missing`

**CI/CD:** a cada push/PR o GitHub Actions roda os testes (Python 3.10–3.12), Ruff (lint) e exige cobertura mínima de 85%. Veja [.github/workflows/tests.yml](.github/workflows/tests.yml).
