"""Streamlit Cloud edition of Search Stage Marrakech / InternMatch.

The app works in "web sources" mode by default.  If MySQL credentials are
provided in Streamlit secrets, it also reads the companies and offers created
by the FastAPI/MySQL version of the project.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Search Stage Marrakech",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


EXTERNAL_OFFERS: list[dict[str, Any]] = [
    {
        "id": "digitalspeak-web-mobile-marrakech",
        "title": "Stage Développeur Web / Mobile — projets réels",
        "company": "Digital Speak Group",
        "city": "Marrakech",
        "offer_type": "stage",
        "field": "Informatique",
        "summary": "Stage de 3 à 6 mois en développement web/mobile avec React, Vue, Laravel, Node.js ou WordPress.",
        "source": "Stagiaires.ma",
        "url": "https://www.stagiaires.ma/stage-emploi-maroc/7696-stage-developpeur-web-mobile-projets-applicatifs-reels-marrakech",
        "checked_at": "2026-11-08",
    },
    {
        "id": "maroc-fer-stage-it-security",
        "title": "Stage PFE en sécurité et automatisation IT",
        "company": "MAROC FER",
        "city": "Marrakech",
        "offer_type": "stage",
        "field": "Informatique · Cybersécurité",
        "summary": "Stage PFE Bac+5 autour de la sécurité et de l’automatisation des infrastructures IT.",
        "source": "MoroccanZ Future",
        "url": "https://future.moroccanz.org/fr/o/stage-pfe-en-securisation-et-automatisation-des-infrastructures-it-y5xnf4v5",
        "checked_at": "2026-11-08",
    },
    {
        "id": "hello-world-fullstack-marrakech",
        "title": "Stagiaire Développeur Web Full Stack",
        "company": "Hello World",
        "city": "Marrakech",
        "offer_type": "stage",
        "field": "Informatique",
        "summary": "Stage en développement web avec HTML, CSS, JavaScript et PHP, ouvert aux profils Bac+2/3.",
        "source": "Postule.ma",
        "url": "https://www.postule.ma/job/stage-en-developpement-web-full-stack-hf-hello-world-opju13r7",
        "checked_at": "2026-11-08",
    },
    {
        "id": "anapec-senior-php-symfony-marrakech",
        "title": "Développeur Senior PHP / Symfony",
        "company": "Recrutement ANAPEC",
        "city": "Marrakech",
        "offer_type": "emploi",
        "field": "Informatique",
        "summary": "CDI à Marrakech-Ménara, avec 3 à 5 ans d’expérience. Référence ANAPEC ET0211261200327.",
        "source": "ANAPEC · Wadifa Public",
        "url": "https://www.wadifapublic.ma/fr/anapec/897d30a0-a713-4774-8ed4-9982c605121a",
        "checked_at": "2026-11-08",
    },
]

FIELDS = [
    "Toutes les filières", "Informatique", "Data", "Réseaux", "Marketing",
    "Commerce", "Finance", "Ressources humaines", "Gestion", "Ingénierie",
    "Design", "Logistique", "Tourisme", "Droit", "Santé", "Éducation",
    "BTP", "Qualité", "Agriculture", "Autre",
]
CITIES = ["Marrakech", "Casablanca", "Rabat", "Tanger", "Agadir", "Fès"]


def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "favorites": set(),
        "profile": {"name": "", "email": "", "city": "Marrakech", "field": "Informatique", "skills": ""},
        "application_notice": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def mysql_configured() -> bool:
    try:
        config = st.secrets.get("mysql", {})
        return all(config.get(key) for key in ("host", "database", "user", "password"))
    except Exception:
        # Secrets are optional on Streamlit Community Cloud.  A missing or
        # incomplete secrets file must not prevent the public web mode from
        # starting.
        return False


@st.cache_data(ttl=300, show_spinner=False)
def load_mysql_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    """Return offers, companies and an optional public configuration error."""
    if not mysql_configured():
        return [], [], None

    try:
        import pymysql

        config = st.secrets["mysql"]
        connection = pymysql.connect(
            host=config["host"],
            port=int(config.get("port", 3306)),
            user=config["user"],
            password=config["password"],
            database=config["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=7,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT o.id, o.title, o.description, o.offer_type, o.filiere,
                           o.city, o.application_url, o.publication_date, c.name AS company
                    FROM offers AS o
                    JOIN companies AS c ON c.id = o.company_id
                    WHERE o.status = 'active'
                    ORDER BY o.publication_date DESC, o.id DESC
                    LIMIT 100
                    """
                )
                offers = cursor.fetchall()
                cursor.execute(
                    """
                    SELECT id, name, sector, city, address, latitude, longitude, website
                    FROM companies
                    ORDER BY created_at DESC, id DESC
                    LIMIT 200
                    """
                )
                companies = cursor.fetchall()
        finally:
            connection.close()

        normalized = [
            {
                "id": f"mysql-{row['id']}",
                "title": row["title"],
                "company": row["company"],
                "city": row["city"],
                "offer_type": row["offer_type"],
                "field": row.get("filiere") or "Autre",
                "summary": row["description"],
                "source": "Base InternMatch",
                "url": row.get("application_url") or "",
                "checked_at": str(row.get("publication_date") or ""),
            }
            for row in offers
            if not row["title"].strip().lower().startswith("demo")
        ]
        return normalized, companies, None
    except Exception:
        return [], [], "La base MySQL configurée ne répond pas pour le moment."


