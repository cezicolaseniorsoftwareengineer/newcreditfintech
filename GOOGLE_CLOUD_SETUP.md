# Configuração do Google OAuth 2.0 para o Render

O erro `redirect_uri_mismatch` ocorre porque o Google não reconhece o endereço do seu site no Render como seguro/autorizado. Você precisa adicionar a URL exata do Render no Console do Google Cloud.

## Passo a Passo

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
2. Selecione o projeto que contém as credenciais usadas no `app/core/config.py`.
3. Em **"Credenciais"**, clique no nome do seu **"ID do cliente OAuth 2.0"**.
4. Procure a seção **"URIs de redirecionamento autorizados"**.
5. Clique em **"Adicionar URI"** e cole EXATAMENTE este endereço:

   ```
   https://newcreditfintech.onrender.com/auth/google/callback
   ```

6. Clique em **Salvar**.

> **Nota:** Pode levar de 5 minutos a algumas horas para o Google propagar essa alteração.

## Se você não tem acesso a essas credenciais

Se as credenciais atuais (`1091893544918-...`) pertencem a outra pessoa ou curso e você não pode editá-las:

1. Crie um novo projeto no Google Cloud Console.
2. Crie novas credenciais OAuth (ID do Cliente e Chave Secreta).
3. Adicione a URL acima nos redirecionamentos autorizados.
4. No painel do **Render**, vá em **Environment** e adicione as variáveis:
   - `GOOGLE_CLIENT_ID`: (seu novo ID)
   - `GOOGLE_CLIENT_SECRET`: (sua nova senha)

O código já está pronto para ler essas variáveis automaticamente.
