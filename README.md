# Seu Aconchego — Sistema de Reservas

## Como colocar no ar (gratuito)

### Passo 1 — Crie uma conta no GitHub
1. Acesse https://github.com e clique em **Sign up**
2. Crie sua conta (gratuito)

### Passo 2 — Suba os arquivos
1. Clique em **New repository**
2. Nome: `seu-aconchego`
3. Clique em **Create repository**
4. Clique em **uploading an existing file**
5. Arraste todos os arquivos desta pasta (incluindo a pasta `templates/`)
6. Clique em **Commit changes**

### Passo 3 — Deploy no Render
1. Acesse https://render.com e clique em **Get Started for Free**
2. Faça login com sua conta do GitHub
3. Clique em **New +** → **Web Service**
4. Selecione o repositório `seu-aconchego`
5. Render vai detectar o `render.yaml` automaticamente
6. Clique em **Create Web Service**
7. Aguarde ~2 minutos

### Passo 4 — Acesse no celular
- Render vai gerar um link tipo: `https://seu-aconchego.onrender.com`
- Abra no Chrome ou Safari do celular
- Toque em **"Adicionar à tela inicial"** para instalar como app!

---

## Observação importante
O plano gratuito do Render "dorme" após 15 min de inatividade.
Na primeira vez que abrir, pode demorar ~30 segundos para carregar.
Para uso contínuo, considere o plano pago ($7/mês).

---

## Estrutura dos arquivos
```
seu_aconchego/
├── app.py              # Backend Flask
├── templates/
│   ├── index.html      # Tela principal
│   └── editar.html     # Tela de edição
├── requirements.txt    # Dependências Python
└── render.yaml         # Config do deploy
```

##  Funcionalidades
-  Cadastro de reservas
-  Edição e exclusão
-  Controle de status (Pago / Pendente / Inadimplente / Cancelado)
-  Filtros por status
-  Painel com contagem de reservas
-  Interface responsiva para celular
-  Banco de dados SQLite (persistente no Render)
