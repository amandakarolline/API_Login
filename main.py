from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import CONN, Pessoa, Tokens
from secrets import token_hex
import hashlib

app = FastAPI()


def conecta_banco():
    engine = create_engine(CONN, echo=True)
    Session = sessionmaker(bind=engine)
    return Session()


@app.post('/cadastro')
def cadastro(nome: str, user: str, senha: str):
    session = conecta_banco()
    situacao_senha = valida_senha(senha)
    if situacao_senha == senha:
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        usuario = session.query(Pessoa).filter_by(usuario=user, senha=senha_hash).all()
        if len(usuario) == 0:
            x = Pessoa(nome=nome, usuario=user, senha=senha_hash)
            session.add(x)
            session.commit()
            return {'status': 'sucesso'}
        if len(usuario) > 0:
            return {'status': 'Usuário já cadastrado'}
    return {'status': {situacao_senha}}


@app.post('/login')
def login(usuario: str, senha: str):
    session = conecta_banco()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    user = session.query(Pessoa).filter_by(usuario=usuario, senha=senha_hash).all()
    if len(user) == 0:
        return {'status': 'Usuário inexistente'}

    while True:
        token = token_hex(50)  # valor dobrado por estar em hexadecimal
        tokenExiste = session.query(Tokens).filter_by(token=token).all()
        if len(tokenExiste) == 0:
            pessoaExiste = session.query(Tokens).filter_by(id_pessoa=user[0].id).all()
            if len(pessoaExiste) == 0:
                novoToken = Tokens(id_pessoa=user[0].id, token=token)
                session.add(novoToken)
            elif len(pessoaExiste) > 0:
                pessoaExiste[0].token = token

            session.commit()
            break
    return token


def valida_senha(senha):
    erro_senha = ('A senha deve conter: '
                  '8 caracteres, '
                  '1 letra maiúscula, '
                  '1 minúscula, '
                  'Números e '
                  'Caracter Especial')

    if senha.islower():
        return erro_senha
    if len(senha) < 8:
        return erro_senha
    if senha.isalpha():
        return erro_senha
    if senha.isalnum():
        return erro_senha
    return senha
