# Sources de données — InternMatch Streamlit

## Annuaire d’entreprises

- **OpenStreetMap / Overpass API** : recherche à la demande d’établissements nommés autour de la ville choisie. Le résultat est limité à 60 éléments par recherche, n’est pas enregistré dans MySQL et reste attribué à OpenStreetMap.
- **MySQL InternMatch** : catalogue facultatif connecté par les secrets Streamlit. Il est prioritaire lorsqu’un même nom d’entreprise existe dans MySQL.
- **Entreprises citées dans les offres** : entreprises affichées dans l’annuaire car une offre liée à une source publique les mentionne.

## Offres externes

Les liens dans l’application renvoient vers le portail qui publie l’annonce. Les annonces suivantes ont été vérifiées le 9 novembre 2026 avant leur ajout : JobSquare, Stagiaires.ma, Postule.ma et PostulerCv. Leur statut peut changer après cette date : l’utilisateur doit le vérifier sur la source avant de postuler.

InternMatch ne collecte pas automatiquement les annonces depuis LinkedIn, Indeed ou d’autres plateformes. Les boutons de recherche ouvrent leurs propres résultats.
