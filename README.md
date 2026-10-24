# Sistema Bancário em Python

Sistema bancário desenvolvido em Python com foco em boas práticas de programação, experiência de utilizador (UX) e segurança de dados

## 🛡️ Principais Funcionalidades e Segurança
* **Criptografia Hash (SHA-256)**: Tanto as palavras-passe (PIN) quanto os CPFs são convertidos em códigos hash irreversíveis no disco, garantindo privacidade total.
* **Persistência de Dados (JSON)**: Os dados de utilizadores e contas são armazenados de forma estruturada no ficheiro `dados_banco.json`, mantendo as informações entre sessões.
* **Tratamento de Erros (`try-except`)**: Proteção contra falhas e *crashes* caso o utilizador insira caracteres ou letras inválidas onde se esperam números.
* **Privacidade Visual**: Mascaramento automático de CPFs na ecrã (ex: `***.456.789-**`) seguindo padrões reais de proteção de dados.
* **Autenticação Segura**: Sistema de login por múltiplos fatores exigindo CPF e palavra-passe encriptada.

## 📁 Estrutura do Projeto
* `operacao_b2.py`: Script principal com toda a lógica de operação, menus blindados e funções bancárias.
* `dados_banco.json`: Base de dados local gerada automaticamente para persistência segura das informações.

## 🚀 Como Executar
1. Certifique-se de ter o **Python** instalado no seu computador.
2. Clone este repositório:
   ```bash
   git clone [https://github.com/Cosme855/sistema-bancario-python.git]
3. Aceda à pasta do projeto e execute o script pelo terminal: "python operacao_b2.py"

Aproveita a experiencia, qualquer atualização estaremos informando durante o processo.
