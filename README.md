# Sistema Bancário em Python (Arquitetura POO) v.0.3

Sistema bancário desenvolvido em Python com foco em boas práticas de programação.

## 🚀 Evolução para POO: Por que fizemos esta mudança?

Inicialmente estruturado de forma procedural (com funções e dicionários), o projeto foi totalmente refatorado para o modelo orientado a objetos seguindo rigorosamente o **diagrama UML** proposto pela DIO. Esta transição trouxe ganhos fundamentais:

* **Conformidade Arquitetural (UML)**: Implementação correta de classes essenciais como `Cliente`, `PessoaFisica`, `Conta`, `ContaCorrente`, `ContaSalario`, `Historico`, `Transacao`, `Deposito` e `Saque`.
* **Encapsulamento e Organização**: Cada entidade do sistema passou a gerir o seu próprio comportamento e dados (ex: o saldo, o histórico e as validações pertencem à classe `Conta`), eliminando variáveis globais e acoplamento excessivo.
* **Herança e Polimorfismo**: Reaproveitamento de código inteligente através de classes-mãe (`Cliente` e `Conta`) e especializações (`ContaCorrente` e `ContaSalario`), tornando o sistema limpo e preparado para futuras expansões.
* **Escalabilidade e Portfólio**: Eleva o nível técnico do projeto, demonstrando domínio de padrões de projeto robustos e de mercado.

## 🛡️ Principais Funcionalidades e Segurança

* **Criptografia Hash (SHA-256)**: Tanto as palavras-passe (PIN) quanto os CPFs são convertidos em códigos hash irreversíveis no disco, garantindo privacidade total.
* **Persistência de Dados (JSON)**: Os dados de utilizadores e contas são armazenados de forma estruturada no ficheiro `dados_banco.json`, mantendo as informações entre sessões com migração automática integrada.
* **Múltiplas Contas e Tipos (Corrente e Salário)**: Um único cliente pode possuir diferentes contas associadas ao seu CPF, com limites de transação e saques independentes.
* **Auditoria Temporal (Datetime)**: Registo automático de data e hora em todas as transações, garantindo um extrato detalhado e controlo de limite diário (até 10 operações por dia).
* **Tratamento de Erros (`try-except`)**: Proteção contra falhas e *crashes* caso o utilizador insira caracteres ou letras inválidas onde se esperam números.
* **Privacidad Visual**: Mascaramento automático de CPFs na ecrã (ex: `***.456.789-**`) seguindo padrões reais de proteção de dados.
* **Autenticação Segura**: Sistema de login por múltiplos fatores exigindo CPF e palavra-passe encriptada, com menu de seleção inteligente para contas múltiplas.

## 📁 Estrutura do Projeto

* `operacao_b2.py`: Script principal com toda a lógica de operação, menus blindados, gestão de utilizadores e funções bancárias.
* `dados_banco.json`: Base de dados local gerada automaticamente para persistência segura das informações.

## 🚀 Como Executar
1. Certifique-se de ter o **Python** instalado no seu computador.
2. Clone este repositório:
   ```bash
   git clone https://github.com/Cosme855/sistema-bancario-python.git
3. abra o arquivo : operacao_b2.py
ou Abra à pasta do projeto por um IDE python e execute o script pelo terminal: "python operacao_b2.py"

Aproveita a experiencia, qualquer atualização estaremos informando durante o processo.
