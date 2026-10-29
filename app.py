"""PetMatch AI - interface Streamlit.

Execute com:  streamlit run app.py
"""
from __future__ import annotations

from datetime import date

import streamlit as st

from src.config import get_settings
from src.database import (
    REPORT_TYPES,
    SPECIES,
    DatabaseError,
    LocalRepository,
    ValidationError,
    get_repository,
    validate_report,
)
from src.image_service import ImageValidationError, load_image, save_image, validate_image
from src.matching import ClipEmbedder, EmbeddingCache, ModelLoadError, rank_candidates

DISCLAIMER = (
    "A similaridade visual indica apenas **possíveis correspondências**. "
    "Ela não confirma que se trata do mesmo animal: verifique sinais particulares, "
    "local e data, e confirme pessoalmente."
)

settings = get_settings()
st.set_page_config(page_title="PetMatch AI", page_icon="🐾", layout="wide")


# ---------- Recursos carregados uma única vez ----------

@st.cache_resource(show_spinner=False)
def get_embedding_cache() -> EmbeddingCache:
    """Carrega o CLIP uma única vez por processo e mantém os embeddings em memória."""
    return EmbeddingCache(ClipEmbedder(settings.clip_model_name))


@st.cache_resource(show_spinner=False)
def get_repo():
    return get_repository(settings)


# ---------- Componentes ----------

def show_mode_banner(repo) -> None:
    if isinstance(repo, LocalRepository):
        st.sidebar.warning(
            "🧪 **MODO DEMONSTRAÇÃO LOCAL**\n\n"
            "Supabase não configurado. Os registros ficam em "
            f"`{settings.demo_db_path.name}` nesta máquina."
        )
    else:
        st.sidebar.success("🟢 Conectado ao Supabase")


def osm_link(report: dict) -> str | None:
    lat, lon = report.get("latitude"), report.get("longitude")
    if lat is None or lon is None:
        return None
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}"


def show_report_details(report: dict) -> None:
    kind = "🔴 Perdido" if report.get("report_type") == "perdido" else "🟢 Encontrado"
    st.markdown(f"**{kind}** · {str(report.get('species', '')).capitalize()}")
    st.markdown(f"**Cor/características:** {report.get('color', '-')}")
    if report.get("description"):
        st.markdown(f"**Descrição:** {report['description']}")
    st.markdown(f"**Data:** {report.get('event_date', '-')}")
    st.markdown(f"**Local:** {report.get('city', '-')}")
    link = osm_link(report)
    if link:
        st.markdown(f"[Ver no OpenStreetMap]({link})")


def show_image(image_path: str) -> None:
    image = load_image(image_path)
    if image is None:
        st.info("Imagem não disponível nesta máquina.")
    else:
        st.image(image, use_column_width=True)


def read_upload(uploaded):
    """Valida o arquivo enviado. Mostra erro e retorna None se for inválido."""
    if uploaded is None:
        return None
    try:
        return validate_image(uploaded.getvalue(), uploaded.name, settings.max_upload_mb)
    except ImageValidationError as exc:
        st.error(f"Imagem inválida: {exc}")
        return None


def load_reports(repo) -> list[dict]:
    try:
        return repo.list_reports()
    except DatabaseError as exc:
        st.error(str(exc))
        return []


# ---------- Páginas ----------

def page_home(repo) -> None:
    st.title("🐾 PetMatch AI")
    st.write(
        "Ajuda a reencontrar animais perdidos comparando fotos com registros de "
        "animais perdidos e encontrados, usando o modelo pré-treinado **CLIP**."
    )
    st.markdown(
        "1. **Cadastrar**: registre um animal perdido ou encontrado com foto.\n"
        "2. **Buscar**: envie uma foto e veja os registros visualmente mais parecidos.\n"
        "3. **Registros**: consulte todos os cadastros."
    )
    st.info(DISCLAIMER)
    reports = load_reports(repo)
    col1, col2, col3 = st.columns(3)
    col1.metric("Registros", len(reports))
    col2.metric("Perdidos", sum(r.get("report_type") == "perdido" for r in reports))
    col3.metric("Encontrados", sum(r.get("report_type") == "encontrado" for r in reports))


