# Estrutura futura (src layout)

**Não aplicar agora.** O repositório está funcional com os módulos na raiz. Esta página descreve uma possível etapa futura de maturação: reorganizar o código em layout `src/`.

## Estrutura sugerida

```
gravador_de_aula/
├── src/
│   └── fiap_class_recorder/
│       ├── __init__.py
│       ├── config.py
│       ├── file_manager.py
│       ├── gravador.py
│       ├── logger_config.py
│       ├── main.py
│       └── upload_gdrive.py
├── tests/
├── scripts/
├── doc/
├── pyproject.toml
└── README.md
```

## Ajuste no pyproject.toml

Quando decidir migrar, inclua algo como:

```toml
[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[project.scripts]
fiap-recorder = "fiap_class_recorder.main:cli"
```

O entry point `fiap-recorder` continua apontando para `fiap_class_recorder.main:cli`; apenas a localização dos arquivos muda para `src/fiap_class_recorder/`.
