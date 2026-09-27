from xmlrpc.client import ServerProxy, Fault, ProtocolError
import sys


# Operações do cliente
def encurtar_url(balanceador):
    print("\n--- ENCURTAR URL ---")

    url = input("Digite a URL original: ").strip()

    if not url:
        print("Erro: a URL não pode ser vazia.")
        return

    resposta = balanceador.encurtar(url)

    print()
    print(resposta["mensagem"])

    if resposta["sucesso"]:
        print(f"URL original : {resposta['url_original']}")
        print(f"URL encurtada: {resposta['url_encurtada']}")


def resolver_url(balanceador):
    print("\n--- RESOLVER URL ---")

    url = input("Digite a URL encurtada: ").strip()

    if not url:
        print("Erro: a URL não pode ser vazia.")
        return

    resposta = balanceador.resolver(url)

    print()
    print(resposta["mensagem"])

    if resposta["sucesso"]:
        print(f"URL encurtada: {resposta['url_encurtada']}")
        print(f"URL original : {resposta['url_original']}")


# Interface
def executar(endereco_balanceador):

    balanceador = ServerProxy(
        endereco_balanceador,
        allow_none=True
    )

    print("=" * 50)
    print("ENCURTADOR DE URLs - SISTEMA DISTRIBUÍDO")
    print("=" * 50)

    while True:

        print("\n1 - Encurtar URL")
        print("2 - Resolver URL")
        print("3 - Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        try:

            if opcao == "1":
                encurtar_url(balanceador)

            elif opcao == "2":
                resolver_url(balanceador)

            elif opcao == "3":
                print("\nEncerrando cliente...")
                break

            else:
                print("\nOpção inválida.")

        except (ConnectionRefusedError, Fault, ProtocolError, OSError) as erro:
            print("\nErro de comunicação com o serviço.")
            print(f"Detalhes: {erro}")


# Execução
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso:")
        print("python cliente.py <endereco_balanceador>")
        print()
        print("Exemplo:")
        print("python cliente.py https://exemplo.ngrok-free.dev")
        sys.exit(1)

    endereco_balanceador = sys.argv[1]

    executar(endereco_balanceador)