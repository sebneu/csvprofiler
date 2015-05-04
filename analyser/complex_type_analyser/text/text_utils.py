# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
Created on May 19, 2014

@author: max
'''

import re
import unittest
import unicodedata
import urlparse

SERVER_URL = 'http://spotlight.dbpedia.org/rest/annotate'
# 'http://localhost/rest/annotate'

date_regex = '^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'
date_pattern = re.compile(date_regex)

date_regex2 = '^[1|2][0-9][0-9][0-9][\/-]?[0-3][0-9][\/-]?[0-3][0-9]$'
date_pattern2 = re.compile(date_regex2)

date_regex3 = '((0[1-9])|(1[0-2]))[\/-]((0[1-9])|(1[0-9])|(2[0-9])|(3[0-1]))[\/-](\d{4})'
date_pattern3 = re.compile(date_regex3)

date_regex4 = '^([0-9]?[0-9][\.\/-])?([0-3]?[0-9][\.\/-])\s?[1-9][0-9]([0-9][0-9])?$'
date_pattern4 = re.compile(date_regex4)

email_regex = '[a-zA-Z0-9_\.\+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-\.]+'
email_pattern = re.compile(email_regex)

phone_regex = '^\(?\+?\d+\)?(\s?\d+)+$'
phone_pattern = re.compile(phone_regex)

address_regex = ''
address_pattern = re.compile(address_regex)

url_regex = 'https?\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}'
url_pattern = re.compile(url_regex)

places = ['street', 'strasse', 'rue', 'str', 'str.', 'platz', 'allee', 'gasse', 'g.', 'blvd', 'ave', 'road']
special_symbols = ['+', ' ', ';', '[', '/', ']', '\\', '-']
commas = [',', '.']
resource = ['://', 'www.', '.jpg', '.png', '.gif', '.html', '.htm', '.mp3', '.doc', '.pdf', '.ps', '.docx']
yes_no = ['yes', 'no', 'y', 'n', 'j', 'ja', 'nein', 'si', 'oui', 'da', 'njet']
# units =

#camelCase regex
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

lookup = []

def contains_number(inputString):
    return any(char.isdigit() for char in inputString)

def contains_alpha(inputString):
    return any(char.isalpha() for char in inputString)

def contains_special(inputString):
    return any(char in special_symbols for char in inputString)

def contains_commas(inputString):
    return any(char in commas for char in inputString)

def contains_ampersand(inputString):
    return any(char == '@' for char in inputString)

def contains_unit_symbol(inputString):
    return any(char in [u'%', u'$', u'€'] for char in inputString)

def contains_resource(inputString):
    for item in resource:
        if item in inputString:
            return True
    return False



def is_yes_no(cell):
    return cell in yes_no

def is_alpha(cell):
    for c in cell:
        if not c.isalpha() and c <> ' ':
            return False
    return True

def is_alphanum(cell):
    is_digit = False
    is_alpha = False
    for c in cell:
        if c.isalpha():
            is_alpha = True
        elif c.isdigit():
            is_digit = True
    return is_digit and is_alpha

def is_street(cell):
    if address_pattern.match(cell):
        return True
    for place in places:
        if cell.contains(place):
            return True
    return False

def is_phone(cell):
    return phone_pattern.match(cell)

def is_email(cell):
    return email_pattern.match(cell)

def is_url(cell):
    return url_pattern.match(cell)

def is_digitsep(cell):
    is_digit = False
    is_sep = False
    separators = [':', ',', '-', '/']
    for c in cell:
        if c in separators:
            is_sep = True
        elif c.isdigit():
            is_digit = True
    return is_digit and is_sep

def is_date(cell):
    if date_pattern.match(cell):
        return True
    if date_pattern2.match(cell):
        return True
    if date_pattern3.match(cell):
        return True
    if date_pattern4.match(cell):
        return True
    return False

def is_year(cell):
    try:
        int_val = int(cell)
        if int_val >= 1400 and int_val <= 2100:
            return True
    except Exception:
        return False

def is_year_month(cell):
    try:
        int_val = int(cell)
        if int_val >= 197000 and int_val < 210000:
            return True
    except Exception:
        return False

def is_numeric(text):
    pattern = re.compile("/^\d*\.?\d*$/")
    return re.match(pattern, text)

def is_categorial(text):
    return text.isnumeric()

def list_to_set(list):
    seen = set()
    seen_add = seen.add
    return [ x for x in list if not (x in seen or seen_add(x))]

def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode_escape')

def file_to_ascii(filename, num_lines=-1):
    lines = []
    with open(filename, 'r+') as f:
        line_num = 1
        for line in f:
            if num_lines > -1 and line_num > num_lines:
                break
            lines.append(removeNonAscii(line))
        text = '\n'.join(lines)
        f.seek(0)
        f.write(text)
        f.truncate()
        f.close()

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')

def to_unicode(value):
    if type(value) is not str and type(value) is not unicode:
        return str(value)
    try:
        value = value.encode('utf8', 'replace')
        str(value)
        return value
    except UnicodeEncodeError as e:
        print type(e), e.encoding
        value = value.decode('utf-8').encode("utf-8")
        # value = value.encode('ascii', 'ignore').encode('utf8')
        str(value)
        return value
    except UnicodeDecodeError as e:
        print type(e), e.encoding, e
        # value = unicode(value)
        # iso-8859-1
        value = value.decode('utf8', 'replace').encode("utf-8")
        str(value)
        return value

def uncamel(text):
    s1 = first_cap_re.sub(r'\1_\2', text)
    return all_cap_re.sub(r'\1_\2', s1).lower()

def humanize_text(text):
    s1 = dequote(text)
    s1 = uncamel(s1)
    s1 = s1.replace("_", " ")
    s1 = s1.replace("/", " / ")
    if (contains_alpha(s1)):
        s1 = ' '.join(re.findall('(\d+|\w+)', s1))
    s1 = ' '.join(s1.split())
    return s1

def extract_info_from_string(text):
    result = {}
    text = humanize_text(text)
    for word in text.split(" "):
        if is_date(word):
            result['date'] = word
        elif is_year(word):
            result['year'] = word
    return result

def dequote(s):
    """
    If a string has single or double quotes around it, remove them.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if (
        s.startswith(("'", '"')) and s.endswith(("'", '"'))
        and (s[0] == s[-1])  # make sure the pair of quotes match
    ):
        s = s[1:-1]
    return s

def get_country_from_url(url):

    url_elements = urlparse(url).netloc.split(".")

    tld = ".".join(url_elements[-2:])
    if tld in all:
        return all[tld]
    elif url_elements[-1] in all:
        return all[url_elements[-1]]
    else:
        return "unknown"

class HumanizeTest(unittest.TestCase):

    def test_humanize(self):
        cell = '105mm'
        cleaned = humanize_text(cell)
        print cell, cleaned

        cell = '12.25'
        cleaned = humanize_text(cell)
        print cell, cleaned
#         print cleaned
        cell = 'StatBezirk'
        cleaned = humanize_text(cell)
        print cell, cleaned

class DatatypeTest(unittest.TestCase):

#     def test_unit(self):
#         cell = '105mm'
#         type = extract_datatype(cell)
#         assert type=='UNIT'

#         cell = 'Gebiet/Distrikt'
#         cleaned = humanize_text(cell)
#         print cleaned
#         type = extract_datatype(cell)
#         type = query_concept(cell)
#         type = query_concept(cell)
#         print type
#         assert type=='UNIT'

#     def test_concept(self):
#         cell = 'Geschlecht'
#         type = extract_datatype(cell, lang=None)
#         print type

#     def test_person(self):
#         cell = 'Major Disaster'
#         type = extract_datatype(cell)
#         print type
#
#     def test_dictionary(self):
#         pass
#
#     def test_date(self):
#         cell = '20110101'
#         type = extract_datatype(cell)
#         assert type=='DATE'
#
#         cell = '2011/01/01'
#         type = extract_datatype(cell)
#         assert type=='DATE'
#
#         cell = '2011-01-01'
#         type = extract_datatype(cell)
#         assert type=='DATE'
#
#         return True
    pass


# parsing functions
def parse_float(cell):
    """
    Float parser, used for converting strings to float values using the type classification of ComplexTypeAnalyser
    :param cell: A string which is considered as NUMBER or FLOAT by the ComplexTypeAnalyser
    :return: 0.0 on an empty input, the parsed float, or throws a ValueError
    """
    try:
        value = float(cell)
        return value
    except Exception as e:
        pass
    cell = str(cell).replace(" ", "")
    if "," in cell:
        if "." in cell:
            if cell.rfind(".") > cell.rfind(", "):
                cell = cell.replace(".", "")
                cell = cell.replace(",", ".")
                return parse_float(cell)
            else:
                cell = cell.replace(",", "")
                return parse_float(cell)
        else:
            cell = cell.replace(",", ".")
            return parse_float(cell)
    raise ValueError(cell + ': cannot convert to numeric')