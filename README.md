# Jovem Aprendiz

Assistente pessoal em Python que entende comandos por **voz** (ou texto) em
**portugues**, responde falando e executa tarefas no computador.

## Etapa atual: 2 - Comandos fixos + Inteligencia Artificial (Gemini)

O Jovem Aprendiz escuta pelo microfone (ou le do teclado) e funciona em duas camadas:

1. **Comandos fixos** (rapidos, offline): abrir programas, sites, hora, data,
   pesquisar, criar pasta.
2. **Inteligencia artificial** (Google Gemini, gratuita): qualquer pergunta ou
   conversa livre que nao seja um comando fixo vai para a IA, que responde em
   portugues e lembra do contexto da conversa.

Se o microfone nao estiver disponivel, ele usa entrada por texto. Se a chave da
IA nao estiver configurada, ele continua funcionando so com os comandos fixos.

### O que ele ja sabe fazer

| Diga / digite                     | Acao                                      |
|-----------------------------------|-------------------------------------------|
| "que horas sao"                   | Fala a hora atual                         |
| "que dia e hoje"                  | Fala a data atual                         |
| "abrir chrome" / "abrir calculadora" | Abre programas do Windows              |
| "abrir youtube" / "abrir github"  | Abre sites no navegador                   |
| "pesquisar <algo>"                | Pesquisa no Google                        |
| "quem foi <pessoa>"               | Resumo da Wikipedia                       |
| "criar pasta <nome>"              | Cria uma pasta na area de trabalho        |
| "wikipedia <assunto>"             | Resumo da Wikipedia                       |
| qualquer pergunta livre           | Responde usando a IA (Gemini)             |
| "sair" / "tchau"                  | Encerra o Jovem Aprendiz                  |

## Configurar a IA (Gemini) - gratuito

1. Gere uma chave gratuita em https://aistudio.google.com/apikey
2. Abra o arquivo `.env` e cole a chave:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   ```
3. O arquivo `.env` esta no `.gitignore` e nunca vai para o GitHub.

Sem a chave, o Jovem Aprendiz ainda funciona normalmente com os comandos fixos.

## Como rodar

```powershell
# 1. Criar e ativar o ambiente virtual (so na primeira vez)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar as dependencias
pip install -r requirements.txt

# 3. Rodar
python main.py
```

## Estrutura

```
jarvis/
  __init__.py
  voz.py           # fala (TTS) e escuta (STT)
  habilidades.py   # as acoes que o Jovem Aprendiz executa
  cerebro.py       # interpreta o comando e escolhe a habilidade
main.py            # ponto de entrada
requirements.txt   # dependencias
```

## Personalizar a voz

A voz usa **Edge TTS** (vozes neurais em pt-BR, soam naturais - precisa de
internet). Se ficar offline, cai automaticamente para a voz do Windows.

Para trocar a voz, edite o topo de `jarvis/voz.py`:

```python
VOZ_EDGE = "pt-BR-FranciscaNeural"  # feminina (padrao)
VELOCIDADE = "+8%"                   # ex: "+0%", "+20%", "-10%"
TOM = "+0Hz"                         # ex: "+0Hz", "+30Hz", "-20Hz"
```

Vozes pt-BR disponiveis:

| Voz                               | Genero    |
|-----------------------------------|-----------|
| `pt-BR-FranciscaNeural`           | feminina  |
| `pt-BR-AntonioNeural`             | masculina |
| `pt-BR-ThalitaMultilingualNeural` | feminina  |

Para ouvir todas as vozes de qualquer idioma:

```powershell
.\.venv\Scripts\python.exe -c "import asyncio, edge_tts; [print(v['ShortName']) for v in asyncio.run(edge_tts.list_voices()) if v['Locale'].startswith('pt')]"
```

## Observacoes

- **Voz em portugues:** o Windows pode so ter voz em ingles instalada. Para
  uma voz em pt-BR, va em *Configuracoes > Hora e idioma > Fala* e adicione a
  voz portuguesa. O Jovem Aprendiz seleciona automaticamente uma voz pt se existir.
- **Python 3.13+:** use `SpeechRecognition>=3.14` (versoes antigas quebram
  porque dependem do modulo `aifc`, removido do Python 3.13).

## Proximos passos

- **Etapa 2:** plugar uma LLM gratuita (Google Gemini) no cerebro para
  entender comandos livres e conversar, nao so palavras-chave.
