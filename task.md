PetMatch AI — Tasks

Legenda: [x] concluído e verificado · [ ] pendente

Fase 1 — Preparação
- [x] Inspecionar o repositório existente. (havia apenas requirements.md, design.md e task.md; nenhum código anterior a preservar)
- [x] Simplificar a estrutura para Python + Streamlit. (sem Docker, Next.js, FastAPI, Redis, Celery, pgvector ou PostGIS)
- [x] Criar ambiente virtual e requirements.txt. (.venv criado com Python 3.12; dependências instaladas e importadas com sucesso)
- [x] Configurar variáveis de ambiente. (.env.example com valores ilustrativos; src/config.py)
- [x] Criar instruções de execução no README.md.

Fase 2 — Banco de dados
- [x] Configurar conexão com Supabase. (src/database.py, SupabaseRepository; ativada por SUPABASE_URL/SUPABASE_KEY)
- [ ] Criar a tabela de registros de animais. (script pronto em sql/schema.sql; falta executá-lo no seu projeto Supabase)
- [x] Implementar cadastro e consulta dos registros. (testado no modo local; com Supabase real ainda não testado)
- [x] Preparar alternativa local para demonstração, se necessário. (LocalRepository em data/demo_db.json, sinalizado na interface)

Fase 3 — Imagens e IA
- [x] Implementar upload e validação de imagens. (extensão, tamanho, conteúdo real, resolução; EXIF removido)
- [x] Carregar CLIP uma única vez. (st.cache_resource + EmbeddingCache em memória)
- [x] Gerar embeddings das imagens cadastradas.
- [x] Implementar similaridade de cosseno.
- [x] Retornar os candidatos mais semelhantes. (com filtros por espécie e tipo)
- [ ] Testar com imagens de animais conhecidos. (testado só com imagens sintéticas geradas pelo seed; falta testar com fotos reais autorizadas)

Fase 4 — Interface
- [x] Criar página inicial no Streamlit.
- [x] Criar formulário de cadastro.
- [x] Criar formulário de busca por imagem.
- [x] Exibir resultados com fotos e características.
- [x] Exibir datas e localizações. (com link opcional para o OpenStreetMap)
- [x] Adicionar estados de carregamento e mensagens de erro.

Fase 5 — Validação
- [x] Testar cadastro e consulta. (tests/test_database.py)
- [x] Testar busca visual. (tests/test_matching.py com embedder falso; scripts/check_search.py com CLIP real: 6/6 em 1º lugar com as imagens de demonstração)
- [x] Testar a interface. (tests/test_app.py renderiza todas as páginas com Streamlit AppTest)
- [x] Verificar tratamento de imagens inválidas. (tests/test_image_service.py)
- [x] Conferir proteção de credenciais. (.env no .gitignore, nenhuma chave no código, RLS em sql/schema.sql)
- [x] Preparar dados autorizados para demonstração. (scripts/seed_demo.py gera imagens sintéticas próprias; --from-folder para fotos autorizadas)
- [x] Atualizar a documentação.

Critério de conclusão do MVP

O usuário consegue cadastrar animais, enviar uma foto e visualizar os registros mais semelhantes encontrados pela IA, com suas informações principais.

Não iniciar funcionalidades fora do escopo antes de concluir o fluxo principal.
