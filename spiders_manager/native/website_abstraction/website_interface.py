import novels_storage.models as ns_models
import webnovelpub
from cout.native.common import standardize_str
import webnovelpub.common
import webnovelpub.processors


class WebsiteInterface:
    def __init__(self, website_name) -> None:
        exists = ns_models.Website.objects.get(name=standardize_str(website_name))
        if website_name == "webnovelpub":
            self.novel_link_page_processor = (
                webnovelpub.processors.novel_link_page_processor
            )
            self.chapter_link_page_processor = (
                webnovelpub.processors.chapter_link_page_processor
            )
            self.novel_page_processor = webnovelpub.processors.novel_page_processor
            self.chapter_page_processor = webnovelpub.processors.chapter_page_processor
            self.get_next_page = webnovelpub.common.get_next_page
            self.get_max_page = webnovelpub.common.get_max_page
            self.get_chapters_index_page = webnovelpub.common.get_chapters_index_page
