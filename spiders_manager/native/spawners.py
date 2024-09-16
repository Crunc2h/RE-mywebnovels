import os


def spawn_novel_links_spider(website_name):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_novel_link_pages_spider '{website_name}'; exec bash'"
    )


def spawn_novel_page_spider(website_name, novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_novel_page_spider '{website_name}' '{novel_link}'; exec bash'"
    )


def spawn_chapter_links_spider(website_name, novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_chapter_link_pages_spider '{website_name}' '{novel_link}'; exec bash'"
    )


def spawn_chapter_pages_spider(website_name, novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py spawn_chapter_pages_spider '{website_name}' '{novel_link}'; exec bash'"
    )


def start_novel_update(website_name, novel_link):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py start_novel_update '{website_name}' {novel_link}; exec bash'"
    )


def start_website_update(website_name, max_allowed_processes):
    os.system(
        "gnome-terminal -- "
        + f"bash -c 'source .re_venv/bin/activate; python3 manage.py start_website_update '{website_name}' {max_allowed_processes}; exec bash'"
    )
