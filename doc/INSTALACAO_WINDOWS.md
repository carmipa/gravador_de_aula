# Instalação no Windows — guia rápido

Ordem recomendada para deixar o projeto e o FFmpeg acessíveis no sistema.

---

## 1. Entrar na pasta do projeto

```powershell
cd G:\PROJETOS-OPEN\gravador_de_aula
```

(Use o caminho real do seu clone.)

---

## 2. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear execução de scripts:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

Depois ative o venv de novo.

---

## 3. Instalar o projeto no sistema

Com o venv ativo:

```powershell
pip install -e .
```

- Com dependências de desenvolvimento: `pip install -e .[dev]`
- Com Google Drive: `pip install -e ".[gdrive]"`

---

## 4. Instalar o FFmpeg no Windows

**Sem FFmpeg no PATH a gravação não inicia.** Escolha uma opção.

### Opção A — winget

```powershell
winget install Gyan.FFmpeg
```

Feche e abra o terminal. Teste:

```powershell
ffmpeg -version
```

### Opção B — manual

1. Baixe o FFmpeg em [ffmpeg.org](https://ffmpeg.org/download.html) (Windows builds).
2. Extraia em `C:\ffmpeg` (ou outro caminho) e confirme que existe `C:\ffmpeg\bin\ffmpeg.exe`.
3. Adicione `C:\ffmpeg\bin` ao PATH do Windows (variáveis de ambiente).
4. Para testar na sessão atual do PowerShell:

```powershell
$env:Path += ";C:\ffmpeg\bin"
ffmpeg -version
```

---

## 5. Testar o projeto instalado

```powershell
fiap-recorder --list-windows
fiap-recorder --no-upload
```

Sem config de upload, o sistema usa a pasta `aula_video` no projeto.

---

## 6. Se `fiap-recorder` não for reconhecido

Rode pelo módulo:

```powershell
python -m main --list-windows
python -m main --no-upload
```

Ou reinstale com o venv ativo: `pip install -e .`

---

## 7. Resultado esperado (com FFmpeg no PATH)

- Detecta ausência de upload → usa `aula_video`
- Encontra a janela do Teams
- Inicia o FFmpeg
- Gera o arquivo `.mkv` (ou `.mp4`) na pasta local; para parar: **Ctrl+C**

---

## Comandos em sequência (copiar e colar)

```powershell
cd G:\PROJETOS-OPEN\gravador_de_aula
.\.venv\Scripts\Activate.ps1
pip install -e .
winget install Gyan.FFmpeg
# fechar e abrir o terminal
ffmpeg -version
fiap-recorder --list-windows
fiap-recorder --no-upload
```

O ponto crítico: **sem FFmpeg no PATH, a gravação nunca inicia.** Depois que `ffmpeg -version` funcionar, o gravador deve começar a gravar.
