from django.dispatch import Signal

novel_link_page_scraped = Signal()
novel_page_scraped = Signal()
chapter_link_page_scraped = Signal()
chapter_page_scraped = Signal()

novel_link_page_processed = Signal()
novel_page_processed = Signal()
chapter_page_processed = Signal()
chapter_link_page_processed = Signal()

new_novel_links_added = Signal()
new_chapter_links_added = Signal()
new_novels_added = Signal()
new_chapters_added = Signal()

scraper_error = Signal()
bad_content_error = Signal()
critical_error = Signal()

process_finish = Signal()
