# PetMatch AI (MVP)

Aplicação local em **Python + Streamlit** que ajuda a reencontrar animais perdidos:
cadastre animais perdidos/encontrados e pesquise por foto usando o modelo
pré-treinado **CLIP** (Hugging Face) com similaridade de cosseno.

> ⚠️ **Similaridade visual não comprova identidade.** Os resultados são *possíveis
> correspondências* e precisam de confirmação humana (sinais particulares, local, data).

## Arquitetura

```
app.py                  # interface Streamlit (Início, Cadastrar, Buscar, Registros)
src/config.py           # variáveis de ambiente (.env)
src/database.py         # validação + Supabase ou modo demonstração local (JSON)
src/image_service.py    # validação, gravação e leitura das imagens locais
src/matching.py         # CLIP (carregado uma vez), cache de embeddings, ranking
scripts/seed_demo.py    # popula dados de demonstração
scripts/make_query_variant.py  # gera variação de uma foto para testar a busca
scripts/check_search.py # avalia a busca (top-1) com as consultas de demonstração
sql/schema.sql          # tabela animal_reports para o Supabase
tests/                  # testes (pytest), não dependem do CLIP nem do Supabase
data/images/            # imagens do MVP (locais, fora do git)
```

- Metadados: Supabase PostgreSQL (tabela `animal_reports`) ou, sem Supabase configurado,
  **modo demonstração local** em `data/demo_db.json` (indicado em amarelo na barra lateral).
- Imagens: salvas em `data/images/` com nome aleatório, redimensionadas (máx. 1024 px) e sem EXIF.
- Embeddings: calculados com CLIP e mantidos em memória (recalculados se a imagem mudar).
- A foto usada na busca **não é salva**.
- Sem Docker, FastAPI, Redis, Celery, pgvector ou PostGIS.

## Requisitos

- Windows, Linux ou macOS com **Python 3.10 a 3.12**.
- ~2 GB livres (PyTorch + modelo CLIP de ~600 MB, baixado no primeiro uso).
- Internet na primeira busca (download do modelo). Depois funciona offline.

## Instalação (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.example .env`

> Se o PowerShell bloquear o `Activate.ps1`, rode
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ou use `.\.venv\Scripts\python.exe` diretamente.

## Configuração

### Opção A: modo demonstração local (sem Supabase)

No `.env`, deixe `SUPABASE_URL` **ou** `SUPABASE_KEY` vazio. Os registros ficam em
`data/demo_db.json`. Nada é enviado para serviços externos (exceto o download do modelo CLIP).

### Opção B: Supabase

1. Crie um projeto em <https://supabase.com>.
2. No **SQL Editor**, execute `sql/schema.sql` (cria a tabela, RLS e políticas de leitura/inserção).
3. Em *Project Settings → API*, copie a **Project URL** e a chave **anon/public**.
4. Preencha no `.env`:
   ```
   SUPABASE_URL=https://<seu-projeto>.supabase.co
   SUPABASE_KEY=<sua-chave-anon>
   ```
5. Nunca faça commit do `.env` (ele está no `.gitignore`). Não use a chave `service_role` no MVP.

## Executar

```powershell
streamlit run app.py
```

Abra <http://localhost:8501>. A barra lateral mostra se o app está em **MODO DEMONSTRAÇÃO LOCAL**
ou **Conectado ao Supabase**.

## Testar a busca visual com dados de demonstração

```powershell
python scripts/seed_demo.py        # cria 6 registros [DEMO] + consultas em data/demo_queries/
python scripts/check_search.py     # opcional: mede no terminal se a original fica em 1º lugar
streamlit run app.py
```

No app, abra **Buscar por foto**, envie um arquivo de `data/demo_queries/` (versões espelhadas,
recortadas e mais claras dos registros) e clique em **Buscar semelhantes**. O registro
correspondente deve aparecer entre os primeiros, com foto, características, data e local.

As imagens geradas pelo seed são desenhos sintéticos (sem direitos de terceiros), úteis para
validar o fluxo. Para um teste mais realista, use **fotos autorizadas** (suas ou com licença
compatível, verificando a licença de qualquer dataset):

```powershell
python scripts/seed_demo.py --from-folder C:\caminho\fotos   # metadata.csv opcional na pasta
python scripts/make_query_variant.py C:\caminho\fotos\rex.jpg consulta_rex.jpg
```

Formato do `metadata.csv`:
`filename,report_type,species,color,description,event_date,city,latitude,longitude`

Para recomeçar o modo demonstração, apague `data/demo_db.json` e o conteúdo de `data/images/`.

## Testes

```powershell
python -m pytest -q
```

Os testes usam um "embedder" falso, então não baixam o CLIP nem acessam o Supabase.

## Limitações do MVP

- CLIP encontra semelhança visual, não identifica o indivíduo. Animais da mesma raça/cor
  terão pontuação alta. O rótulo (alta/média/baixa) é qualitativo, não uma probabilidade.
- Imagens são locais: em outra máquina, registros do Supabase aparecem sem foto e são
  ignorados na busca (o app avisa). Para produção, mova as imagens para um storage (ex.: Supabase Storage).
- Embeddings ficam em memória e são recalculados a cada reinício (adequado para bases pequenas).
- Sem autenticação: qualquer pessoa com acesso ao app pode cadastrar. Não coloque dados
  pessoais (telefone, endereço) na descrição.
