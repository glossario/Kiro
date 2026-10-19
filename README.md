# Jarvis

Assistente pessoal em Python que entende comandos por **voz** (ou texto) em
**portugues**, responde falando e executa tarefas no computador.

## Etapa atual: 1 - Comandos por palavra-chave

O Jarvis escuta pelo microfone, interpreta o comando por palavras-chave e
responde. Se o microfone nao estiver disponivel, ele usa entrada por texto
automaticamente.

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
| "sair" / "tchau"                  | Encerra o Jarvis                          |

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
  habilidades.py   # as acoes que o Jarvis executa
  cerebro.py       # interpreta o comando e escolhe a habilidade
main.py            # ponto de entrada
requirements.txt   # dependencias
```

## Observacoes

- **Voz em portugues:** o Windows pode so ter voz em ingles instalada. Para
  uma voz em pt-BR, va em *Configuracoes > Hora e idioma > Fala* e adicione a
  voz portuguesa. O Jarvis seleciona automaticamente uma voz pt se existir.
- **Python 3.13+:** use `SpeechRecognition>=3.14` (versoes antigas quebram
  porque dependem do modulo `aifc`, removido do Python 3.13).

## Proximos passos

- **Etapa 2:** plugar uma LLM gratuita (Google Gemini) no cerebro para
  entender comandos livres e conversar, nao so palavras-chave.
