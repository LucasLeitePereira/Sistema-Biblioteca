import psycopg2
import os
from tabulate import tabulate

class erro(Exception):
    pass

def abrirBancoDeDados():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="Biblioteca",
            user="postgres",
            password="LucasBR20"
        )
        cur = conn.cursor()
        return conn, cur
    except psycopg2.Error as e:
        print(f"Não conseguiu abrir o banco de dados: {e}")
        return None, None

def cadastrarCliente(cur):
    os.system('cls')
    cur.execute("SELECT MAX(id_cliente) FROM cliente")
    maiorID = cur.fetchone()[0]
    
    idCliente = maiorID + 1
    nome = input("Nome: ")
    sql = "INSERT INTO cliente (id_cliente, nome_cliente) VALUES (%s, %s)"
    cur.execute(sql, (idCliente, nome))
    conn.commit()
    
def cadastrarLivro(cur):
    os.system('cls')
    cur.execute("SELECT MAX(id_livro) FROM livro")
    maiorID = cur.fetchone()[0]
    
    idLivro = maiorID + 1
    nomeLivro = input("Nome do livro: ")
    autor = input("Autor: ")
    status = "L"
    sql = "INSERT INTO livro (id_livro, nome_livro, autor, status) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (idLivro, nomeLivro, autor, status))
    conn.commit()
    
def imprimirLivros(cur):
    cur.execute("SELECT id_livro, nome_livro, status FROM livro ORDER BY nome_livro ASC")
    dados = cur.fetchall()
    
    cabecalho = ['ID', 'Nome', 'Status']
    print(tabulate(dados, headers=cabecalho, tablefmt='psql'))

def apagarCliente(cur, conn):
    nomeCliente = input("Qual o nome do cliente que deseja apagar: ")
    sql = "DELETE FROM cliente WHERE nome_cliente = %s"
    cur.execute(sql, (nomeCliente,))
    conn.commit()

def apagarLivro(cur, conn):
    nomeLivro = input("Qual o nome do livro que deseja apagar: ")
    sql = "DELETE FROM livro WHERE nome_livro = %s"
    cur.execute(sql, (nomeLivro,))
    conn.commit()
    
def alugarLivro(cur):
    while (True):
        try:
            nomeBusca = input("Nome do Cliente: ")
            sql = "SELECT id_cliente FROM cliente WHERE nome_cliente = %s"
            cur.execute(sql, (nomeBusca,))
            idCliente = cur.fetchone()[0]
            break
        except TypeError:
            os.system('cls')
            print("Cliente não encontrado")
    while (True):
        try:
            livroBusca = input("Nome do Livro: ")
            sql = "SELECT id_livro, status FROM livro WHERE nome_livro = %s AND status = %s"
            cur.execute(sql, (livroBusca, 'L'))
            dadosLivro = cur.fetchall()
            idLivro, statusLivro = dadosLivro[0]
            break
        except TypeError:
            os.system('cls')
            print("Livro não encontrado")
        except IndexError:
            os.system('cls')
            print("Livro não está disponivel para aluguel")
            
    sql = "UPDATE livro SET status = 'A' WHERE id_livro = %s"
    cur.execute(sql, (idLivro,))        
    conn.commit()
    
    sql = "INSERT INTO os (id_cliente, id_livro, data_aluguel, data_devolucao, status) VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + INTERVAL '7 days', 'Alugado')"
    cur.execute(sql, (idCliente, idLivro))        
    conn.commit()
    
def verificarLivrosAlugados(cur): 
    cur.execute("SELECT COUNT(*) FROM os WHERE status = 'Alugado'")
    numero = cur.fetchone()[0]
    
    if (numero > 0):
        cur.execute("SELECT cliente.nome_cliente, livro.nome_livro, os.data_devolucao FROM os INNER JOIN cliente ON os.id_cliente = cliente.id_cliente INNER JOIN livro ON livro.id_livro = os.id_livro WHERE os.status = 'Alugado' ORDER BY cliente.nome_cliente ASC")
        dados = cur.fetchall()
        
        cabecalho = ['Cliente', 'Livro', 'Data para devolução']
        print(tabulate(dados, headers=cabecalho, tablefmt='psql'))
    else:
        print("Não há livros a serem devolvidos")
    
