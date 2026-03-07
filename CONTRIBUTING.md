# Contributing

Obrigado pelo interesse em contribuir com o projeto.

Este repositório foi criado com foco em **uso pessoal e educacional**, mas melhorias bem fundamentadas são bem-vindas.

---

## Objetivo do projeto

O foco principal é:

- gravar aulas no Microsoft Teams Desktop
- manter simplicidade operacional
- gerar arquivos confiáveis
- preservar boa qualidade com compressão adequada
- permitir automação opcional com Google Drive

Evite propostas que descaracterizem o projeto ou o transformem em algo excessivamente complexo sem ganho real.

---

## Como contribuir

### 1. Faça um fork
Crie seu fork do repositório e trabalhe em uma branch própria.

### 2. Crie uma branch descritiva
Exemplos:

- `feature/windows-ci`
- `fix/env-validation`
- `refactor/ffmpeg-builder`

### 3. Instale o ambiente
```bash
pip install -e .[dev]
```

### 4. Rode os testes
```bash
pytest
```

### 5. Rode o lint
```bash
ruff check .
```

---

## Tipos de contribuição aceitos

**Bem-vindos:** correções de bugs, melhorias de robustez, testes, documentação, melhorias de logging, compatibilidade Windows, melhorias no fluxo de FFmpeg, melhorias no empacotamento.

**Devem ser discutidos antes:** mudança radical de arquitetura, conversão para GUI completa, integração com serviços externos adicionais, telemetria, automações agressivas, recursos que possam impactar privacidade ou conformidade.

---

## Padrões esperados

- mantenha o código simples
- prefira legibilidade
- evite dependências desnecessárias
- preserve compatibilidade com Windows
- não introduza comportamentos que ocultem falhas críticas
- documente mudanças que afetem uso, instalação ou configuração

---

## Commits

Prefira mensagens claras, por exemplo:

- `fix: validação de CRF no config`
- `feat: adiciona listagem de janelas via CLI`
- `test: cobre fallback de codec inválido`

---

## Pull Requests

Ao abrir um PR, inclua: objetivo da mudança, problema que ela resolve, impacto esperado, como validar. Screenshots ou logs, se fizer sentido.

---

## Versionamento

O projeto segue versionamento semântico sempre que possível:

- **MAJOR:** mudanças incompatíveis
- **MINOR:** novas funcionalidades compatíveis
- **PATCH:** correções e ajustes menores

Releases são criadas automaticamente ao empurrar uma tag `v*` (ex.: `v2.0.0`). Comandos sugeridos:

```bash
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0
```

Ou sem anotação: `git tag v2.0.0` e `git push origin v2.0.0`.

---

## Observação importante

Este projeto lida com gravação de aulas. Contribuições devem respeitar privacidade, uso responsável, contexto educacional e políticas institucionais e da plataforma.
