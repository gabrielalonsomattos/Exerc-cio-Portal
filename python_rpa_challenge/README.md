# Desafio Python RPA

Este projeto implementa uma solução inicial para o desafio de automação do Portal da Transparência.

## Funcionalidades
- Entrada de nome/CPF e filtros por interface local
- Geração de payload para automação
- Exportação de resultado em JSON
- Estrutura pronta para integrar Selenium/Playwright

## Como executar
1. Instale Python 3.10+
2. Execute:
   ```bash
   py -3 app.py
   ```
3. Preencha os campos e clique em Executar
4. Salve o resultado em JSON

## Observações
A automação web real depende de um navegador e driver instalados na máquina. O projeto já conta com uma camada de fallback que gera o JSON mesmo sem a execução da navegação completa.