def page_register(repo) -> None:
    st.header("Cadastrar animal")
    st.caption("Não inclua dados pessoais (telefone, endereço) na descrição.")
    with st.form("register", clear_on_submit=True):
        uploaded = st.file_uploader("Foto do animal *", type=["jpg", "jpeg", "png", "webp"])
        c1, c2 = st.columns(2)
        report_type = c1.selectbox("Tipo de ocorrência *", REPORT_TYPES)
        species = c2.selectbox("Espécie *", SPECIES)
        color = st.text_input("Cor e características *", max_chars=100)
        description = st.text_area("Descrição (opcional)", max_chars=1000)
        c3, c4 = st.columns(2)
        event_date = c3.date_input("Data da ocorrência *", value=date.today(), max_value=date.today())
        city = c4.text_input("Cidade ou localização aproximada *", max_chars=120)
        with st.expander("Coordenadas aproximadas (opcional)"):
            c5, c6 = st.columns(2)
            latitude = c5.text_input("Latitude", placeholder="-23.55")
            longitude = c6.text_input("Longitude", placeholder="-46.63")
        submitted = st.form_submit_button("Cadastrar", type="primary")

    if not submitted:
        return
    if uploaded is None:
        st.error("Envie uma foto do animal.")
        return
    image = read_upload(uploaded)
    if image is None:
        return

    report = {
        "report_type": report_type, "species": species, "color": color,
        "description": description, "event_date": event_date, "city": city,
        "latitude": latitude, "longitude": longitude, "image_path": "pendente",
    }
    try:
        validate_report(report)  # valida antes de gravar a imagem em disco
        report["image_path"] = save_image(image, settings.images_dir)
        with st.spinner("Salvando registro..."):
            saved = repo.add_report(report)
    except (ValidationError, DatabaseError) as exc:
        st.error(str(exc))
        return
    except OSError as exc:
        st.error(f"Não foi possível salvar a imagem: {exc}")
        return
    st.success(f"Registro salvo (id {saved.get('id')}).")


def page_search(repo) -> None:
    st.header("Buscar por foto")
    st.info(DISCLAIMER)
    uploaded = st.file_uploader("Foto para pesquisa", type=["jpg", "jpeg", "png", "webp"])
    c1, c2, c3 = st.columns(3)
    type_filter = c1.selectbox("Procurar entre", ["todos", "encontrado", "perdido"])
    species_filter = c2.selectbox("Espécie", ["todas", *SPECIES])
    top_k = c3.slider("Quantidade de resultados", 1, 20, 5)

    image = read_upload(uploaded)
    if image is None:
        return
    st.image(image, caption="Foto enviada (não é salva)", width=250)

    if not st.button("Buscar semelhantes", type="primary"):
        return
    reports = load_reports(repo)
    if not reports:
        st.warning("Nenhum registro cadastrado ainda.")
        return

    try:
        with st.spinner("Carregando o modelo CLIP (apenas na primeira vez)..."):
            cache = get_embedding_cache()
        with st.spinner(f"Comparando com {len(reports)} registros..."):
            query = cache.embedder(image)
            matches, missing = rank_candidates(
                query, reports, cache, top_k=top_k,
                species=None if species_filter == "todas" else species_filter,
                report_type=None if type_filter == "todos" else type_filter,
            )
    except ModelLoadError as exc:
        st.error(f"{exc}\n\nVerifique a conexão (o modelo é baixado no primeiro uso).")
        return
    except Exception as exc:  # erro inesperado na inferência
        st.error(f"Erro durante a busca visual: {exc}")
        return

    if missing:
        st.warning(f"{missing} registro(s) ignorado(s) porque a imagem não está nesta máquina.")
    if not matches:
        st.warning("Nenhum registro compatível com os filtros.")
        return

    st.subheader("Possíveis correspondências (do mais ao menos semelhante)")
    for rank, match in enumerate(matches, start=1):
        with st.container(border=True):
            left, right = st.columns([1, 2])
            with left:
                show_image(match.report.get("image_path", ""))
            with right:
                st.markdown(
                    f"### #{rank} · semelhança visual {match.level} "
                    f"({match.score:.3f})"
                )
                show_report_details(match.report)


def page_list(repo) -> None:
    st.header("Registros cadastrados")
    reports = load_reports(repo)
    if not reports:
        st.info("Nenhum registro ainda. Use **Cadastrar** ou rode `python scripts/seed_demo.py`.")
        return
    type_filter = st.selectbox("Tipo", ["todos", *REPORT_TYPES])
    if type_filter != "todos":
        reports = [r for r in reports if r.get("report_type") == type_filter]
    cols = st.columns(3)
    for i, report in enumerate(reports):
        with cols[i % 3], st.container(border=True):
            show_image(report.get("image_path", ""))
            show_report_details(report)


def main() -> None:
    try:
        repo = get_repo()
    except DatabaseError as exc:
        st.error(f"{exc}\n\nConfira SUPABASE_URL e SUPABASE_KEY no arquivo .env.")
        st.stop()

    show_mode_banner(repo)
    pages = {
        "Início": page_home,
        "Cadastrar": page_register,
        "Buscar por foto": page_search,
        "Registros": page_list,
    }
    choice = st.sidebar.radio("Navegação", list(pages))
    pages[choice](repo)


main()
