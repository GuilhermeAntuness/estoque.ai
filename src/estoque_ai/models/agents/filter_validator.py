from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from models import llm_gemini
from route_checker import route_validator

"""

Agente Validador de Parâmetros Obrigatórios para API

Este agente inteligente valida se uma pergunta/solicitação do usuário contém todos os 
parâmetros obrigatórios necessários para executar uma requisição à API. Ele recebe como 
entrada a pergunta do usuário e os dados estruturados da rota selecionada (incluindo 
parâmetros, método HTTP e documentação), analisa quais campos são obrigatórios vs opcionais, 
e retorna um JSON indicando se a validação passou ou quais campos obrigatórios estão 
faltando. O agente considera variações linguísticas naturais e exclui automaticamente 
campos de autenticação que são gerenciados pelo sistema.
"""


template = """
Você é um agente inteligente que valida se a pergunta do usuário contém os **filtros obrigatórios** necessários para fazer uma requisição à API.

## Objetivo:
Verificar se todos os campos marcados como obrigatórios estão presentes na pergunta feita pelo usuário, baseando-se nas informações da rota selecionada.

## Estrutura de dados recebida:
Você receberá um JSON com:
- `validated`: indica se a rota foi validada
- `selected_route`: contém informações da rota incluindo:
  - `path`: caminho da API
  - `method`: método HTTP
  - `parameters`: parâmetros disponíveis (com indicação se são opcionais ou obrigatórios)
  - `authentication_flow`: fluxo de autenticação
  - `base_url` e `full_url`: URLs da API

## Instruções:
1. Analise os `parameters` da `selected_route` e identifique quais campos são obrigatórios.
   - Campos marcados como "optional" NÃO são obrigatórios
   - Campos sem marcação "optional" devem ser considerados obrigatórios
   - Para métodos POST, PATCH, PUT, verifique também campos obrigatórios no body da requisição

2. Verifique se esses campos obrigatórios aparecem na pergunta do usuário.

3. Se **todos os campos obrigatórios estiverem presentes**, retorne:
```json
{{ "validated": true }}
```

4. Se algum campo obrigatório estiver ausente, retorne:
```json
{{
  "validated": false,
  "missing_fields": [
    {{
      "name": "nome_do_campo_faltante",
      "required": true,
      "description": "descrição do campo se disponível"
    }}
  ]
}}
```

5. Se não houver nenhum campo obrigatório na rota (apenas campos opcionais), retorne:
```json
{{ "validated": true }}
```

## Observações importantes:
- A autenticação (access_token, personal_token) é gerenciada automaticamente e NÃO deve ser considerada como campo obrigatório da pergunta do usuário
- Parâmetros marcados como "optional" podem estar ausentes na pergunta
- Considere variações na linguagem natural (ex: "código", "cod", "id" podem se referir ao mesmo campo)

Pergunta do usuário: 
{question}

Dados da rota:
{rota}

Retorne apenas o JSON solicitado.
"""

def filter_checker(question):
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "openapi"]
    )

    rota = route_validator(question)

    prompt_format = prompt.format(question=question, rota=rota)
    response = llm_gemini.invoke([HumanMessage(content=prompt_format)])
    return response.content, rota


