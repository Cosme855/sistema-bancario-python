""" Sistema Bancário em Python  """


import json
import os
import hashlib
from datetime import datetime
from abc import ABC, abstractmethod

ARQUIVO_DADOS = "dados_banco_poo.json"

def criar_hash(texto):
    """Gera um hash SHA-256 para proteger dados sensíveis (CPFs e Pins)."""
    return hashlib.sha256(texto.encode()).hexdigest()

def formatar_e_mascarar_cpf(cpf):
    """Privacidade Visual: Oculta os dígitos centrais do CPF no ecrã."""
    apenas_digitos = "".join([c for c in cpf if c.isdigit()])
    if len(apenas_digitos) == 11:
        return f"***.{apenas_digitos[3:6]}.{apenas_digitos[6:9]}-**"
    return "***.***.***-**"

def obter_valor_numerico(mensagem):
    """Garante que o programa não quebra se forem inseridas letras."""
    while True:
        try:
            valor = float(input(mensagem))
            return valor
        except ValueError:
            print("\n❌ Erro de formato: Por favor, informe apenas números válidos.")


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, tipo, valor):
        agora = datetime.now()
        self._transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "data_iso": agora.strftime("%Y-%m-%d %H:%M:%S"),
            "data_formatada": agora.strftime("%d/%m/%Y %H:%M:%S")
        })


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.verificar_limite_transacoes():
            print("\n❌ Operação falhou! Excedeu o limite máximo de 10 transações diárias.")
            return False

        if self.valor > 0:
            conta._saldo += self.valor
            conta.historico.adicionar_transacao("Depósito", self.valor)
            print(f"\n✅ Depósito de R$ {self.valor:.2f} realizado com sucesso!")
            return True
        else:
            print("\n❌ Operação falhou! O valor informado deve ser maior que zero.")
            return False


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.verificar_limite_transacoes():
            print("\n❌ Operação falhou! Excedeu o limite máximo de 10 transações diárias.")
            return False

        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao("Saque", self.valor)
        return sucesso


