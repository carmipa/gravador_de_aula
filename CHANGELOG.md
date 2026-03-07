# Changelog

Todas as mudanças relevantes deste projeto serão documentadas aqui.

O formato segue uma linha inspirada em [Keep a Changelog](https://keepachangelog.com/) e versionamento semântico.

---

## [2.0.0] - 2026-03-06

### Adicionado
- CLI com `argparse`
- comando `fiap-recorder` via `pyproject.toml`
- suporte a overrides por linha de comando:
  - `--codec`
  - `--fps`
  - `--crf`
  - `--title`
  - `--no-upload`
  - `--list-windows`
- `pyproject.toml` com extras:
  - `gdrive`
  - `dev`
- README reestruturado e mais profissional
- novos testes para config, gravador (sanitize, output_base, screen-share) e CLI
- workflow preparado para Linux e Windows
- separação de dependências:
  - `requirements.txt`
  - `requirements-gdrive.txt`
  - `requirements-dev.txt`
- `_sanitize_filename` e `_build_output_base` no gravador (helpers para nomes de arquivo)

### Alterado
- robustez da leitura de variáveis de ambiente
- clamp e fallback para `CRF`, `FPS` e `AV1_PRESET`
- melhoria na escolha da janela do Teams (prioridade: screen-share, foco, área)
- padronização dos logs com `loguru`
- melhoria no fluxo de pós-processamento
- estrutura geral do projeto preparada para distribuição como pacote

### Corrigido
- risco de quebra por `.env` com valores inválidos
- inconsistências entre logs do runtime e logs do upload
- problemas de manutenção por dependências opcionais misturadas
- ausência de cobertura explícita para execução em Windows no CI

---

## [1.x] - anterior

### Existente na base inicial
- gravação da janela do Teams com FFmpeg
- suporte a AV1 / HEVC / H.264
- health check do arquivo de saída
- cópia para pasta local do Google Drive
- upload opcional via API
- logs e testes básicos
