from hermes import master_settings

class App:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.scraper_objs = settings.scraper_objs
        self.storage_obj = settings.storage_obj
        self.notifier_objs = settings.notifier_objs


    def runbot(self, notify: bool=None) -> None:
        if not notify:
            NOTIFY = self.settings.NOTIFY
        else:
            NOTIFY = notify

        MAX_ARTICLES = self.settings.MAX_ARTICLES


        with self.storage_obj as s:
            s.create_tables_if_not_exist()
            s.update_or_create_scrapers(self.scraper_objs)

        new_articles = []

        for scraper in self.scraper_objs:

            html = scraper.get_html()
            data = scraper.get_data_from_html(html, MAX_ARTICLES)
            
            with self.storage_obj as s:
                s.store(data, scraper)


        with self.storage_obj as s:
            new_articles = s.get_new()

        
        if NOTIFY and len(new_articles) > 0:
            for notifier in self.notifier_objs:
                notifier.read_receivers_from_json()
                notifier.set_articles(new_articles)
                notifier.notify()


        with self.storage_obj as s:
            s.mark_old_all()


    def deletedb(self) -> None:
        with self.storage_obj as s:
            s.delete_db(perform=True)

    def getallrowsdb(self) -> None:
        row_lists = []
        with self.storage_obj as s:
            row_lists = s.get_all_rows()

        for rows in row_lists:
            if len(rows) < 1:
                continue

            print(rows[0].keys())
            for row in rows:
                print([value for value in row])
            print("="*50)

    def getarticlesdb(self) -> None:
        with self.storage_obj as s:
            articles = s.get_all_rows_in_table(s.tables["articles"])

        if len(articles) < 1:
            print("No articles found")
            return

        print(articles[0].keys())
        for article in articles:
            print([value for value in article])

    def deletearticlesdb(self) -> None:
        with self.storage_obj as s:
            articles = s.delete_table(s.tables["articles"])

    def deletescrapersdb(self) -> None:
        with self.storage_obj as s:
            articles = s.delete_table(s.tables["scrapers"])

    def info(self) -> None:
        print(f"You are running Hermes Framework version: {master_settings.VERSION}")
        print(f"Source: {master_settings.GITHUB_LINK}")
        print(f"Made by: {master_settings.AUTHOR}")
