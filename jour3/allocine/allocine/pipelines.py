from itemadapter import ItemAdapter

class CleanPipeline:
    """Nettoie les espaces superflus et formate les notes en float."""
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Nettoyage des textes
        for field in ["titre", "realisateur", "annee"]:
            if adapter.get(field):
                adapter[field] = str(adapter[field]).strip()

        # Nettoyage et typage des notes
        for field in ["note_presse", "note_spectateurs"]:
            raw_val = adapter.get(field)
            if raw_val:
                try:
                    clean_str = str(raw_val).replace(",", ".").strip()
                    adapter[field] = float(clean_str)
                except (ValueError, TypeError):
                    adapter[field] = None
            else:
                adapter[field] = None

        return item