# Gravador de Aula - Teams FIAP

Bot para gravar a janela do **Microsoft Teams (app desktop)** durante aulas online, com arquivos pequenos e boa qualidade (AV1/HEVC/H.264). Uso pessoal: não perder nada da aula.

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

- **Áudio:** a captura é da **janela** (gdigrab). No Windows o áudio do sistema costuma ir junto; se não for o caso, você pode usar um cabo de áudio virtual (ex.: VB-Cable) e configurar o FFmpeg para capturar esse dispositivo.
- **Segurança:** não coloque senhas no código; use apenas o `.env` (e não faça commit do `.env`).
- **Política de uso:** use apenas para estudo pessoal e respeite os termos da FIAP e do Microsoft Teams.
