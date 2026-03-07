# Security Policy

## Escopo

Este projeto é uma ferramenta local de automação para gravação de aulas no Microsoft Teams Desktop, com opção de cópia local e upload para Google Drive.

Questões de segurança relevantes incluem:

- vazamento de credenciais
- exposição de tokens OAuth
- upload indevido de arquivos
- logs com dados sensíveis
- manipulação insegura de caminhos e arquivos
- dependências vulneráveis

---

## Boas práticas adotadas

- uso local e pessoal como cenário principal
- separação entre runtime, Google Drive e dependências de desenvolvimento
- tratamento cuidadoso de erros de autenticação
- tentativa de evitar exposição direta de credenciais em mensagens de erro (credential scrubbing)
- uso de `.env` para configuração local
- suporte a testes automatizados

---

## O que não deve ser commitado

Nunca envie para o repositório:

- `.env`
- `credentials.json`
- `token.json`
- vídeos gravados
- logs contendo dados sensíveis
- caminhos pessoais do seu sistema
- IDs privados de pastas, quando não necessário

---

## Reportando vulnerabilidades

Se você identificar uma vulnerabilidade relevante, reporte de forma responsável ao mantenedor.

Inclua, se possível: descrição do problema, impacto, como reproduzir, sugestão de correção, versão afetada.

Evite divulgar publicamente detalhes exploráveis antes da correção.

---

## Recomendações para usuários

- mantenha `credentials.json`, `token.json` e `.env` fora do Git
- use permissões mínimas necessárias na API do Google Drive
- revise seus logs antes de compartilhá-los
- teste primeiro com arquivos curtos
- atualize dependências periodicamente
