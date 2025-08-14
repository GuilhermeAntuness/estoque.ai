
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from .models import llm_groq
from ...main import API_KEY
from filter_validator import filter_checker

"""
Agente Extrator de Parâmetros de API

Este agente inteligente analisa perguntas em linguagem natural e extrai parâmetros 
específicos para formar requisições de API. Ele recebe a pergunta do usuário, os dados 
da rota validada (com parâmetros disponíveis) e a API_KEY, então mapeia termos em 
linguagem natural para os parâmetros corretos da API (strings, números, booleanos, datas). 
O agente retorna um JSON estruturado com os parâmetros extraídos, informações de 
autenticação e dados da requisição, ou indica quais informações adicionais são necessárias 
se a extração for incompleta.
"""


template = """

Você é um agente inteligente especializado em extrair parâmetros de perguntas de usuários para formar requisições de API.

## Objetivo:
Analisar a pergunta do usuário e extrair todos os parâmetros necessários para executar a requisição na API, baseando-se nos parâmetros disponíveis na rota selecionada.

## Estrutura de dados recebida:
Você receberá:
1. **Pergunta do usuário**: A solicitação em linguagem natural
2. **Dados da rota validada**: JSON com `selected_route` contendo parâmetros disponíveis
3. **API_KEY**: Chave de acesso para autenticação na API

## Instruções de extração:

### 1. Analise os parâmetros disponíveis
- Examine todos os parâmetros em `selected_route.parameters`
- Identifique o tipo de cada parâmetro (`string`, `integer`, `boolean`, etc.)
- Note a descrição e valores possíveis de cada parâmetro

### 2. Mapeamento de linguagem natural
Considere as seguintes equivalências comuns:
- **filtro/busca**: "buscar", "procurar", "encontrar", "listar com", "que contém"
- **códigos**: "código", "cod", "id", "identificador"
- **datas**: "antes de", "depois de", "até", "desde", "a partir de"
- **números**: "maior que", "menor que", "igual a"
- **booleanos**: "sim/não", "ativo/inativo", "arquivado/não arquivado"

### 3. Extração de valores
- **Strings**: Extraia termos entre aspas ou palavras-chave após indicadores
- **Números**: Identifique valores numéricos no texto
- **Datas**: Converta datas para o formato "YYYY-MM-DD HH:MM:SS"
- **Booleanos**: Converta "sim/não", "ativo/inativo" para true/false

### 4. Formato de retorno
Retorne um JSON com a seguinte estrutura:

```json
{{
  "success": true,
  "extracted_parameters": {{
    "nome_do_parametro": "valor_extraido",
    "outro_parametro": valor_numerico_ou_boolean
  }},
  "authentication": {{
    "api_key": "valor_da_api_key_recebida",
    "method": "bearer_token_ou_personal_token"
  }},
  "request_info": {{
    "method": "GET/POST/PUT/etc",
    "url": "url_completa_da_requisicao",
    "has_required_params": true
  }}
}}
```

### 5. Se não conseguir extrair parâmetros suficientes:
```json
{{
  "success": false,
  "error": "Não foi possível extrair parâmetros suficientes",
  "missing_context": [
    "Especifique qual produto você está procurando",
    "Informe o código da categoria desejada"
  ],
  "available_parameters": ["lista dos parâmetros disponíveis"]
}}
```

## Exemplos de mapeamento:

### Pergunta: "Buscar produtos que contém 'notebook' na categoria 5"
**Extração**:
- `filtro`: "notebook" (busca nos campos código, nome, etc.)
- `codCategoria`: 5 (código da categoria)

### Pergunta: "Listar produtos arquivados que controlam estoque"
**Extração**:
- `arquivado`: true
- `controlarEstoque`: 1

### Pergunta: "Produtos alterados depois de 15/01/2024"
**Extração**:
- `updatedAfter`: "2024-01-15 00:00:00"

## Dados de entrada:

**Pergunta do usuário:**
{pergunta}

**Dados da rota:**
{rota_data}

**API Key:**
{api_key}

Analise cuidadosamente a pergunta e extraia todos os parâmetros possíveis. Retorne apenas o JSON solicitado.

"""

def gerar_resposta(pergunta):
    prompt = PromptTemplate(
        template=template,
        input_variables=["pergunta", "resultado"]
    )

    validacao, rota = filter_checker(pergunta)
    validacao = validacao.strip("```json").strip("```").strip()
    validacao = json.loads(validacao)

    return resposta.content


