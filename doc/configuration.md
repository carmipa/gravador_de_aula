# ⚙️ Configuração

Todas as opções do **Gravador de Aula** são controladas por **variáveis de ambiente**, carregadas a partir do arquivo **`.env`** na raiz do projeto (via `python-dotenv`). Nunca commite o `.env` (credenciais e paths locais).

---

## 1. Referência rápida (tabela)

| Variável | Tipo | Default | Descrição |
|----------|------|---------|-----------|
| `GRAVACOES_DIR` | string | `gravacoes/` (no projeto) | Pasta onde os vídeos são gravados. |
| `GDRIVE_PASTA_LOCAL` | string | *(vazio)* | Pasta local do Google Drive Desktop para copiar o arquivo. |
| `GDRIVE_PASTA_ID` | string | *(vazio)* | ID da pasta no Google Drive para upload via API. |
| `CODEC` | `av1` \| `hevc_nvenc` \| `hevc` \| `h264` | `av1` | Codec de vídeo. |
| `CRF` | 18–32 | `30` | Qualidade (maior = menor arquivo). |
| `FPS` | 15–60 | `30` | Frames por segundo. |
| `TEAMS_WINDOW_TITLE` | string | `Teams` | Trecho do título da janela do Teams para busca. |
| `AUDIO_DEVICE_DSHOW` | string | *(vazio)* | Dispositivo de áudio DShow (Windows). |
| `AV1_PRESET` | 0–13 | `10` | Preset do libsvtav1 (maior = mais lento, menor arquivo). |
| `HEALTH_CHECK_INTERVAL_SEC` | 5–60 | `10` | Intervalo (s) entre verificações de crescimento do arquivo. |
| `HEALTH_CHECK_STALL_SECONDS` | 15–120 | `30` | Tempo (s) sem crescimento para disparar alerta crítico. |
| `TEAMS_SCREEN_SHARE_KEYWORDS` | string | `Compartilhando|Screen|Partage|Sharing` | Palavras no título para modo “compartilhamento de tela”. |
| `CRF_OFFSET_SCREEN_SHARE` | 0–10 | `3` | Aumento de CRF no modo compartilhamento (arquivo menor). |

---

## 2. Saída e armazenamento

### 2.1 `GRAVACOES_DIR`

- **O que faz:** Define o diretório onde os arquivos de vídeo (`.mkv` ou `.mp4`) são salvos.
- **Default:** `gravacoes/` dentro da pasta do projeto.
- **Exemplo:** `GRAVACOES_DIR=D:\Gravações\Aulas`

### 2.2 `GDRIVE_PASTA_LOCAL`

- **O que faz:** Se definido, após encerrar a gravação o arquivo é **copiado** para esta pasta (ex.: pasta sincronizada pelo Google Drive para Desktop).
- **Default:** vazio (nenhuma cópia).
- **Exemplo:** `GDRIVE_PASTA_LOCAL=C:\Users\SeuUsuario\Google Drive\Meu Drive\Aulas FIAP`

### 2.3 `GDRIVE_PASTA_ID`

- **O que faz:** Se definido, após encerrar a gravação o arquivo é enviado para esta pasta no **Google Drive via API** (OAuth2).
- **Default:** vazio (nenhum upload via API).
- **Como obter o ID:** Abra a pasta no Drive no navegador; o ID está na URL: `https://drive.google.com/drive/folders/**ID_AQUI**`.

---

## 3. Vídeo e codec

### 3.1 `CODEC`

| Valor | Encoder | Extensão | Uso típico |
|-------|---------|----------|------------|
| `av1` | libsvtav1 | .mkv | Menor arquivo, ótima qualidade (recomendado). |
| `hevc_nvenc` | NVIDIA NVENC | .mp4 | GPU NVIDIA; gravação rápida. |
| `hevc` | libx265 | .mkv | CPU; bom compromisso tamanho/qualidade. |
| `h264` | libx264 | .mp4 | Máxima compatibilidade; arquivos maiores. |

### 3.2 `CRF`

- **18–22:** Mais qualidade, arquivo maior.
- **28–30:** Equilíbrio para aula (recomendado).
- **31–32:** Menor arquivo, menor qualidade.

### 3.3 `FPS`

- **15–60.** Valores típicos: 30 (padrão) ou 15 para aulas com pouco movimento (economiza espaço).

### 3.4 `AV1_PRESET` (só quando `CODEC=av1`)

- **0:** Mais rápido, arquivo maior.
- **10:** Default; bom para aulas.
- **13:** Mais lento, arquivo menor.

---

## 4. Detecção da janela e áudio

### 4.1 `TEAMS_WINDOW_TITLE`

- **O que faz:** A primeira janela cujo **título contém** essa string (case insensitive) é usada para gravação.
- **Default:** `Teams`.
- **Exemplo:** Se a janela for "Microsoft Teams - Reunião", `Teams` já basta.

### 4.2 `AUDIO_DEVICE_DSHOW`

- **O que faz:** Se definido, o FFmpeg usa este dispositivo como **segunda entrada** (áudio) e codifica com **libopus** (32 kbps).
- **Default:** vazio (apenas vídeo).
- **Como listar dispositivos:**  
  `ffmpeg -list_devices true -f dshow -i dummy`
- **Exemplo:** `AUDIO_DEVICE_DSHOW=audio=Linha 1 (Virtual Audio Cable)`

---

## 5. Health check e bitrate dinâmico

### 5.1 `HEALTH_CHECK_INTERVAL_SEC`

- **O que faz:** A cada N segundos o monitor verifica se o arquivo de saída aumentou de tamanho.
- **Range:** 5–60. **Default:** 10.

### 5.2 `HEALTH_CHECK_STALL_SECONDS`

- **O que faz:** Se o arquivo **não crescer** por esse número de segundos (com o processo FFmpeg ainda ativo), é emitido um **alerta crítico** nos logs (possível codec travado ou disco cheio).
- **Range:** 15–120. **Default:** 30.

### 5.3 `TEAMS_SCREEN_SHARE_KEYWORDS`

- **O que faz:** Se o **título da janela** contiver alguma dessas palavras (separadas por `|`), o modo é considerado **compartilhamento de tela** e o CRF é aumentado (arquivo menor).
- **Default:** `Compartilhando|Screen|Partage|Sharing`

### 5.4 `CRF_OFFSET_SCREEN_SHARE`

- **O que faz:** No modo compartilhamento de tela, o CRF efetivo é `CRF + CRF_OFFSET_SCREEN_SHARE` (limitado a 32).
- **Range:** 0–10. **Default:** 3.

---

## 6. Exemplo de `.env` completo

```env
# Saída
GRAVACOES_DIR=D:\Aulas
GDRIVE_PASTA_LOCAL=C:\Users\Voce\Google Drive\Aulas
# GDRIVE_PASTA_ID=1abc...xyz

# Vídeo
CODEC=av1
CRF=30
FPS=30
AV1_PRESET=10

# Janela e áudio
TEAMS_WINDOW_TITLE=Teams
# AUDIO_DEVICE_DSHOW=audio=Virtual Cable

# Health check e modo
HEALTH_CHECK_INTERVAL_SEC=10
HEALTH_CHECK_STALL_SECONDS=30
TEAMS_SCREEN_SHARE_KEYWORDS=Compartilhando|Screen|Partage|Sharing
CRF_OFFSET_SCREEN_SHARE=3
```

---

[⬆️ Voltar ao índice](README.md)
