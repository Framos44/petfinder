PetMatch AI — Requisitos
Objetivo

Criar uma aplicação simples para ajudar pessoas a encontrar animais perdidos por meio de comparação de imagens com inteligência artificial.

Funcionalidades principais
RF01 — Cadastro de animais

Permitir cadastrar animais perdidos ou encontrados com:

Foto.
Espécie.
Cor e características.
Data da ocorrência.
Cidade ou localização aproximada.
Tipo de ocorrência: perdido ou encontrado.
RF02 — Busca visual com IA

Permitir enviar uma foto e comparar com as imagens cadastradas usando um modelo pré-treinado CLIP.

RF03 — Resultados

Exibir os animais visualmente mais semelhantes, com fotos, características, datas e localização.

RF04 — Armazenamento

Guardar os registros no Supabase e armazenar as imagens localmente durante o MVP.

RF05 — Dados de demonstração

Permitir testar o sistema com imagens autorizadas de animais e registros de demonstração.

Tecnologias
Python.
Streamlit.
PyTorch.
Hugging Face Transformers.
CLIP.
Supabase PostgreSQL.
OpenStreetMap, opcional.
Requisitos não funcionais
Interface simples e intuitiva.
Execução local sem Docker.
Configuração por variáveis de ambiente.
Código organizado e documentado.
Tratamento de erros e validação dos arquivos enviados.
Proteção de credenciais e dados pessoais.
Critérios de aceitação
Cadastrar um animal perdido ou encontrado.
Salvar e recuperar os registros.
Enviar uma foto para pesquisa.
Retornar imagens ordenadas por similaridade visual.
Exibir os detalhes dos candidatos.
Executar a aplicação com instruções claras.
Fora do escopo
Aplicativo mobile nativo.
Autenticação complexa.
Notificações automáticas.
Treinamento de modelos do zero.
Microsserviços e processamento distribuído.
Observação

Similaridade visual não comprova identidade. Os resultados devem ser apresentados como possíveis correspondências, sujeitas à confirmação humana.