def get_ru_header(year, date, issue_number, article_number):
    return f'''+++

categories="article"
date="{date}T00:{(30-article_number):02d}:00+03:00"
issue="{year}-{issue_number:02d}"
issue_name="{year} - №{issue_number:02d}"
number="{article_number:02d}"
file="https://static.nuclear-power-engineering.ru/articles/{year}/{issue_number:02d}/{article_number:02d}.pdf"
doi="https://doi.org/10.26583/npe.{year}.{issue_number}.{article_number:02d}"
udc=""
first_page=""
last_page=""
rubric = ""
rubric_name = ""
title=""
authors=[""]
tags=[""]

+++



### Ссылки


'''

def get_en_header(year, date, issue_number, article_number):
    return f'''+++

categories="article"
outputs=["HTML", "DOI"]
date="{date}T00:{(30-article_number):02d}:00+03:00"
issue="{year}-{issue_number:02d}"
issue_name="{year} - #{issue_number:02d}"
issue_id="{issue_number}"
number="{article_number:02d}"
file="https://static.nuclear-power-engineering.ru/articles/{year}/{issue_number:02d}/{article_number:02d}.pdf"
doi="https://doi.org/10.26583/npe.{year}.{issue_number}.{article_number:02d}"
udc=""
first_page=""
last_page=""
rubric=""
rubric_name=""
title=""
original_title=""
authors=[""]
tags=[""]

+++



### References


'''

def get_ru_path(year, issue_number, article_number):
    return f"content/article/{year}/{issue_number:02d}/{article_number:02d}.md"

def get_en_path(year, issue_number, article_number):
    return f"content_en/article/{year}/{issue_number:02d}/{article_number:02d}.md"

def write_string_to_file(filename, string):
    with open(filename, 'w') as file:
        file.write(string)


def main():
    year=2024
    date=f"{year}-06-05"
    issue_number=2
    for article in range(1, 17):
        print(get_ru_path(year, issue_number, article))
        write_string_to_file(
            get_ru_path(year, issue_number, article),
            get_ru_header(year, date, issue_number, article))
        print(get_en_path(year, issue_number, article))
        write_string_to_file(
            get_en_path(year, issue_number, article),
            get_en_header(year, date, issue_number, article))


if __name__ == '__main__':
    main()
