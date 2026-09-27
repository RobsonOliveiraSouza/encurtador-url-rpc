from xmlrpc.server import SimpleXMLRPCServer
import random
import string
import sqlite3
import sys

ARQUIVO_BANCO = "dados.db"
PREFIXO_URL = "sddin.uem/"


# Config do banco
def conectar_banco():
    return sqlite3.connect(
        ARQUIVO_BANCO,
        timeout=10
    )

def inicializar_banco():

    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                codigo TEXT PRIMARY KEY,
                url_original TEXT UNIQUE NOT NULL
            )
        """)


# Geração de código aleatório
def gerar_codigo():
    """
    Gera exatamente 8 caracteres, os primeiros 7 podem ser letras ou números mas o último deve ser um dígito.

    """
    caracteres = string.ascii_letters + string.digits

    primeiros_sete = "".join(
        random.choice(caracteres)
        for _ in range(7)
    )

    ultimo = random.choice(string.digits)

    return primeiros_sete + ultimo


# Operações RPC

def encurtar(url, endereco_cliente="desconhecido"):
    print("=" * 50)
    print("[SERVIDOR] Requisição recebida")
    print(f"[SERVIDOR] Cliente: {endereco_cliente}")
    print(f"[SERVIDOR] Operação: encurtar")
    print(f"[SERVIDOR] URL: {url}")

    with conectar_banco() as conexao:

        # Verifica se a URL já existe
        cursor = conexao.execute(
            "SELECT codigo FROM urls WHERE url_original = ?",
            (url,)
        )

        resultado = cursor.fetchone()

        if resultado:
            codigo = resultado[0]

            return {
                "sucesso": True,
                "mensagem": "A URL já foi encurtada anteriormente.",
                "url_original": url,
                "url_encurtada": f"{PREFIXO_URL}{codigo}"
            }

        # Tenta gerar um código ainda não utilizado
        while True:

            codigo = gerar_codigo()

            try:
                conexao.execute(
                    """
                    INSERT INTO urls (codigo, url_original)
                    VALUES (?, ?)
                    """,
                    (codigo, url)
                )

                conexao.commit()
                break

            except sqlite3.IntegrityError:

                # Pode ter ocorrido colisão do código, se outra instância cadastrou a mesma URL simultaneamente, recuperamos o cadastro.
                cursor = conexao.execute(
                    "SELECT codigo FROM urls WHERE url_original = ?",
                    (url,)
                )

                resultado = cursor.fetchone()

                if resultado:
                    codigo = resultado[0]
                    break

                # Caso contrário, houve colisão do código aleatório e tentamos outro.
                continue

    return {
        "sucesso": True,
        "mensagem": "URL encurtada com sucesso.",
        "url_original": url,
        "url_encurtada": f"{PREFIXO_URL}{codigo}"
    }


def resolver(url, endereco_cliente="desconhecido"):
    print("=" * 50)
    print("[SERVIDOR] Requisição recebida")
    print(f"[SERVIDOR] Cliente: {endereco_cliente}")
    print(f"[SERVIDOR] Operação: resolver")
    print(f"[SERVIDOR] URL: {url}")

    if url.startswith(PREFIXO_URL):
        codigo = url[len(PREFIXO_URL):]
    else:
        codigo = url

    with conectar_banco() as conexao:

        cursor = conexao.execute(
            """
            SELECT url_original
            FROM urls
            WHERE codigo = ?
            """,
            (codigo,)
        )

        resultado = cursor.fetchone()

    if resultado:

        return {
            "sucesso": True,
            "mensagem": "URL encontrada.",
            "url_encurtada": f"{PREFIXO_URL}{codigo}",
            "url_original": resultado[0]
        }

    return {
        "sucesso": False,
        "mensagem": "URL encurtada não encontrada.",
        "url_encurtada": url,
        "url_original": ""
    }


# Servidor RPC
def iniciar_servidor(porta):

    inicializar_banco()

    servidor = SimpleXMLRPCServer(
        ("0.0.0.0", porta),
        allow_none=True
    )

    servidor.register_function(encurtar, "encurtar")
    servidor.register_function(resolver, "resolver")

    print("=" * 50)
    print("SERVIDOR RPC - Encurtador de URLs")
    print(f"Porta: {porta}")
    print(f"Banco de dados: {ARQUIVO_BANCO}")
    print("=" * 50)
    print("Aguardando requisições...")

    servidor.serve_forever()


# Execução
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Uso: python servidor.py <porta>")
        print("Exemplo: python servidor.py 8001")
        sys.exit(1)

    try:
        porta = int(sys.argv[1])

    except ValueError:
        print("Erro: a porta deve ser um número inteiro.")
        sys.exit(1)

    iniciar_servidor(porta)