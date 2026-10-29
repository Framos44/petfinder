PetMatch AI — Design
Arquitetura

Aplicação monolítica em Python com Streamlit, executada localmente.

Tecnologias
Streamlit: interface e fluxo da aplicação.
Python: lógica principal.
PyTorch + Hugging Face Transformers: execução do CLIP.
Supabase PostgreSQL: armazenamento dos registros.
Sistema de arquivos local: imagens durante o MVP.
OpenStreetMap: mapa opcional.
Fluxo principal
O usuário cadastra um animal perdido ou encontrado.
A aplicação salva os metadados no Supabase.
A foto é armazenada localmente.
O modelo CLIP gera um embedding da imagem.
O sistema compara o embedding com os das imagens cadastradas.
Os candidatos são ordenados por similaridade.
A interface exibe fotos e informações dos resultados.
Estrutura sugerida

petmatch-ai/

app.py
requirements.txt
.env.example
.gitignore
README.md
src/
database.py
image_service.py
matching.py
data/
images/
tests/
Banco de dados

Tabela animal_reports:

id
report_type
species
color
description
event_date
city
latitude
longitude
image_path
created_at

Os embeddings podem ser mantidos em memória durante o protótipo e recalculados quando necessário. Para uma base pequena, isso reduz a complexidade do banco. Evitar depender de arquivos locais para imagens em produção ou em uma implantação com múltiplas máquinas.

Busca visual

Utilizar um modelo CLIP pré-treinado para gerar embeddings de imagens e calcular similaridade de cosseno.

Ordenar os resultados do mais semelhante para o menos semelhante. A localização pode ser exibida como informação complementar, sem exigir PostGIS.

Configuração

Utilizar variáveis de ambiente para as credenciais do Supabase. O arquivo .env.example deve conter apenas valores ilustrativos.

Execução

A aplicação deve iniciar com Streamlit, sem Docker e sem serviços intermediários.

Limitações
CLIP encontra semelhanças visuais, mas não garante identificação individual.
A busca deve ser avaliada com imagens de teste conhecidas.
Imagens locais podem não estar disponíveis após implantação em outra máquina.
Datasets externos devem ter suas licenças verificadas.