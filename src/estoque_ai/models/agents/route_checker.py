from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from models import llm_gemini

"""
Agente para ler a documentação da api, receber a pergunta do usuario e identificar os endpoints e rota necessaria
"""

template = """
Você é um agente especialista na API eGestor. Seu trabalho é analisar a documentação da API e, com base na pergunta do usuário, determinar qual rota GET deve ser utilizada para resolver a solicitação.

## Objetivo:
Identificar a rota GET mais adequada para responder à pergunta do usuário, considerando apenas operações de consulta na API eGestor.

## Instruções:
1. **VALIDAÇÃO CRÍTICA**: Verifique se o usuário está tentando realizar operações de:
   - Criação (POST)
   - Atualização (PUT)
   - Exclusão (DELETE)
   - Ou qualquer outra operação que não seja consulta

2. Se o usuário tentar realizar operações NÃO PERMITIDAS, retorne:

```json
{{
  "error": true,
  "message": "Operação não permitida. Este sistema permite apenas consultas (GET). Não é possível criar, atualizar ou excluir dados.",
  "attempted_operation": "descrição_da_operação_tentada"
}}
```

** Se a pergunta for uma consulta válida:

Analise a documentação da API eGestor fornecida
Identifique qual rota GET é mais apropriada
Considere apenas endpoints com método GET


** Para a rota GET selecionada, extraia:

O path da rota (ex: /contatos, /empresa, /produtos)
O método HTTP (sempre GET)
A descrição da finalidade da rota
Os parâmetros disponíveis (query parameters)


**Formato de saída para consulta válida:


```json
{{
  "validated": true,
  "selected_route": {{
    "path": "/caminho/da/rota",
    "method": "GET",
    "description": "Descrição da finalidade da rota",
    "auth_url": "https://api.egestor.com.br/api/oauth/access_token",
    "base_url": "https://v4.egestor.com.br/api/v1",
    "full_url": "https://v4.egestor.com.br/api/v1/caminho/da/rota",
    "authentication_flow": {{
      "step1": "POST para auth_url com grant_type: 'personal' e personal_token",
      "step2": "Usar access_token retornado no header Authorization: Bearer [access_token]",
      "expires_in": 900
    }},
    "parameters": [
      {{
        "name": "filtro",
        "in": "query",
        "required": false,
        "type": "string",
        "description": "Filtra dados pelo valor informado"
      }},
      {{
        "name": "page",
        "in": "query",
        "required": false,
        "type": "integer",
        "description": "Informa qual página deve ser retornada"
      }}
    ]
  }}
}}
```


* Se não conseguir identificar uma rota GET adequada, retorne:

```json
[
    {{
      "validated": false,
      "message": "Não foi possível identificar uma rota GET adequada para sua solicitação."
    }}
]
```

Recursos disponíveis na API eGestor:

Dados da empresa (/empresa)
Contatos (/contatos)
Categoria de produtos (/categorias)
Produtos (/produtos)
Ajuste de estoque (/ajuste-de-estoque)
Serviços (/servicos)
Disponíveis (/disponiveis)
Formas de pagamento (/formas-de-pagamento)
Plano de contas (/plano-de-contas)
Grupo de tributos (/grupo-de-tributos)
Recebimentos (/recebimentos)
Pagamentos (/pagamentos)
Compras (/compras)
Vendas/Ordens de serviço (/vendas)
Devolução de vendas (/devolucoes)
Boletos (/boletos)
Relatórios (/relatorios)
NFSe (/nfse)
NFe (/nfe)
Disco virtual (/disco-virtual)
Usuários (/usuarios)
Webhooks (/webhooks)

Fluxo de autenticação obrigatório:

Passo 1: POST para https://api.egestor.com.br/api/oauth/access_token

Body: {{"grant_type": "personal", "personal_token": "API_KEY"}}
Retorna: access_token válido por 900 segundos (15 minutos)


Passo 2: GET para https://v4.egestor.com.br/api/v1/[endpoint]

Header: Authorization: Bearer [access_token]

Parâmetros padrão disponíveis:

filtro (string): Filtra dados pelo valor informado
page (integer): Número da página para paginação (50 registros por página)

Observações importantes:

URL de autenticação: https://api.egestor.com.br/api/oauth/access_token
Base URL para endpoints: https://v4.egestor.com.br/api/v1
Access token expira em 15 minutos (900 segundos)
Considere apenas rotas com método GET
Todas as respostas são paginadas (50 registros por página)
Autenticação em duas etapas é obrigatória
Parameters deve conter apenas query parameters
Foque na rota GET mais específica para a pergunta

Pergunta do usuário:
{question}
Documentação da API eGestor:
{openapi}
Retorne apenas o JSON solicitado.
"""


def route_validator(question):
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "openapi"]
    )

    with open('openapi.apib', 'r', encoding='utf8') as file:
        openapi = file.read()

    prompt_format = prompt.format(question=question, openapi=openapi)
    response = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response.content

