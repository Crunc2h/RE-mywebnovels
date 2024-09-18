import links_manager.models as lm_models
import novels_storage.models as ns_models
import spiders_manager.native.website_abstraction.webnovelpub.common as common
from cout.native.common import standardize_str
from datetime import datetime


def novel_link_page_processor(
    soup, website_link_object, get_novel_name_from_url=common.get_novel_name_from_url
):
    novel_links_in_page = []
    bad_content_in_page = False

    for novel_item in soup.find_all(class_="novel-item"):
        link_element = novel_item.find("a")
        if link_element != None:
            if not common.check_is_all_alpha(
                common.get_novel_slug(link_element["href"]).split("-")[-1]
            ):
                slug = [
                    common.get_novel_slug(link_element["href"]).split("-")[i]
                    for i in range(
                        0, len(common.get_novel_slug(link_element["href"]).split("-"))
                    )
                    if i
                    != len(common.get_novel_slug(link_element["href"]).split("-")) - 1
                ]
                stub = common.get_novel_stub(link_element["href"])
                href = stub + "-".join(slug)
            else:
                href = link_element["href"]
            novel_links_in_page.append(
                lm_models.NovelLink(
                    website_link=website_link_object,
                    link=website_link_object.base_link + href,
                    name=get_novel_name_from_url(href),
                )
            )
        else:
            bad_content_in_page = True
    return novel_links_in_page, bad_content_in_page


def chapter_link_page_processor(soup, novel_link_object):
    chapter_links_in_page = []
    bad_content_in_page = False

    chapter_list = soup.select_one(".chapter-list")
    if not chapter_list:
        bad_content_in_page = True
        return chapter_links_in_page, bad_content_in_page

    for chapter_item in chapter_list.find_all("li"):
        link_element = chapter_item.find("a")
        name_element = chapter_item.find(class_="chapter-title")
        if link_element != None and name_element != None:
            chapter_links_in_page.append(
                lm_models.ChapterLink(
                    novel_link=novel_link_object,
                    name=standardize_str(name_element.text),
                    link=novel_link_object.website_link.base_link
                    + link_element["href"],
                )
            )
        else:
            bad_content_in_page = True
    return chapter_links_in_page, bad_content_in_page


def chapter_page_processor(
    soup,
    novel_object,
    get_chapter_number_from_title=common.get_chapter_number_from_title,
):
    name_element = soup.select_one(".chapter-title")
    date_published_element = soup.select_one(".titles > meta:nth-child(1)")
    chapter_container_element = soup.find(id="chapter-container")
    if (
        name_element != None
        and date_published_element != None
        and chapter_container_element != None
    ):
        name = standardize_str(name_element.text)
        number = get_chapter_number_from_title(name_element.text)
        date_published = datetime.strptime(
            date_published_element["content"],
            "%Y-%m-%dT%H:%M:%S",
        )
        chapter_text = "\n".join(
            [
                paragraph_element.text
                for paragraph_element in chapter_container_element.find_all("p")
            ]
        )
        return ns_models.Chapter(
            name=name,
            number=number,
            date_published=date_published,
            novel=novel_object,
            text=chapter_text,
        )
    return None


def novel_page_processor(soup, novel_name):
    author_element = soup.select_one("a.property-item:nth-child(2) > span:nth-child(1)")
    summary_element = soup.select_one("div.content")
    completion_status_element = soup.select_one(".completed")
    if completion_status_element is None:
        completion_status_element = soup.select_one(".ongoing")
    categories_element = soup.select_one(".categories")
    tags_element = soup.select_one(".tags")

    if (
        author_element
        and summary_element
        and completion_status_element
        and categories_element
        and tags_element
    ):
        name = novel_name
        author = ns_models.get_or_create_enum_model_from_str(
            standardize_str(author_element.text),
            ns_models.NovelAuthor,
        )
        summary = "\n".join(
            [
                paragraph.text
                for paragraph in soup.select_one("div.content").find_all("p")
            ]
        )
        completion_status = ns_models.get_or_create_enum_model_from_str(
            standardize_str(completion_status_element.text),
            ns_models.NovelCompletionStatus,
        )
        new_novel = ns_models.Novel(
            name=name,
            summary=summary,
            author=author,
            completion_status=completion_status,
        )
        categories = [
            ns_models.get_or_create_enum_model_from_str(
                standardize_str(category.text), ns_models.NovelCategory
            )
            for category in categories_element.find_all("li")
        ]
        tags = [
            ns_models.get_or_create_enum_model_from_str(
                standardize_str(tag.text), ns_models.NovelTag
            )
            for tag in tags_element.find_all("li")
        ]

        m2m = {
            "categories": categories,
            "tags": tags,
        }
        return new_novel, m2m
    return None
