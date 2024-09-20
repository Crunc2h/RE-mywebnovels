from cout.native.common import standardize_str


def get_next_page(response, website_base_link):

    next_page_relative_href = response.css(
        ".PagedList-skipToNext > a:nth-child(1)::attr(href)"
    ).get()
    if next_page_relative_href != None:
        if "https://" in next_page_relative_href:
            return next_page_relative_href
        else:
            return website_base_link + next_page_relative_href
    return None


def get_max_page(response, website_base_link):
    skip_last_link = response.css(
        ".PagedList-skipToLast > a:nth-child(1)::attr(href)"
    ).get()
    if skip_last_link is None:
        if (
            response.css(".PagedList-skipToNext > a:nth-child(1)::attr(href)").get()
            is not None
        ):
            skip_last_link = response.css(
                ".pagination li:nth-last-child(2) > a:nth-child(1)::attr(href)"
            ).get()
        else:
            skip_last_link = response.url
    if skip_last_link != None:
        if "https://" in skip_last_link:
            return skip_last_link
        else:
            return website_base_link + skip_last_link
    return None


def get_chapters_index_page(response, website_base_link):
    chapters_index_page_relative_href = response.css(
        "a.grdbtn:nth-child(1)::attr(href)"
    ).get()
    if chapters_index_page_relative_href != None:
        return website_base_link + chapters_index_page_relative_href
    return None


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