class Conta:
    def __init__(self, numero, cliente, tipo_conta="corrente", senha_hash="", limite=5000.0, saldo=0.0, numero_saques=0):
        self._saldo = saldo
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
        self._tipo_conta = tipo_conta
        self._senha_hash = senha_hash
        self._limite = limite
        self._numero_saques = numero_saques

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @property
    def tipo_conta(self):
        return self._tipo_conta

    @property
    def senha_hash(self):
        return self._senha_hash

    @property
    def limite(self):
        return self._limite

    @property
    def numero_saques(self):
        return self._numero_saques

    def verificar_limite_transacoes(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        transacoes_hoje = [t for t in self.historico.transacoes if t["data_iso"].startswith(hoje)]
        return len(transacoes_hoje) >= 10

    @classmethod
    def nova_conta(cls, cliente, numero, tipo_conta, senha, limite):
        return cls(numero, cliente, tipo_conta=tipo_conta, senha_hash=criar_hash(senha), limite=limite)

    def sacar(self, valor):
        if valor > self._saldo:
            print("\n❌ Operação falhou! Saldo insuficiente.")
            return False
        elif valor > self._limite:
            print(f"\n❌ Operação falhou! O valor excede o limite máximo por saque de R$ {self._limite:.2f}.")
            return False
        elif self._numero_saques >= 5:
            print("\n❌ Operação falhou! Número máximo de saques diários atingido.")
            return False
        elif valor > 0:
            self._saldo -= valor
            self._numero_saques += 1
            print(f"\n✅ Saque de R$ {valor:.2f} realizado com sucesso!")
            return True
        else:
            print("\n❌ Operação falhou! O valor informado é inválido.")
            return False

    def depositar(self, valor):
        transacao = Deposito(valor)
        return transacao.registrar(self)


class ContaCorrente(Conta):
    pass


class ContaSalario(Conta):
    pass


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf_hash, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf_hash = cpf_hash


def carregar_sistema():
    """Carrega clientes e contas do ficheiro JSON e reconstrói os objetos."""
    clientes = []
    contas = []

    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
                
                # Carregar clientes
                dic_clientes = {}
                for c_data in dados.get("clientes", []):
                    cli = PessoaFisica(
                        nome=c_data["nome"],
                        data_nascimento=c_data["data_nascimento"],
                        cpf_hash=c_data["cpf_hash"],
                        endereco=c_data["endereco"]
                    )
                    dic_clientes[c_data["cpf_hash"]] = cli
                    clientes.append(cli)

                # Carregar contas
                for acc_data in dados.get("contas", []):
                    cli = dic_clientes.get(acc_data["cpf_titular_hash"])
                    if cli:
                        conta = Conta(
                            numero=acc_data["numero_conta"],
                            cliente=cli,
                            tipo_conta=acc_data["tipo_conta"],
                            senha_hash=acc_data["senha_hash"],
                            limite=acc_data["limite"],
                            saldo=acc_data["saldo"],
                            numero_saques=acc_data["numero_saques"]
                        )
                        # Restaurar histórico
                        for t in acc_data.get("historico", []):
                            conta.historico.transacoes.append(t)
                        
                        cli.adicionar_conta(conta)
                        contas.append(conta)
        except json.JSONDecodeError:
            print("\n⚠️ Aviso: Ficheiro corrompido. A iniciar com base limpa.")
            return [], []
    return clientes, contas


def salvar_sistema(clientes, contas):
    """Salva o estado atual dos objetos em formato JSON estruturado."""
    dados_clientes = []
    for cli in clientes:
        dados_clientes.append({
            "nome": cli.nome,
            "data_nascimento": cli.data_nascimento,
            "cpf_hash": cli.cpf_hash,
            "endereco": cli.endereco
        })

    dados_contas = []
    for acc in contas:
        dados_contas.append({
            "agencia": acc.agencia,
            "numero_conta": acc.numero,
            "tipo_conta": acc.tipo_conta,
            "cpf_titular_hash": acc.cliente.cpf_hash,
            "senha_hash": acc.senha_hash,
            "saldo": acc.saldo,
            "limite": acc.limite,
            "numero_saques": acc.numero_saques,
            "historico": acc.historico.transacoes
        })

    dados = {
        "clientes": dados_clientes,
        "contas": dados_contas
    }

    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


def criar_utilizador(clientes, contas):
    cpf_input = input("Informe o CPF do cliente (apenas números): ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    
    if len(cpf_limpo) != 11:
        print("\n❌ Segurança: CPF inválido! Deve conter exatamente 11 dígitos.")
        return None
    
    cpf_hash_novo = criar_hash(cpf_limpo)

    for c in clientes:
        if c.cpf_hash == cpf_hash_novo:
            print("\n❌ Operação negada: Já existe um utilizador registado com este CPF!")
            return c

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")

    print("\n--- Dados do Endereço ---")
    rua = input("Informe a rua: ")
    bairro = input("Informe o bairro: ")
    cidade_estado = input("Informe a cidade/sigla estado (ex: Rio de Janeiro/RJ): ")
    endereco = f"{rua} - {bairro} - {cidade_estado}"

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf_hash=cpf_hash_novo, endereco=endereco)
    clientes.append(cliente)
    salvar_sistema(clientes, contas)
    
    print(f"\n🎉 Utilizador cadastrado com sucesso!")
    print(f"🛡️ CPF Protegido (Hash): {formatar_e_mascarar_cpf(cpf_limpo)}")
    return cliente


def criar_nova_conta(clientes, contas):
    if not clientes:
        print("\n❌ Nenhum utilizador cadastrado. Cadastre o utilizador primeiro (Opção 2).")
        return None

    cpf_input = input("Informe o CPF do titular para vincular a conta: ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    cpf_hash_busca = criar_hash(cpf_limpo)

    cliente_encontrado = None
    for c in clientes:
        if c.cpf_hash == cpf_hash_busca:
            cliente_encontrado = c
            break

    if not cliente_encontrado:
        print("\n❌ Utilizador não encontrado! Por favor, cadastre o utilizador primeiro.")
        return None

    print("\n--- Selecione o Tipo de Conta ---")
    print("[1] Conta Corrente (Limite de saque: R$ 5000.00)")
    print("[2] Conta Salário (Limite de saque: R$ 2500.00)")
    tipo_opcao = input("Escolha o tipo (1 ou 2): ").strip()
    
    tipo_conta = "salario" if tipo_opcao == "2" else "corrente"
    nome_tipo = "Conta Salário" if tipo_conta == "salario" else "Conta Corrente"
    limite_conta = 5000.0 if tipo_conta == "corrente" else 2500.0

    while True:
        senha = input("Crie uma palavra-passe/PIN numérico de 4 dígitos para esta conta: ")
        if senha.isdigit() and len(senha) == 4:
            break
        print("\n❌ A senha deve conter exatamente 4 números.")

    numero_conta = len(contas) + 1
    
    if tipo_conta == "corrente":
        conta = ContaCorrente.nova_conta(cliente_encontrado, numero_conta, tipo_conta, senha, limite_conta)
    else:
        conta = ContaSalario.nova_conta(cliente_encontrado, numero_conta, tipo_conta, senha, limite_conta)

    cliente_encontrado.adicionar_conta(conta)
    contas.append(conta)
    salvar_sistema(clientes, contas)

    print(f"\n🎉 {nome_tipo} criada com sucesso!")
    print(f"📄 Agência: 0001 | Número da Conta: {numero_conta} | Limite por Saque: R$ {limite_conta:.2f}")
    return conta


def autenticar_usuario(clientes, contas):
    cpf_input = input("Informe o seu CPF para autenticação: ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    cpf_hash_tentativa = criar_hash(cpf_limpo)
    
    contas_do_usuario = [c for c in contas if c.cliente.cpf_hash == cpf_hash_tentativa]
    
    if not contas_do_usuario:
        print("\n❌ Acesso Negado: Nenhuma conta encontrada para este CPF.")
        return None
        
    senha_input = input("Informe a sua palavra-passe/PIN de 4 dígitos: ")
    senha_hash_tentativa = criar_hash(senha_input)
    
    contas_validas = [c for c in contas_do_usuario if c.senha_hash == senha_hash_tentativa]
    
    if not contas_validas:
        print("\n❌ Acesso Negado: Palavra-passe incorreta.")
        return None
        
    nome_titular = contas_validas[0].cliente.nome
            
    if len(contas_validas) == 1:
        conta_encontrada = contas_validas[0]
        tipo_nome = "Conta Salário" if conta_encontrada.tipo_conta == "salario" else "Conta Corrente"
        print(f"\n✨ Autenticação bem-sucedida! Bem-vindo(a), {nome_titular} ({tipo_nome} - C/C: {conta_encontrada.numero}).")
        return conta_encontrada
        
    print(f"\n✨ Olá, {nome_titular}! Encontramos mais do que uma conta associada ao seu CPF.")
    print("=" * 50)
    print("Selecione qual conta deseja aceder:")
    
    for idx, conta in enumerate(contas_validas, start=1):
        tipo_nome = "Conta Salário" if conta.tipo_conta == "salario" else "Conta Corrente"
        print(f"[{idx}]\t{tipo_nome} (Ag: {conta.agencia} | C/C: {conta.numero} | Saldo: R$ {conta.saldo:.2f})")
        
    print("=" * 50)
    
    while True:
        escolha = input("Digite o número da conta desejada: ").strip()
        if escolha.isdigit():
            indice = int(escolha) - 1
            if 0 <= indice < len(contas_validas):
                conta_escolhida = contas_validas[indice]
                tipo_nome = "Conta Salário" if conta_escolhida.tipo_conta == "salario" else "Conta Corrente"
                print(f"\n✅ Acedendo à {tipo_nome} (C/C: {conta_escolhida.numero})...")
                return conta_escolhida
        print("❌ Opção inválida. Digite um número correspondente à lista.")


def exibir_extrato(conta):
    tipo_nome = "Conta Salário" if conta.tipo_conta == "salario" else "Conta Corrente"
    print(f"\n================ EXTRATO ({tipo_nome}) ================")
    if not conta.historico.transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for t in conta.historico.transacoes:
            print(f"[{t['data_formatada']}] {t['tipo']}:\tR$ {t['valor']:.2f}")
    print(f"\nSaldo atual:\tR$ {conta.saldo:.2f}")
    print("======================================================")


def main():
    clientes, contas = carregar_sistema()

    while True:
        menu_inicial = """
        ================ ACESSO BANCÁRIO ================
        [1]\tAcessar à Conta
        [2]\tCadastrar Novo Utilizador
        [3]\tCriar Nova Conta (Corrente ou Salário)
        [q]\tSair do Sistema
        => """
        
        opcao = input(menu_inicial).strip().lower()

        if opcao == "1":
            conta_atual = autenticar_usuario(clientes, contas)
            
            if conta_atual:
                while True:
                    tipo_nome = "Salário" if conta_atual.tipo_conta == "salario" else "Corrente"
                    menu_operacoes = f"""
                    ================ MENU ({tipo_nome} - Ag: {conta_atual.agencia} | C/C: {conta_atual.numero}) ================
                    [d]\tDepositar
                    [s]\tSacar
                    [e]\tExtrato
                    [q]\tTerminar Sessão (Voltar ao Início)
                    => """
                    
                    op_conta = input(menu_operacoes).strip().lower()

                    if op_conta == "d":
                        valor = obter_valor_numerico("Informe o valor do depósito (R$): ")
                        transacao = Deposito(valor)
                        conta_atual.cliente.realizar_transacao(conta_atual, transacao)
                        salvar_sistema(clientes, contas)

                    elif op_conta == "s":
                        valor = obter_valor_numerico("Informe o valor do saque (R$): ")
                        transacao = Saque(valor)
                        conta_atual.cliente.realizar_transacao(conta_atual, transacao)
                        salvar_sistema(clientes, contas)

                    elif op_conta == "e":
                        exibir_extrato(conta_atual)

                    elif op_conta == "q":
                        print("\nSessão encerrada com segurança.")
                        break
                    else:
                        print("\n❌ Opção inválida, selecione novamente.")

        elif opcao == "2":
            criar_utilizador(clientes, contas)

        elif opcao == "3":
            criar_nova_conta(clientes, contas)

        elif opcao == "q":
            print("\nObrigado por utilizar o nosso banco. Até logo!")
            break
        else:
            print("\n❌ Opção inválida, selecione novamente.")

if __name__ == "__main__":
    main()