# 🔒 GRC e Segurança

Este documento descreve os controles de **Governança, Risco e Compliance (GRC)** e **Segurança** implementados no Gravador de Aula — Teams FIAP.

---

## 1. Resumo dos controles

| Controle | Descrição | Onde |
|----------|-----------|------|
| **Leak prevention** | Aviso se a janela do Teams não estiver em foco (evitar gravar outras janelas/notificações). | `gravador._janela_em_foco` |
| **Credential scrubbing** | Em erros de autenticação ou upload, nunca imprimir token/creds nos logs. | `upload_gdrive._safe_auth_message` e tratamento de exceção no upload |
| **Integridade (hash)** | SHA-256 local; pós-upload comparação com SHA-256/MD5 do Drive. | `file_manager`, `upload_gdrive` |
| **Auditoria** | Logs em arquivo com rotação e retenção (logs/audit_*.log). | `logger_config` |
| **Encerramento gracioso** | Envio de `q` ao FFmpeg em vez de kill, para não corromper o arquivo. | `gravador.parar_gravacao`, `main` |

---

## 2. Leak prevention (janela em foco)

- **Risco:** Gravar conteúdo de outra janela (e-mail, Slack, notificações) por engano.
- **Controle:** Antes de iniciar a gravação, o código verifica se a janela do Teams é a **janela em foco** (foreground).
- **Implementação:** Em Windows, `ctypes.windll.user32.GetForegroundWindow()` é comparado ao HWND da janela encontrada. Se forem diferentes, um **aviso** é logado (a gravação não é bloqueada; o usuário pode corrigir colocando o Teams em foco).
- **Função:** `_janela_em_foco(win)` em `gravador.py`.

---

## 3. Credential scrubbing (privacidade)

- **Risco:** Em mensagens de erro (ex.: falha OAuth ou HttpError), o corpo da resposta ou a exceção pode conter **tokens** ou credenciais.
- **Controle:**
  - **Auth:** Em qualquer exceção no bloco de carregamento/refresh de credenciais, a mensagem logada é **genérica**: `"Erro de autenticação. Verifique credentials.json e token.json."` (função `_safe_auth_message`). O texto da exceção **não** é impresso.
  - **Upload:** Se a exceção no upload contiver as palavras `token`, `credentials`, `access_token` ou for muito longa (>200 caracteres), apenas a mensagem genérica é impressa: `"Erro no upload. Verifique permissões e rede."`
- **Arquivos:** `upload_gdrive.py`.

---

## 4. Integridade (cadeia de custódia)

- **Hash local:** O `FileManager` calcula **SHA-256** (e MD5 para compatibilidade com a API do Drive) do arquivo antes/depois de operações.
- **Pós-upload:** Após o upload para o Google Drive, o código obtém os metadados do arquivo (campos `sha256Checksum` e/ou `md5Checksum`) e **compara** com o hash local. Se divergirem, um **aviso** é logado (possível corrupção em trânsito).
- **Uso:** Verificação de integridade em `upload_gdrive.upload_para_drive_api` e funções de verificação em `file_manager`.

---

## 5. Auditoria (logs)

- **Terminal:** Logs com **Rich** (cores, markup); formato `FIAP-BOT | {message}`.
- **Arquivo:** Logs em `logs/audit_YYYY-MM-DD.log` com:
  - **Rotação:** 100 MB.
  - **Retenção:** 30 dias.
  - **Formato:** `timestamp | level | name:function:line - message`.
  - **Encoding:** UTF-8.
- **Segurança:** Os logs de arquivo não devem conter credenciais; as mensagens de erro já são sanitizadas (credential scrubbing).

---

## 6. Encerramento gracioso (resiliência)

- **Risco:** Encerrar o processo FFmpeg com `kill` ou `terminate` pode impedir que o **container** (MP4/MKV) feche o header corretamente, gerando arquivo **corrompido** ou não reproduzível.
- **Controle:** O encerramento é feito enviando o caractere **`q`** ao **stdin** do FFmpeg (`processo.communicate(input=b'q', timeout=5)`). O FFmpeg finaliza a gravação e escreve o header. Se não responder em 5 s, aí sim é feito `kill` (fallback).
- **Função:** `parar_gravacao(processo)` em `gravador.py`; chamada em **main** no tratamento de Ctrl+C e no handler de SIGTERM.

---

## 7. Checklist GRC (referência)

| Item | Status | Observação |
|------|--------|------------|
| Leak prevention | ✅ | Aviso quando janela não está em foco. |
| Credential scrubbing | ✅ | Mensagens genéricas em erros de auth/upload. |
| Integridade (hash) | ✅ | SHA-256/MD5 e verificação pós-upload. |
| Auditoria | ✅ | Logs rotativos em arquivo. |
| Encerramento gracioso | ✅ | `q` no stdin do FFmpeg antes de kill. |
| Uso de .env | ✅ | Credenciais e paths fora do código; .env no .gitignore. |

---

[⬆️ Voltar ao índice](README.md)
