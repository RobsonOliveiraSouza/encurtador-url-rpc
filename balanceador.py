from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy
import threading
import sys

SERVIDORES = [
    {"nome": "Servidor 1", "endereco": "http://localhost:8001"},
    {"nome": "Servidor 2", "endereco": "http://localhost:8002"},
    {"nome": "Servidor 3", "endereco": "http://localhost:8003"},
    {"nome": "Servidor 3", "endereco": "http://localhost:8003"}
]

indice_atual = 0

contexto_requisicao = threading.local()


class RequestHandler(SimpleXMLRPCRequestHandler):

    rpc_paths = ("/RPC2",)

    def do_POST(self):

        endereco_cliente = self.client_address[0]

        # caso exista informação de encaminhamento utilizamos o primeiro endereço informado
        forwarded_for = self.headers.get("X-Forwarded-For")

        if forwarded_for:
            endereco_cliente = forwarded_for.split(",")[0].strip()

        contexto_requisicao.endereco_cliente = endereco_cliente

        try:
            super().do_POST()

        finally:
            contexto_requisicao.endereco_cliente = None


# round-robin ponderado S1=1, S2=1 e S3=2 seguindo a intrução da especificacão
def selecionar_servidor():

    global indice_atual

    servidor = SERVIDORES[indice_atual]

    indice_atual = (indice_atual + 1) % len(SERVIDORES)

    return servidor

def encaminhar(operacao, argumento):

    servidor_destino = selecionar_servidor()

    nome = servidor_destino["nome"]
    endereco = servidor_destino["endereco"]

    endereco_cliente = getattr(
        contexto_requisicao,
        "endereco_cliente",
        "desconhecido"
    )

    print("=" * 50)
    print("[BALANCEADOR] Requisição recebida")
    print(f"[BALANCEADOR] Cliente: {endereco_cliente}")
    print(f"[BALANCEADOR] Operação: {operacao}")
    print(f"[BALANCEADOR] Encaminhando para: {nome}")
    print(f"[BALANCEADOR] Destino: {endereco}")

    try:

        servidor_rpc = ServerProxy(
            endereco,
            allow_none=True
        )

        metodo_remoto = getattr(
            servidor_rpc,
            operacao
        )

        resposta = metodo_remoto(
            argumento,
            endereco_cliente
        )

        print(
            f"[BALANCEADOR] Resposta recebida de {nome}"
        )

        return resposta

    except Exception as erro:

        print(
            f"[BALANCEADOR] Erro ao acessar {nome}: {erro}"
        )

        return {
            "sucesso": False,
            "mensagem": f"Erro ao acessar {nome}.",
            "url_original": "",
            "url_encurtada": ""
        }

def encurtar(url):
    return encaminhar("encurtar", url)


def resolver(url):
    return encaminhar("resolver", url)


def iniciar_balanceador(porta):

    balanceador = SimpleXMLRPCServer(
        ("0.0.0.0", porta),
        requestHandler=RequestHandler,
        allow_none=True
    )

    balanceador.register_function(
        encurtar,
        "encurtar"
    )

    balanceador.register_function(
        resolver,
        "resolver"
    )

    print("=" * 50)
    print("BALANCEADOR DE CARGA RPC")
    print(f"Porta: {porta}")
    print("Estratégia: Round-Robin ponderado")
    print("Pesos: S1=1 | S2=1 | S3=2")
    print("=" * 50)
    print("Aguardando requisições...")

    balanceador.serve_forever()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso: python balanceador.py <porta>")
        print("Exemplo: python balanceador.py 8000")
        sys.exit(1)

    try:
        porta = int(sys.argv[1])

    except ValueError:
        print(
            "Erro: a porta deve ser um número inteiro."
        )
        sys.exit(1)

    iniciar_balanceador(porta)