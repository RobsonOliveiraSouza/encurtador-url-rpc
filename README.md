# Encurtador de URLs com RPC

Trabalho prático da disciplina de **Sistemas Distribuídos** do curso de
Engenharia de Software da Universidade Estadual de Maringá (UEM).

O projeto implementa um serviço distribuído de encurtamento de URLs
utilizando **RPC**, balanceamento de carga **Round-Robin ponderado**,
persistência com **SQLite** e **ngrok** para acesso externo ao
balanceador.

## Arquitetura

O sistema é composto por:

- um cliente RPC
- um balanceador de carga
- três instâncias do servidor RPC
- um banco de dados SQLite compartilhado entre os servidores
- ngrok para disponibilizar externamente o balanceador

O cliente conhece apenas o endereço público disponibilizado pelo ngrok,
já o balanceador recebe as requisições e as distribui entre as três
instâncias dos servidores.

A distribuição utiliza Round-Robin ponderado com os seguintes pesos:

| Servidor   | Porta | Peso |
| ---------- | ----: | ---: |
| Servidor 1 |  8001 |    1 |
| Servidor 2 |  8002 |    1 |
| Servidor 3 |  8003 |    2 |

Dessa forma, a sequência utilizada é:

```text
S1 -> S2 -> S3 -> S3 -> S1 -> S2 -> S3 -> S3 -> ...
```

O balanceador foi implementado no próprio projeto por meio de testes, e
o ngrok é utilizado somente como mecanismo de acesso externo ao
balanceador.

## Operações

### Encurtar URL

A operação `encurtar` recebe uma URL original e retorna uma URL
encurtada no formato:

```text
sddin.uem/XXXXXXXX
```

O identificador possui exatamente **8 caracteres alfanuméricos**, sendo
o último caractere obrigatoriamente um dígito.

Antes de criar um novo identificador, o servidor verifica se a URL
original já foi encurtada. Caso já exista, a URL encurtada anteriormente
é retornada.

### Resolver URL

A operação `resolver` recebe uma URL encurtada, consulta a persistência
e retorna a URL original correspondente.

Caso o identificador não exista, o serviço informa que a URL encurtada
não foi encontrada.

## Persistência

A persistência é realizada utilizando **SQLite**.

As três instâncias dos servidores utilizam o mesmo arquivo `dados.db`.
Dessa forma, uma URL cadastrada por uma instância pode ser consultada
posteriormente por outra.

A estrutura do banco de dados é criada automaticamente quando um
servidor é iniciado.

O arquivo `dados.db` não precisa ser incluído no repositório, pois é
gerado durante a execução.

## Registro das requisições

Os servidores registram no terminal informações sobre as requisições
recebidas, incluindo:

- operação executada;
- URL recebida;
- endereço do cliente.

Quando o acesso ocorre por meio do ngrok, o balanceador preserva a
informação de origem recebida e a encaminha ao servidor responsável pela
requisição.

## Requisitos

O projeto foi desenvolvido e testado com:

- **Python 3.13.7**
- **ngrok (login por token)**

Não são necessárias bibliotecas Python externas para a aplicação. Os
módulos utilizados pertencem à biblioteca padrão do Python, incluindo
`xmlrpc`, `sqlite3`, `random`, `string` e `threading`.

## Execução

### 1. Iniciar os servidores RPC

Abra três terminais no diretório do projeto.

No primeiro:

```bash
python servidor.py 8001
```

No segundo:

```bash
python servidor.py 8002
```

No terceiro:

```bash
python servidor.py 8003
```

As três instâncias compartilham o mesmo banco SQLite.

### 2. Iniciar o balanceador

Em outro terminal, execute:

```bash
python balanceador.py 8000
```

O balanceador ficará responsável por receber as chamadas RPC e
distribuí-las entre os servidores.

### 3. Configurar o ngrok

O ngrok deve estar instalado e autenticado.

Para adicionar o token da conta:

```bash
ngrok config add-authtoken SEU_AUTHTOKEN
```

> Não compartilhamos nem adicionamos o authtoken do ngrok ao
> repositório.

Com o balanceador executando na porta `8000`, disponibilize essa porta
por meio do ngrok:

```bash
ngrok http 8000
```

O ngrok fornecerá um endereço público semelhante a:

```text
https://exemplo.ngrok-free.dev
```

Somente o balanceador deve ser disponibilizado pelo ngrok. Os servidores
das portas `8001`, `8002` e `8003` permanecem locais.

### 4. Executar o cliente

O endereço público fornecido pelo ngrok deve ser informado ao
`cliente.py` como argumento na linha de comando. Dessa forma, não é
necessário alterar o código-fonte sempre que o endereço do ngrok mudar.

Execute:

```bash
python cliente.py https://exemplo.ngrok-free.dev
```

O cliente não precisa conhecer os endereços individuais dos três
servidores, apenas o endereço público que encaminha as requisições ao
balanceador.

Caso o cliente seja executado sem o endereço do balanceador, será
exibida a forma correta de utilização:

```text
Uso:
python cliente.py <endereco_balanceador>

Exemplo:
python cliente.py https://exemplo.ngrok-free.dev
```

O menu disponibiliza:

```text
1 - Encurtar URL
2 - Resolver URL
3 - Sair
```

O cliente pode ser executado em outro dispositivo, desde que consiga
acessar o endereço público disponibilizado pelo ngrok.

## Estrutura do projeto

```text
encurtador-url-rpc/
|-- .gitignore
|-- README.md
|-- balanceador.py
|-- cliente.py
|-- servidor.py
`-- dados.db        # gerado na execução e não versionado
```

## .gitignore

O banco gerado e os arquivos temporários do Python são mantidos fora do
versionamento:

```gitignore
__pycache__/
*.py[cod]
dados.db
```

## Autor

**Gabriel Sossai Soares**  
**Robson Oliveira de Souza**  
**Vitor Fernando Regis**

Engenharia de Software  
Universidade Estadual de Maringá
