import novels_storage.models as ns_models
import webnovelpub.processors as webnovelpub
from cout.native.common import standardize_str


class ProcessorInterface:
    def __init__(self, website_name) -> None:
        exists = ns_models.Website.objects.get(name=standardize_str(website_name))
        if website_name == "webnovelpub":
            self.novel_link_page_processor = webnovelpub.novel_link_page_processor
            self.chapter_link_page_processor = webnovelpub.chapter_link_page_processor
            self.novel_page_processor = webnovelpub.novel_page_processor
            self.chapter_page_processor = webnovelpub.chapter_page_processor