def apply_css() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#101a52; --purple:#5d32dc; --violet:#7138ea; --pale:#f4f6ff; }
        .stApp { background:#f5f7ff; color:#162052; }
        [data-testid="stSidebar"] { background:linear-gradient(180deg,#101746 0%,#0d1640 100%); }
        [data-testid="stSidebar"] * { color:#f5f5ff; }
        [data-testid="stSidebar"] .stRadio label { padding:7px 10px; border-radius:8px; }
        [data-testid="stSidebar"] .stRadio label:hover { background:#33238d; }
        .hero { background:linear-gradient(112deg,#1735a8 0%,#5d36cd 52%,#f26a83 100%); color:white;
          padding:28px 32px; border-radius:18px; min-height:165px; position:relative; overflow:hidden;
          box-shadow:0 10px 24px rgba(49,55,150,.17); }
        .hero:after { content:""; position:absolute; width:270px; height:270px; right:-65px; top:-135px;
          background:rgba(255,255,255,.14); border-radius:50%; }
        .hero h1 { color:white; margin:10px 0 6px; font-size:2.15rem; line-height:1.05; }
        .hero p { color:#f6f4ff; margin:0; }
        .eyebrow { font-weight:700; letter-spacing:.12em; font-size:.66rem; text-transform:uppercase; }
        .metric-card { background:white; border-radius:14px; padding:16px 18px; min-height:86px;
          border:1px solid #e9eafb; box-shadow:0 5px 18px rgba(30,35,100,.05); }
        .metric-label { color:#596385; font-size:.75rem; margin-bottom:6px; }
        .metric-value { color:#111a4d; font-size:1.65rem; font-weight:800; }
        .metric-help { color:#8790ad; font-size:.66rem; }
        .section-card { background:#fff; border:1px solid #e8e9f6; border-radius:15px; padding:18px; margin:8px 0 15px;
          box-shadow:0 5px 16px rgba(30,35,100,.035); }
        .section-card h3 { margin:0 0 4px; color:#121c55; }
        .section-card p { color:#6b7393; font-size:.82rem; margin:0 0 12px; }
        .offer-card { background:#fff; border:1px solid #e7e9f6; border-radius:15px; padding:16px 17px; margin:0 0 12px;
          box-shadow:0 5px 14px rgba(30,35,100,.04); }
        .offer-tag { display:inline-block; background:#eaf8ef; color:#16804d; border-radius:999px; padding:4px 9px;
          font-size:.66rem; font-weight:700; margin-bottom:8px; }
        .offer-tag.job { background:#fff2e9; color:#d66e1d; }
        .offer-card h4 { margin:0 0 3px; font-size:1.03rem; color:#131c52; }
        .offer-company { color:#46517b; font-size:.82rem; font-weight:650; }
        .offer-meta { color:#838ba6; font-size:.74rem; margin-top:8px; }
        .notice { color:#786000; background:#fff9df; padding:10px 13px; border-radius:10px; font-size:.8rem; }
        div[data-testid="stButton"] button, div[data-testid="stLinkButton"] a { border-radius:9px; font-weight:700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric(label: str, value: int, subtitle: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-help">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def offer_card(offer: dict[str, Any], show_favorite: bool = True) -> None:
    offer_type = offer["offer_type"]
    label = "Stage" if offer_type == "stage" else "Emploi"
    css_class = "offer-tag" if offer_type == "stage" else "offer-tag job"
    st.markdown(
        f'<div class="offer-card"><span class="{css_class}">{label}</span>'
        f'<h4>{offer["title"]}</h4><div class="offer-company">{offer["company"]}</div>'
        f'<div class="offer-meta">{offer["city"]} · {offer["field"]} · Source : {offer["source"]}</div>'
        f'<div class="offer-meta">{offer["summary"]}</div></div>',
        unsafe_allow_html=True,
    )
    action, favorite = st.columns([3, 1])
    if offer.get("url"):
        action.link_button("Voir l’annonce ↗", offer["url"], use_container_width=True)
    else:
        action.caption("Aucun lien de candidature n’a été fourni pour cette offre.")
    if show_favorite:
        saved = offer["id"] in st.session_state.favorites
        label = "♥ Retirer" if saved else "♡ Favori"
        if favorite.button(label, key=f"favorite-{offer['id']}", use_container_width=True):
            if saved:
                st.session_state.favorites.remove(offer["id"])
            else:
                st.session_state.favorites.add(offer["id"])
            st.rerun()


def filter_offers(offers: list[dict[str, Any]], city: str, field: str, offer_type: str, keyword: str) -> list[dict[str, Any]]:
    needle = keyword.strip().lower()
    filtered: list[dict[str, Any]] = []
    for offer in offers:
        haystack = " ".join(str(offer.get(key, "")) for key in ("title", "company", "field", "summary")).lower()
        city_ok = offer["city"].lower() == city.lower()
        field_ok = field == "Toutes les filières" or field.lower() in offer["field"].lower()
        type_ok = offer_type == "Tous" or offer["offer_type"] == offer_type.lower()
        if city_ok and field_ok and type_ok and (not needle or needle in haystack):
            filtered.append(offer)
    return filtered


def dashboard(offers: list[dict[str, Any]], companies: list[dict[str, Any]], db_error: str | None) -> None:
    st.markdown(
        """
        <div class="hero"><div class="eyebrow">● La prochaine étape commence à Marrakech</div>
        <h1>Trouvez votre stage idéal<br>à Marrakech !</h1>
        <p>Explorez les opportunités, découvrez les entreprises et avancez vers votre avenir.</p></div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    filters = st.columns([1.2, 1.05, 1.25, 1])
    selected_type = filters[0].selectbox("Type", ["Tous", "Stage", "Emploi"], label_visibility="collapsed")
    selected_city = filters[1].selectbox("Ville", CITIES, label_visibility="collapsed")
    selected_field = filters[2].selectbox("Filière", FIELDS, label_visibility="collapsed")
    keyword = filters[3].text_input("Mot-clé", placeholder="Rechercher", label_visibility="collapsed")
    filtered = filter_offers(offers, selected_city, selected_field, selected_type, keyword)

    stages = sum(offer["offer_type"] == "stage" for offer in filtered)
    jobs = sum(offer["offer_type"] == "emploi" for offer in filtered)
    kpi = st.columns(4)
    metric("Entreprises", len(companies), "depuis MySQL" if mysql_configured() else "annuaire à configurer")
    metric("Offres de stage", stages, "sources web et MySQL")
    metric("Offres d’emploi", jobs, "sources web et MySQL")
    metric("Candidatures", 0, "CV non stockés dans la démo")

    if db_error:
        st.warning(db_error)
    elif not mysql_configured():
        st.info("Mode web : ajoute les secrets MySQL sur Streamlit Cloud pour afficher les données de ta base.")

    map_col, offers_col = st.columns([1.5, 1])
    with map_col:
        st.markdown('<div class="section-card"><h3>⌖ Carte des opportunités</h3><p>La carte se centre sur la ville choisie. Les entreprises MySQL avec coordonnées s’y ajoutent.</p></div>', unsafe_allow_html=True)
        coordinates = {"Marrakech": (31.6295, -7.9811), "Casablanca": (33.5731, -7.5898), "Rabat": (34.0209, -6.8416), "Tanger": (35.7595, -5.8340), "Agadir": (30.4278, -9.5981), "Fès": (34.0331, -5.0003)}
        locations = [{"lat": coordinates[selected_city][0], "lon": coordinates[selected_city][1]}]
        for company in companies:
            try:
                if company.get("latitude") is not None and company.get("longitude") is not None:
                    locations.append({"lat": float(company["latitude"]), "lon": float(company["longitude"])})
            except (TypeError, ValueError):
                continue
        st.map(pd.DataFrame(locations), latitude="lat", longitude="lon", zoom=11, use_container_width=True, height=330)
    with offers_col:
        st.markdown('<div class="section-card"><h3>✦ Offres récentes</h3><p>Résultats correspondant aux filtres actifs.</p></div>', unsafe_allow_html=True)
        if filtered:
            for offer in filtered[:2]:
                offer_card(offer)
        else:
            st.info("Aucune offre ne correspond aux filtres. Essaie une autre filière ou la vue “Tous”.")

    st.markdown('<div class="section-card"><h3>Autres sources</h3><p>Les annonces ouvrent le site qui les publie. Vérifie qu’elles sont toujours ouvertes avant de postuler.</p></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    left.link_button("Rechercher sur LinkedIn ↗", f"https://www.linkedin.com/jobs/search/?keywords={selected_field if selected_field != 'Toutes les filières' else 'stage'}&location={selected_city}%2C%20Morocco", use_container_width=True)
    right.link_button("Rechercher sur Indeed ↗", f"https://ma.indeed.com/jobs?q={selected_field if selected_field != 'Toutes les filières' else 'stage'}&l={selected_city}", use_container_width=True)


def offers_page(offers: list[dict[str, Any]]) -> None:
    st.title("Offres de stage et d’emploi")
    st.caption("Filtre les opportunités et ouvre l’annonce sur sa source officielle.")
    a, b, c, d = st.columns(4)
    city = a.selectbox("Ville", CITIES, key="offers-city")
    field = b.selectbox("Filière", FIELDS, key="offers-field")
    offer_type = c.selectbox("Type", ["Tous", "Stage", "Emploi"], key="offers-type")
    keyword = d.text_input("Mot-clé", key="offers-keyword")
    visible = filter_offers(offers, city, field, offer_type, keyword)
    st.caption(f"{len(visible)} résultat(s) affiché(s).")
    for offer in visible:
        offer_card(offer)
    if not visible:
        st.info("Aucun résultat pour ces critères.")


def companies_page(companies: list[dict[str, Any]]) -> None:
    st.title("Entreprises")
    st.caption("Annuaire alimenté par la base MySQL de l’application quand elle est configurée.")
    if not companies:
        st.info("Aucune entreprise MySQL n’est encore disponible sur ce déploiement. Configure les secrets MySQL ou ajoute des entreprises dans la version FastAPI.")
        return
    city = st.selectbox("Ville", CITIES, key="companies-city")
    keyword = st.text_input("Rechercher une entreprise ou un secteur", key="companies-keyword")
    needle = keyword.strip().lower()
    visible = [company for company in companies if company.get("city", "").lower() == city.lower() and (not needle or needle in " ".join(str(company.get(k, "")) for k in ("name", "sector", "description")).lower())]
    for company in visible:
        with st.container(border=True):
            st.subheader(company["name"])
            st.caption(f"{company.get('sector') or 'Secteur non renseigné'} · {company.get('city')}")
            if company.get("address"):
                st.write(company["address"])
            if company.get("website"):
                st.link_button("Site web ↗", company["website"])
    if not visible:
        st.info("Aucune entreprise ne correspond à la recherche.")


def map_page(companies: list[dict[str, Any]]) -> None:
    st.title("Carte interactive")
    st.caption("Visualise les entreprises de la base qui possèdent des coordonnées GPS.")
    city = st.selectbox("Ville", CITIES, key="map-city")
    coordinates = {
        "Marrakech": (31.6295, -7.9811), "Casablanca": (33.5731, -7.5898),
        "Rabat": (34.0209, -6.8416), "Tanger": (35.7595, -5.8340),
        "Agadir": (30.4278, -9.5981), "Fès": (34.0331, -5.0003),
    }
    locations = [{"lat": coordinates[city][0], "lon": coordinates[city][1]}]
    mapped_companies: list[dict[str, Any]] = []
    for company in companies:
        try:
            if company.get("city", "").lower() == city.lower() and company.get("latitude") is not None and company.get("longitude") is not None:
                locations.append({"lat": float(company["latitude"]), "lon": float(company["longitude"])})
                mapped_companies.append(company)
        except (TypeError, ValueError):
            continue
    st.map(pd.DataFrame(locations), latitude="lat", longitude="lon", zoom=11, use_container_width=True, height=520)
    if mapped_companies:
        st.caption(f"{len(mapped_companies)} entreprise(s) de la base sont positionnées sur cette carte.")
    else:
        st.info("Aucune entreprise géolocalisée n’est disponible pour cette ville. Ajoute latitude et longitude dans MySQL pour la faire apparaître.")


def favorites_page(all_offers: list[dict[str, Any]]) -> None:
    st.title("Mes favoris")
    saved = [offer for offer in all_offers if offer["id"] in st.session_state.favorites]
    if not saved:
        st.info("Aucun favori pour le moment. Utilise le bouton ♡ sur une offre pour la conserver dans cette session.")
        return
    st.caption(f"{len(saved)} offre(s) sauvegardée(s) dans cette session.")
    for offer in saved:
        offer_card(offer)


def profile_page() -> None:
    st.title("Mon profil et candidature")
    st.caption("Les champs restent dans la session de navigation. Cette version Streamlit ne reçoit ni ne stocke les CV.")
    profile = st.session_state.profile
    with st.form("profile-form"):
        left, right = st.columns(2)
        name = left.text_input("Nom complet", value=profile["name"])
        email = right.text_input("E-mail", value=profile["email"])
        city = left.selectbox("Ville", CITIES, index=CITIES.index(profile["city"]) if profile["city"] in CITIES else 0)
        field = right.selectbox("Filière", FIELDS[1:], index=max(0, FIELDS[1:].index(profile["field"]) if profile["field"] in FIELDS[1:] else 0))
        skills = st.text_area("Compétences", value=profile["skills"], placeholder="Ex. React, Python, SQL")
        submitted = st.form_submit_button("Enregistrer mon profil")
    if submitted:
        st.session_state.profile = {"name": name, "email": email, "city": city, "field": field, "skills": skills}
        st.success("Profil enregistré pour cette session.")

    st.divider()
    st.subheader("Candidater à une offre")
    st.info("Cette version Streamlit ne reçoit ni ne stocke les CV. Pour postuler, ouvre le lien officiel affiché sur chaque offre.")


def analytics_page(offers: list[dict[str, Any]], companies: list[dict[str, Any]]) -> None:
    st.title("Analyses et statistiques")
    st.caption("Les données web et les données MySQL sont distinguées dans les libellés.")
    stages = sum(offer["offer_type"] == "stage" for offer in offers)
    jobs = sum(offer["offer_type"] == "emploi" for offer in offers)
    cols = st.columns(3)
    metric("Offres visibles", len(offers), "web + MySQL")
    metric("Stages", stages, "selon les filtres et sources")
    metric("Emplois", jobs, "selon les filtres et sources")
    if offers:
        frame = pd.DataFrame(offers)
        st.subheader("Répartition par filière")
        st.bar_chart(frame["field"].value_counts())
    st.subheader("État de la base")
    st.write(f"{len(companies)} entreprise(s) chargée(s) depuis MySQL.")


def guide_page() -> None:
    st.title("Guide du site")
    st.markdown(
        """
        1. Sélectionne la ville, la filière et le type d’opportunité.
        2. Consulte les offres et ouvre le portail qui les publie pour postuler.
        3. Ajoute les opportunités utiles aux favoris pendant ta session.
        4. Complète ton profil pour mieux préparer ta recherche.

        Les annonces externes restent liées à leur source. Vérifie toujours leur disponibilité avant de candidater.
        """
    )


def main() -> None:
    initialize_state()
    apply_css()
    mysql_offers, companies, db_error = load_mysql_data()
    all_offers = [*mysql_offers, *EXTERNAL_OFFERS]

    with st.sidebar:
        st.markdown("## 🎓 Search Stage\n#### Marrakech")
        page = st.radio(
            "Navigation",
            ["Accueil", "Offres de stage et d’emploi", "Entreprises", "Carte interactive", "Analyses & stats", "Mon profil", "Mes favoris", "Guide du site"],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("● API MySQL connectée" if mysql_configured() and not db_error else "● Mode web autonome")
        st.markdown("<br><br>**Boostez votre carrière dès aujourd’hui !**", unsafe_allow_html=True)

    if page == "Accueil":
        dashboard(all_offers, companies, db_error)
    elif page == "Offres de stage et d’emploi":
        offers_page(all_offers)
    elif page == "Entreprises":
        companies_page(companies)
    elif page == "Carte interactive":
        map_page(companies)
    elif page == "Analyses & stats":
        analytics_page(all_offers, companies)
    elif page == "Mon profil":
        profile_page()
    elif page == "Mes favoris":
        favorites_page(all_offers)
    else:
        guide_page()


if __name__ == "__main__":
    main()
