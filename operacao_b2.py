"""
Sistema Bancário em Python 
"""

import textwrap
import json
import os
import hashlib

ARQUIVO_DADOS = "dados_banco.json"

def carregar_dados():
    """
    Carrega os dados dos utilizadores e contas a partir do ficheiro JSON,
    garantindo a persistência segura das informações.
    """
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
                return dados.get("utilizadores", []), dados.get("contas", [])
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
    Segurança Avançada (Hash): Converte qualquer dado sensível (CPF ou Senha) 
    num código criptografado irreversível (SHA-256).
    """
    return hashlib.sha256(texto.encode()).hexdigest()

def formatar_e_mascarar_cpf(cpf):
    """
    Privacidade Visual: Formata o CPF no padrão xxx.xxx.xxx-xx e oculta os dígitos centrais na tela.
    """
    apenas_digitos = "".join([c for c in cpf if c.isdigit()])
    if len(apenas_digitos) == 11:
        return f"***.{apenas_digitos[3:6]}.{apenas_digitos[6:9]}-**"
    return "***.***.***-**"

def obter_valor_numerico(mensagem):
    """
    Robustez: Garante que o programa não quebre se forem inseridas letras em vez de números.
    """
    while True:
        try:
            valor = float(input(mensagem))
            return valor
        except ValueError:
            print("\n❌ Erro de formato: Por favor, informe apenas números válidos.")

def depositar(conta, valor, utilizadores, contas):
    """
    Realiza a operação de depósito com validação de valor positivo.
    """
    if valor > 0:
        conta["saldo"] += valor
        conta["extrato"] += f"Depósito:\tR$ {valor:.2f}\n"
        salvar_dados(utilizadores, contas)
        print(f"\n✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
    else:
        print("\n❌ Operação falhou! O valor informado deve ser maior que zero.")

def sacar(*, conta, valor, limite, limite_saques, utilizadores, contas):
    """
    Realiza a operação de saque aplicando regras de segurança financeira.
    """
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
        conta["extrato"] += f"Saque:\t\tR$ {valor:.2f}\n"
        conta["numero_saques"] += 1
        salvar_dados(utilizadores, contas)
        print(f"\n✅ Saque de R$ {valor:.2f} realizado com sucesso!")
    else:
        print("\n❌ Operação falhou! O valor informado é inválido.")

def exibir_extrato(conta):
    """
    Exibe o extrato detalhado de transações da conta autenticada.
    """
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not conta["extrato"] else conta["extrato"])
    print(f"\nSaldo atual:\tR$ {conta['saldo']:.2f}")
    print("==========================================")

def criar_utilizador_e_conta(utilizadores, contas, agencia):
    """
    Cadastra um novo utilizador validando o CPF, evitando duplicados por hash,
    recolhendo morada e criando credenciais totalmente criptografadas.
    """
    cpf_input = input("Informe o CPF (apenas números ou com pontuação): ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    
    if len(cpf_limpo) != 11:
        print("\n❌ Segurança: CPF inválido! Deve conter exatamente 11 dígitos.")
        return None
    
    # Gera o hash do CPF para verificação segura
    cpf_hash_novo = criar_hash(cpf_limpo)

    # Verifica se já existe um utilizador registado com este CPF
    for u in utilizadores:
        if u["cpf_hash"] == cpf_hash_novo:
            print("\n❌ Operação negada: Já existe um utilizador registado com este CPF!")
            return None

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    
    while True:
        senha = input("Crie uma palavra-passe/PIN numérico de 4 dígitos para a sua conta: ")
        if senha.isdigit() and len(senha) == 4:
            break
        print("\n❌ A senha deve conter exatamente 4 números.")

    print("\n--- Dados do Endereço ---")
    rua = input("Informe a rua: ")
    bairro = input("Informe o bairro: ")
    cidade_estado = input("Informe a cidade/sigla estado (ex: Rio de Janeiro/RJ): ")
    
    endereco = f"{rua} - {bairro} - {cidade_estado}"

    utilizador = {
        "nome": nome, 
        "data_nascimento": data_nascimento, 
        "cpf_hash": cpf_hash_novo, # O CPF fica guardado exclusivamente em formato Hash
        "endereco": endereco
    }
    utilizadores.append(utilizador)

    numero_conta = len(contas) + 1
    conta = {
        "agencia": agencia,
        "numero_conta": numero_conta,
        "cpf_titular_hash": cpf_hash_novo, # Relacionamento da conta feito via Hash do CPF
        "senha_hash": criar_hash(senha),
        "saldo": 0.0,
        "limite": 3000.0,
        "extrato": "",
        "numero_saques": 0
    }
    contas.append(conta)
    
    salvar_dados(utilizadores, contas)
    
    print(f"\n🎉 Conta e Utilizador Criados com Segurança Máxima!")
    print(f"📄 Agência: {agencia} | Conta Corrente: {numero_conta}")
    print(f"🛡️ CPF Registrado (Protegido na Ecrã): {formatar_e_mascarar_cpf(cpf_limpo)}")
    print(f"🔒 Tanto o CPF quanto a palavra-passe foram criptografados no disco.")
    print(f"🏠 Endereço: {endereco}")
    return conta

def autenticar_usuario(contas, utilizadores):
    """
    Autenticação Ultra-Segura: Converte o CPF e a senha informados em hash
    e valida a correspondência exata no sistema.
    """
    cpf_input = input("Informe o seu CPF para autenticação: ")
    cpf_limpo = "".join([c for c in cpf_input if c.isdigit()])
    cpf_hash_tentativa = criar_hash(cpf_limpo)
    
    conta_encontrada = None
    for conta in contas:
        if conta["cpf_titular_hash"] == cpf_hash_tentativa:
            conta_encontrada = conta
            break
                
    if conta_encontrada:
        senha_input = input("Informe a sua palavra-passe/PIN de 4 dígitos: ")
        senha_hash_tentativa = criar_hash(senha_input)
        
        if senha_hash_tentativa == conta_encontrada["senha_hash"]:
            nome_titular = ""
            for u in utilizadores:
                if u["cpf_hash"] == cpf_hash_tentativa:
                    nome_titular = u["nome"]
                    break
                        
            print(f"\n✨ Autenticação bem-sucedida! Bem-vindo(a) de volta, {nome_titular}.")
            return conta_encontrada
        else:
            print("\n❌ Acesso Negado: Palavra-passe incorreta.")
            return None
    else:
        print("\n❌ Acesso Negado: CPF não encontrado.")
        return None

def main():
    """
    Função principal que gere o ciclo de vida da aplicação com menus blindados.
    """
    LIMITE_SAQUES = 4
    AGENCIA = "0001"
    
    utilizadores, contas = carregar_dados()

    while True:
        menu_inicial = """
        ================ ACESSO BANCÁRIO  ================
        [1]\tAutenticar com CPF e Senha (Login)
        [2]\tCriar Nova Conta / Utilizador Blindado
        [q]\tSair do Sistema
        => """
        
        opcao = input(menu_inicial).strip().lower()

        if opcao == "1":
            conta_atual = autenticar_usuario(contas, utilizadores)
            
            if conta_atual:
                while True:
                    menu_operacoes = f"""
                    ================ MENU DA CONTA (Ag: {conta_atual['agencia']} | C/C: {conta_atual['numero_conta']}) ================
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
            criar_utilizador_e_conta(utilizadores, contas, AGENCIA)

        elif opcao == "q":
            print("\nObrigado por utilizar o nosso banco. Até logo!")
            break
        else:
            print("\n❌ Opção inválida, selecione novamente.")

if __name__ == "__main__":
    main()