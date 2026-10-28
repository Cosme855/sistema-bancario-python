"""
Sistema Bancário em Python - Versão 0.3 para contas corrente e salário.
"""

import textwrap
import json
import os
import hashlib
from datetime import datetime

ARQUIVO_DADOS = "dados_banco.json"

def carregar_dados():
    """
    Carrega os dados dos utilizadores e contas a partir do ficheiro JSON,
    garantindo a persistência e atualizando contas antigas automaticamente (migração).
    """
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
                utilizadores = dados.get("utilizadores", [])
                contas = dados.get("contas", [])
                
                # Migração automática para garantir compatibilidade com versões anteriores
                
                for conta in contas:
                    if "historico_transacoes_datas" not in conta:
                        conta["historico_transacoes_datas"] = []
                    if "tipo_conta" not in conta:
                        conta["tipo_conta"] = "corrente"
                    if "limite" not in conta or conta["limite"] <= 0.0:
                        conta["limite"] = 5000.0 if conta.get("tipo_conta") == "corrente" else 2500.0
                        
                return utilizadores, contas
        except json.JSONDecodeError:
            print("\n⚠️ Aviso: Ficheiro de dados corrompido ou vazio. A iniciar com base limpa.")
            return [], []
    return [], []

def salvar_dados(utilizadores, contas):
    """
    Salva o estado atual das listas de utilizadores e contas no ficheiro JSON.
    """
    dados = {
        "utilizadores": utilizadores,
        "contas": contas
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

def criar_hash(texto):
    """
    Segurança Avançada (Hash): Converte dados sensíveis num código criptografado (SHA-256).
    """
    return hashlib.sha256(texto.encode()).hexdigest()

def formatar_e_mascarar_cpf(cpf):
    """
    Privacidade Visual: Formata o CPF e oculta os dígitos centrais na tela.
    """
    apenas_digitos = "".join([c for c in cpf if c.isdigit()])
    if len(apenas_digitos) == 11:
        return f"***.{apenas_digitos[3:6]}.{apenas_digitos[6:9]}-**"
    return "***.***.***-**"

def obter_valor_numerico(mensagem):
    """
    Garante que o programa não quebre se forem inseridas letras.
    """
    while True:
        try:
            valor = float(input(mensagem))
            return valor
        except ValueError:
            print("\n❌ Erro de formato: Por favor, informe apenas números válidos.")

def verificar_limite_transacoes(conta):
    """
    Verifica se a conta já atingiu o limite de 10 transações no dia atual.
    """
    hoje = datetime.now().strftime("%Y-%m-%d")
    transacoes_hoje = [t for t in conta.get("historico_transacoes_datas", []) if t.startswith(hoje)]
    
    if len(transacoes_hoje) >= 10:
        return True
    return False

def registar_transacao(conta, tipo, valor):
    """
    Regista a data, hora e tipo da transação para controlo diário e exibição no extrato.
    """
    agora = datetime.now()
    data_hora_str = agora.strftime("%d/%m/%Y %H:%M:%S")
    data_iso_str = agora.strftime("%Y-%m-%d %H:%M:%S")
    
    if "historico_transacoes_datas" not in conta:
        conta["historico_transacoes_datas"] = []
    conta["historico_transacoes_datas"].append(data_iso_str)
    
    conta["extrato"] += f"[{data_hora_str}] {tipo}:\tR$ {valor:.2f}\n"

def depositar(conta, valor, utilizadores, contas):
    """
    Realiza a operação de depósito validando o valor e o limite diário de transações.
    """
    if verificar_limite_transacoes(conta):
        print("\n❌ Operação falhou! Excedeu o número máximo de 10 transações permitidas para hoje.")
        return

    if valor > 0:
        conta["saldo"] += valor
        registar_transacao(conta, "Depósito", valor)
        salvar_dados(utilizadores, contas)
        print(f"\n✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
    else:
        print("\n❌ Operação falhou! O valor informado deve ser maior que zero.")

def sacar(*, conta, valor, limite, limite_saques, utilizadores, contas):
    """
    Realiza o saque aplicando regras financeiras, limite de saques e limite diário.
    """
    if verificar_limite_transacoes(conta):
        print("\n❌ Operação falhou! Excedeu o número máximo de 10 transações permitidas para hoje.")
        return

    excedeu_saldo = valor > conta["saldo"]
    excedeu_limite = valor > limite
    excedeu_saques = conta["numero_saques"] >= limite_saques

    if excedeu_saldo:
        print("\n❌ Operação falhou! Saldo insuficiente.")
    elif excedeu_limite:
        print(f"\n❌ Operação falhou! O valor excede o limite máximo por saque de R$ {limite:.2f}.")
    elif excedeu_saques:
        print("\n❌ Operação falhou! Número máximo de saques diários atingido.")
    elif valor > 0:
        conta["saldo"] -= valor
        conta["numero_saques"] += 1
        registar_transacao(conta, "Saque", valor)
        salvar_dados(utilizadores, contas)
        print(f"\n✅ Saque de R$ {valor:.2f} realizado com sucesso!")
    else:
        print("\n❌ Operação falhou! O valor informado é inválido.")

def exibir_extrato(conta):
    """
    Exibe o extrato detalhado com data, hora, tipo de conta e saldo atual.
    """
    tipo_nome = "Conta Salário" if conta.get("tipo_conta") == "salario" else "Conta Corrente"
    print(f"\n================ EXTRATO ({tipo_nome}) ================")
    print("Não foram realizadas movimentações." if not conta["extrato"] else conta["extrato"])
    print(f"\nSaldo atual:\tR$ {conta['saldo']:.2f}")
    print("======================================================")

def criar_utilizador(utilizadores, contas):
    """
    Cadastra apenas o perfil do utilizador (Cliente) com segurança Hash no CPF.
    """
    cpf_input = input("Informe o CPF do cliente (apenas números): ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    
    if len(cpf_limpo) != 11:
        print("\n❌ Segurança: CPF inválido! Deve conter exatamente 11 dígitos.")
        return None
    
    cpf_hash_novo = criar_hash(cpf_limpo)

    for u in utilizadores:
        if u["cpf_hash"] == cpf_hash_novo:
            print("\n❌ Operação negada: Já existe um utilizador registado com este CPF!")
            return u

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")

    print("\n--- Dados do Endereço ---")
    rua = input("Informe a rua: ")
    bairro = input("Informe o bairro: ")
    cidade_estado = input("Informe a cidade/sigla estado (ex: Rio de Janeiro/RJ): ")
    endereco = f"{rua} - {bairro} - {cidade_estado}"

    utilizador = {
        "nome": nome, 
        "data_nascimento": data_nascimento, 
        "cpf_hash": cpf_hash_novo,
        "endereco": endereco
    }
    utilizadores.append(utilizador)
    salvar_dados(utilizadores, contas)
    
    print(f"\n🎉 Utilizador cadastrado com sucesso!")
    print(f"🛡️ CPF Protegido (Hash): {formatar_e_mascarar_cpf(cpf_limpo)}")
    return utilizador

def criar_nova_conta(utilizadores, contas, agencia):
    """
    Cria uma nova conta (Corrente ou Salário) vinculada a um utilizador existente,
    definindo limites financeiros adequados para cada tipo.
    """
    if not utilizadores:
        print("\n❌ Nenhum utilizador cadastrado. Cadastre o utilizador primeiro (Opção 2).")
        return None

    cpf_input = input("Informe o CPF do titular para vincular a conta: ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    cpf_hash_busca = criar_hash(cpf_limpo)

    utilizador_encontrado = None
    for u in utilizadores:
        if u["cpf_hash"] == cpf_hash_busca:
            utilizador_encontrado = u
            break

    if not utilizador_encontrado:
        print("\n❌ Utilizador não encontrado! Por favor, cadastre o utilizador primeiro.")
        return None

    print("\n--- Selecione o Tipo de Conta ---")
    print("[1] Conta Corrente (Limite de saque: R$ 5000.00)")
    print("[2] Conta Salário (Limite de saque: R$ 2500.00)")
    tipo_opcao = input("Escolha o tipo (1 ou 2): ").strip()
    
    tipo_conta = "salario" if tipo_opcao == "2" else "corrente"
    nome_tipo = "Conta Salário" if tipo_conta == "salario" else "Conta Corrente"
    
    # 🛡️ Correção: Atribui limites válidos para evitar o bloqueio indevido
    limite_conta = 5000.0 if tipo_conta == "corrente" else 2500.0

    while True:
        senha = input("Crie uma palavra-passe/PIN numérico de 4 dígitos para esta conta: ")
        if senha.isdigit() and len(senha) == 4:
            break
        print("\n❌ A senha deve conter exatamente 4 números.")

    numero_conta = len(contas) + 1
    conta = {
        "agencia": agencia,
        "numero_conta": numero_conta,
        "tipo_conta": tipo_conta,
        "cpf_titular_hash": cpf_hash_busca,
        "senha_hash": criar_hash(senha),
        "saldo": 0.0,
        "limite": limite_conta, # Limite de saque por operação corrigido
        "extrato": "",
        "numero_saques": 0,
        "historico_transacoes_datas": []
    }
    contas.append(conta)
    salvar_dados(utilizadores, contas)

    print(f"\n🎉 {nome_tipo} criada com sucesso!")
    print(f"📄 Agência: {agencia} | Número da Conta: {numero_conta} | Limite por Saque: R$ {limite_conta:.2f}")
    return conta

def autenticar_usuario(contas, utilizadores):
    """
    Autenticação segura via hash de CPF e palavra-passe. 
    Se o cliente tiver múltiplas contas, exibe um menu para escolher qual deseja aceder.
    """
    cpf_input = input("Informe o seu CPF para autenticação: ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    cpf_hash_tentativa = criar_hash(cpf_limpo)
    
    contas_do_usuario = [c for c in contas if c["cpf_titular_hash"] == cpf_hash_tentativa]
    
    if not contas_do_usuario:
        print("\n❌ Acesso Negado: Nenhuma conta encontrada para este CPF.")
        return None
        
    senha_input = input("Informe a sua palavra-passe/PIN de 4 dígitos: ")
    senha_hash_tentativa = criar_hash(senha_input)
    
    contas_validas = [c for c in contas_do_usuario if c["senha_hash"] == senha_hash_tentativa]
    
    if not contas_validas:
        print("\n❌ Acesso Negado: Palavra-passe incorreta.")
        return None
        
    nome_titular = ""
    for u in utilizadores:
        if u["cpf_hash"] == cpf_hash_tentativa:
            nome_titular = u["nome"]
            break
            
    if len(contas_validas) == 1:
        conta_encontrada = contas_validas[0]
        tipo_nome = "Conta Salário" if conta_encontrada.get("tipo_conta") == "salario" else "Conta Corrente"
        print(f"\n✨ Autenticação bem-sucedida! Bem-vindo(a), {nome_titular} ({tipo_nome} - C/C: {conta_encontrada['numero_conta']}).")
        return conta_encontrada
        
    print(f"\n✨ Olá, {nome_titular}! Encontramos mais do que uma conta associada ao seu CPF[cite: 20].")
    print("=" * 50)
    print("Selecione qual conta deseja aceder:")
    
    for idx, conta in enumerate(contas_validas, start=1):
        tipo_nome = "Conta Salário" if conta.get("tipo_conta") == "salario" else "Conta Corrente"
        print(f"[{idx}]\t{tipo_nome} (Ag: {conta['agencia']} | C/C: {conta['numero_conta']} | Saldo: R$ {conta['saldo']:.2f})")
        
    print("=" * 50)
    
    while True:
        escolha = input("Digite o número da conta desejada: ").strip()
        if escolha.isdigit():
            indice = int(escolha) - 1
            if 0 <= indice < len(contas_validas):
                conta_escolhida = contas_validas[indice]
                tipo_nome = "Conta Salário" if conta_escolhida.get("tipo_conta") == "salario" else "Conta Corrente"
                print(f"\n✅ Acedendo à {tipo_nome} (C/C: {conta_escolhida['numero_conta']})...")
                return conta_escolhida
        print("❌ Opção inválida. Digite um número correspondente à lista.")

def main():
    LIMITE_SAQUES = 5
    AGENCIA = "0001"
    
    utilizadores, contas = carregar_dados()

    while True:
        menu_inicial = """
        ================ ACESSO BANCÁRIO  ================
        [1]\tAcessar à Conta
        [2]\tCadastrar Novo Utilizador 
        [3]\tCriar Nova Conta (Corrente ou Salário)
        [q]\tSair do Sistema
        => """
        
        opcao = input(menu_inicial).strip().lower()

        if opcao == "1":
            conta_atual = autenticar_usuario(contas, utilizadores)
            
            if conta_atual:
                while True:
                    tipo_nome = "Salário" if conta_atual.get("tipo_conta") == "salario" else "Corrente"
                    menu_operacoes = f"""
                    ================ MENU ({tipo_nome} - Ag: {conta_atual['agencia']} | C/C: {conta_atual['numero_conta']}) ================
                    [d]\tDepositar
                    [s]\tSacar
                    [e]\tExtrato
                    [q]\tTerminar Sessão (Voltar ao Início)
                    => """
                    
                    op_conta = input(menu_operacoes).strip().lower()

                    if op_conta == "d":
                        valor = obter_valor_numerico("Informe o valor do depósito (R$): ")
                        depositar(conta_atual, valor, utilizadores, contas)

                    elif op_conta == "s":
                        valor = obter_valor_numerico("Informe o valor do saque (R$): ")
                        sacar(
                            conta=conta_atual,
                            valor=valor,
                            limite=conta_atual["limite"],
                            limite_saques=LIMITE_SAQUES,
                            utilizadores=utilizadores,
                            contas=contas
                        )

                    elif op_conta == "e":
                        exibir_extrato(conta_atual)

                    elif op_conta == "q":
                        print("\nSessão encerrada com segurança.")
                        break
                    else:
                        print("\n❌ Opção inválida, selecione novamente.")

        elif opcao == "2":
            criar_utilizador(utilizadores, contas)

        elif opcao == "3":
            criar_nova_conta(utilizadores, contas, AGENCIA)

        elif opcao == "q":
            print("\nObrigado por utilizar o nosso sistema bancário. Até logo!")
            break
        else:
            print("\n❌ Opção inválida, selecione novamente.")

if __name__ == "__main__":
    main()