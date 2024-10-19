raw_work_ru = '''
ФГБУ ГНЦ РФ ФМБЦ им. А.И. Бурназяна ФМБА России,
'''

raw_author_ru = '''
Еремина Наталья Александровна, младший научный сотрудник,
E-mail: eremina-na@mail.ru
'''

raw_work_en = '''
State Research Center – Burnasyan Federal Medical Biophysical Center of the Federal Medical Biological Agency
(SRC-FMBC),
'''

raw_author_en = '''
Natalia A. Eremina, Junior Researcher,
E-mail: eremina-na@mail.ru
'''

# Get the surname.
# Surname is 3rd word in the raw string without commas.
def get_en_surname():
    return raw_author_en.split()[2].replace(',', '')

# Get the name.
# Name is first word in the raw.
def get_en_name():
    return raw_author_en.split()[0]

# Get the fathers name.
# Fathers name is second word in the raw string.
def get_en_fathers_name():
    return raw_author_en.split()[1]

# Get the initials.
# Initials are first letters of name and fathers name.
def get_en_initials():
    return get_en_name()[0] + '.' + \
           get_en_fathers_name()[0] + '.'

# Get the surname.
# Surname is 1st word in the raw.
def get_ru_surname():
    return raw_author_ru.split()[0]

# Get the name.
# Name is second word in the raw.
def get_ru_name():
    return raw_author_ru.split()[1]

# Get the fathers name.
# Fathers name is second word in the raw string without ending comma.
def get_ru_fathers_name():
    return raw_author_ru.split()[2].replace(',', '')

# Get the initials.
# Initials are first letters of name and fathers name.
def get_ru_initials():
    return get_ru_name()[0] + '.' + \
           get_ru_fathers_name()[0] + '.'

# Get the term.
# Term consists of surname and 
# first letters of name and fathers name.
def get_term():
    return get_en_surname() + \
           get_en_name()[0].upper() + \
           get_en_fathers_name()[0].upper()

# Trim newlines and ending commas from the string
def trim_work(raw):
    return raw[:-1].replace('\n', '').removesuffix(',')

# Get regals.
# Regals are starting from the 4th word
# till the E-mail word without ending comma.
def get_regals(raw):
    start = raw.find(',') + 2
    stop = raw.find('E-mail')
    return trim_work(raw[start:stop])

# Get email.
# Email is starting from the E-mail word till the end of string.
def get_email(raw):
    prefix = 'E-mail: '
    prefix_index = raw.find(prefix)
    if prefix_index == -1:
        return ""
    start = prefix_index + len(prefix)
    return f'email="{trim_work(raw[start:])}"'

def get_ru_filename():
    return f'data/authors/{get_term()}.toml'

def get_en_filename():
    return f'data_en/authors/{get_term()}.toml'

author_ru = f'''term="{get_term()}"
name="{get_ru_initials()} {get_ru_surname()}"
work="{trim_work(raw_work_ru)}"
full_name="{get_ru_surname()} {get_ru_name()} {get_ru_fathers_name()}"
regals="{get_regals(raw_author_ru)}"
{get_email(raw_author_ru)}
'''

author_en = f'''term="{get_term()}"
name="{get_en_surname()} {get_en_initials()}"
work="{trim_work(raw_work_en)}"
full_name="{get_en_surname()} {get_en_name()} {get_en_fathers_name()}"
regals="{get_regals(raw_author_en)}"
{get_email(raw_author_en)}
'''

def write_string_to_file(filename, string):
    with open(filename, 'w') as file:
        file.write(string)

def main():
    print(get_ru_filename())
    print(author_ru)
    write_string_to_file(get_ru_filename(), author_ru)
    print(get_ru_filename())
    print(author_en)
    write_string_to_file(get_en_filename(), author_en)

if __name__ == "__main__":
    main()
