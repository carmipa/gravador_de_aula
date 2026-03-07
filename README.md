<p align="center">
  <img src="https://raw.githubusercontent.com/carmipa/gravador_de_aula/main/assets/icon.png" alt="Gravador de Aula Teams FIAP" width="200" />
</p>

# FIAP Class Recorder

[![Tests & Lint](https://github.com/carmipa/gravador_de_aula/actions/workflows/tests.yml/badge.svg)](https://github.com/carmipa/gravador_de_aula/actions/workflows/tests.yml)
[![Release](https://github.com/carmipa/gravador_de_aula/actions/workflows/release.yml/badge.svg)](https://github.com/carmipa/gravador_de_aula/actions/workflows/release.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6)
![FFmpeg](https://img.shields.io/badge/FFmpeg-required-black)
![License](https://img.shields.io/badge/License-MIT-green)

Gravador pessoal de aulas no **Microsoft Teams** com **Python + FFmpeg**, foco em qualidade, automação e integridade.

> **📚 Documentação completa (arquitetura, configuração, fluxos, GRC, desenvolvimento):** [doc/](doc/README.md)

- **Requisitos:** Windows, FFmpeg no PATH, app Teams aberto (janela da reunião visível).
- **Uso:** rode o script antes ou durante a aula; para parar: **Ctrl+C**.
- **Saída:** vídeo na pasta `gravacoes/` (ou em `GRAVACOES_DIR`). Opcional: cópia para pasta do Google Drive ou upload via API.

---

## Preview

### Banner
![FIAP Class Recorder Banner](doc/banner.png)

### Screenshot
![FIAP Class Recorder Screenshot](doc/screenshot-terminal.png)

*Exemplo de execução com detecção da janela do Teams, inicialização do FFmpeg e início da gravação.*

---

## Instalação rápida

1. **FFmpeg**  
   Baixe em [ffmpeg.org](https://ffmpeg.org/download.html) (Windows builds) e coloque a pasta `bin` no PATH. Para **AV1** (arquivos menores), use um build com **libsvtav1** (ex.: [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases)).

2. **Ambiente (Windows)**  
   Use o script de setup na raiz do projeto:

   **Runtime básico:**
   ```powershell
   .\scripts\setup.ps1
   ```

   **Com Google Drive:**
   ```powershell
   .\scripts\setup.ps1 -GDrive
   ```

   **Com desenvolvimento (testes, ruff):**
   ```powershell
   .\scripts\setup.ps1 -Dev
   ```

   O script cria o `.venv`, instala o pacote (`pip install -e .` ou com extras) e copia `.env.example` para `.env` se não existir.

   **Alternativa manual:**
   ```bash
   cd gravador_de_aula
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```
   Com Drive: `pip install -e ".[gdrive]"` | Desenvolvimento: `pip install -e ".[dev]"`

3. **Configuração (opcional)**  
   Copie `.env.example` para `.env` e ajuste:
   - `GRAVACOES_DIR` – pasta das gravações (vazio = `gravacoes/` no projeto).
   - `CODEC` – `av1` (recomendado), `hevc_nvenc` (GPU NVIDIA), `hevc`, ou `h264`.
   - `CRF` – qualidade (28–30 para aulas).
   - `TEAMS_WINDOW_TITLE` – trecho do título da janela do Teams (default: `Teams`).

---

## Como usar

### Modo tradicional
```bash
python main.py
```

### Via CLI instalada (pacote)
```bash
pip install -e .
fiap-recorder
```

### Exemplos úteis

Listar janelas abertas (ajustar título no .env):
```bash
fiap-recorder --list-windows
```

Forçar codec e FPS:
```bash
fiap-recorder --codec av1 --fps 30 --crf 30
```

Não fazer upload nem cópia pós-gravação:
```bash
fiap-recorder --no-upload
```

Usar outro trecho do título da janela:
```bash
fiap-recorder --title "Microsoft Teams"
```

### Fluxo

1. Abra o **Microsoft Teams** e entre na reunião da aula (ou deixe a janela pronta para entrar).
2. Rode `python main.py` ou `fiap-recorder`.
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
pip install -r requirements-dev.txt   # inclui pytest, pytest-cov e ruff
pytest
```

Para relatório de cobertura: `pytest --cov=. --cov-report=term-missing`

**CI/CD:** a cada push/PR o GitHub Actions roda os testes (Python 3.10–3.12), Ruff (lint) e exige cobertura mínima de 85%. Veja [.github/workflows/tests.yml](.github/workflows/tests.yml).

---

## Desenvolvimento

Instalação editável (recomendado para contribuir):

```bash
pip install -e .[dev]
```

Executar testes:
```bash
pytest
```

Executar lint:
```bash
ruff check .
```

Entry point instalado: `fiap-recorder`

*Reorganização futura:* o código pode ser movido para `src/fiap_class_recorder/`; ver [doc/ESTRUTURA_FUTURA.md](doc/ESTRUTURA_FUTURA.md) para o modelo.

---

## Releases

As versões publicadas podem ser encontradas na aba [Releases](https://github.com/carmipa/gravador_de_aula/releases) do GitHub.

Ao usar tags (ex.: `v2.0.0`), a release é criada automaticamente pelo workflow [release.yml](.github/workflows/release.yml).

---

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
