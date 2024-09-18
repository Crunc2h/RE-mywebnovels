from cout.native.common import standardize_str


def get_next_page(response):
    return response.css(".PagedList-skipToNext > a:nth-child(1)::attr(href)").get()


def get_max_page(response):
    skip_last_link = response.css(
        ".PagedList-skipToLast > a:nth-child(1)::attr(href)"
    ).get()
    if skip_last_link != None:
        return skip_last_link.split("page=")[1]
    return None


def get_chapters_index_page(response):
    return response.css("a.grdbtn:nth-child(1)::attr(href)").get()


def get_chapter_number_from_title(title):
    return standardize_str(title.split("Chapter ")[1].split(":")[0])


def get_novel_slug(url):
    return standardize_str(url.split("novel/")[1])


def get_novel_stub(url):
    return url.split("novel/")[0] + "novel/"


def get_novel_name_from_slug(slug_name):
    return standardize_str(" ".join(slug_name.split("-")))


def get_novel_name_from_url(url):
    return standardize_str(get_novel_name_from_slug(get_novel_slug(url)))


def check_is_all_alpha(str):
    return len(list(filter(lambda letter: letter.isalpha(), str))) == len(str)