def devolverLivro(cur):
    cur.execute("SELECT COUNT(*) FROM os WHERE status = 'Alugado'")
    numero = cur.fetchone()[0]
    
    if (numero > 0):
        cur.execute("SELECT os.id_aluguel, cliente.nome_cliente, livro.nome_livro, os.data_devolucao FROM os INNER JOIN cliente ON os.id_cliente = cliente.id_cliente INNER JOIN livro ON livro.id_livro = os.id_livro WHERE os.status = 'Alugado' ORDER BY cliente.nome_cliente ASC")
        dados = cur.fetchall()
        cabecalho = ['ID', 'Cliente', 'Livro', 'Data para devolução']
        print(tabulate(dados, headers=cabecalho, tablefmt='psql'))
        
        
        idOS = input("Qual o ID do Alguel: ")
        sql = "SELECT id_livro FROM os WHERE id_aluguel = %s"
        cur.execute(sql, (idOS,))
        idLivro = cur.fetchone()
        
        sql = "UPDATE os SET status = 'Devolvido' WHERE id_aluguel = %s"
        cur.execute(sql, (idOS,))
        conn.commit()
        
        sql = "UPDATE livro SET status = 'L' WHERE id_livro = %s"
        cur.execute(sql, (idLivro,))
        conn.commit()
    else:
        print("Nenhum alguel de livro encontrado")
    
def vizualizarTabelas(cur):
    print("Qual tabela você deseja vizualizar?")
    print("1. Clientes Cadastrados")
    print("2. Livros Cadastrados")
    print("3. Livros Alugados")
    opcao = int(input("Opção: "))
    
    if (opcao == 1):
        sql = "SELECT nome_cliente FROM cliente ORDER BY nome_cliente ASC"
        cur.execute(sql)
        dados = cur.fetchall()
        
        cabecalho = ["Nome"]
        print(tabulate(dados, headers=cabecalho, tablefmt='psql'))
    elif (opcao == 2):
        sql = "SELECT nome_livro, autor FROM livro ORDER BY nome_livro ASC"
        cur.execute(sql)
        dados = cur.fetchall()
        
        cabecalho = ["Nome", "Autor"]
        print(tabulate(dados, headers=cabecalho, tablefmt='psql'))
    elif (opcao == 3):
        sql = "SELECT cliente.nome_cliente, livro.nome_livro, os.data_devolucao, os.status FROM os INNER JOIN cliente ON os.id_cliente = cliente.id_cliente INNER JOIN livro ON os.id_livro = livro.id_livro"
        cur.execute(sql)
        dados = cur.fetchall()
        
        cabecalho = ["Cliente", "Livro", "Data de Devolução", "Status"]
        print(tabulate(dados, headers=cabecalho, tablefmt='psql'))
    else:
        print("Opção Invalida")

def menuCadastrar(cur):
    while (True):
        print("1. Cadastrar cliente")
        print("2. Cadastrar livro")
        print("3. Alugar livro")
        opcao = int(input("Opção: "))
        
        match opcao:
            case 1:
                cadastrarCliente(cur)
                break
            case 2:
                cadastrarLivro(cur)
                break
            case 3:
                alugarLivro(cur)
                break
            case 0:
                print("Voltando para o menu")
                break
            case _:
                print("Opção inválida")

def menuVizualizar(cur):
    while (True):
        print("== Vizualizar qual tabela ==")
        print("1. Clientes")
        print("2. Livros Cadastrados")
        print("3. Livros Alugados")
        opcao = int(input("Opção: "))
        os.system('cls')
        match opcao:
            case 1:
                cur.execute("SELECT nome_cliente FROM cliente ORDER BY nome_cliente ASC")
                dados = cur.fetchall()
                cabecalho = ["Nome"]
                print(tabulate(dados, headers=cabecalho, tablefmt='psql'))
                break
            case 2:
                imprimirLivros(cur)
                break
            case 3:
                verificarLivrosAlugados(cur)
                break
            case 0:
                print("Voltando para o menu")
                break
            case _:
                print("Opção inválida")
    
def menuDeletar(cur):
    while(True):
        os.system('cls')
        print("Apagar dado da tabela")
        print("1. Clientes")
        print("2. Livros")
        print("0. Voltar para o menu")
        opcao = int(input("Opção: "))
        
        match opcao:
            case 1:
                nomeBusca = input("Nome do cliente: ")
                sql = "DELETE FROM cliente WHERE nome_cliente = %s"
                cur.execute(sql, (nomeBusca,))
                conn.commit()
            case 2:
                livroBusca = input("Nome do livro: ")
                sql = "DELETE FROM livro WHERE nome_livro = %s"
                cur.execute(sql, (livroBusca,))
                conn.commit()
            case 0:
                print("Voltando para o menu")
                break
            case _:
                print("Opção inválida")
                
conn, cur = abrirBancoDeDados()

os.system('cls')

while (True):
    print("Escolha uma opção")
    print("1. Cadastrar")
    print("2. Deletar")
    print("3. Alugar livro")
    print("4. Devolver livro")
    print("5. Vizualizar tabelas")
    print("0. Encerrar o progrma")
    opcao = int(input("Opção: "))
    
    os.system('cls')
    match opcao:
        case 1:
            menuCadastrar(cur)
        case 2:
            menuDeletar(cur)
        case 3:
            alugarLivro(cur)
        case 4:
            devolverLivro(cur)
        case 5:
            menuVizualizar(cur)
        case 0:
            break
        case _:
            print("Opção Invalida")
    

    
cur.close()
conn.close()
