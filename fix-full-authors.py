
import os

'''
 Return a list of *.toml files from data_en/authors folder
'''
def get_author_profiles():
    return [f for f in os.listdir(os.path.join('data_en', 'authors'))]

'''
Read income toml file and find a line starting with 'full_name' key.
Remove "" from the beginning of the string
'''
def get_full_name(file):
    with open('data_en/authors/' + file) as f:
        for line in f.readlines():
            if 'full_name' in line and '=' in line:
                return line[line.index('=')+1:].replace("\"", "").replace("\n", "")
            
'''
String consists of 3 words.
If the second word is a single capital letter with dot,
move the last word to the beginning of the string.
Otherwise, return the string as it is.

For example:
'Tatiana A. Polyakova' -> 'Polyakova Tatiana A.'
'Petrozhitsky Aleksey V.' -> 'Petrozhitsky Aleksey V.'
'''
def rearrange_full_name(full_name):
    if len(full_name.split(' ')) != 3:
        return (full_name, False)
    first, middle, last = full_name.split(' ')
    if middle[0].isupper() and middle[1] == '.':
        new_name = f"{last} {first} {middle}"
        print(f'{full_name} -> {new_name}')
        return (new_name, True)
    else: 
        return (full_name, False)
    



def replace_full_names(profile):
    lines = []
    with open('data_en/authors/' + profile) as f:
        lines = f.readlines()
    
    need_to_replace = False
    for i, line in enumerate(lines):
        if 'full_name' in line:
            full_name = line[line.index('=')+1:].replace("\"", "").replace("\n", "")
            expected, need_to_replace = rearrange_full_name(full_name)
            if need_to_replace:
                lines[i] = f'full_name="{expected}"\n'
    
    if need_to_replace:
        with open('data_en/authors/' + profile, 'w') as f:
            for line in lines:
                print(line)
                f.write(line)

def main():
    for profile in get_author_profiles():
        replace_full_names(profile)


if __name__ == '__main__':
    main()
