__author__ = 'jumbrich'


from text import text_utils
import re
import dateutil.parser
import math

url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


digittypes = [
    ('INT', int),
    ('LONG', long),
    ('FLOAT', float)]



def detectCellType(cell):
    '''
    Detect the type of a cell value
    Basic idea is:
        1) 1.1 (EMPTY): test for empty or null values
        2) check if the cell contains characters or not (+ some extra symbols for unit measures)
            2.1) contains characters
                2.1.1 (EMAIL) contains @ -> prop for EMAIL
                2.1.2 (URL) contains / or . -> prop for URL
                2.1.3 contains numbers
                    2.1.3.1) (DATE) try to parse the cell as a date
                    2.1.3.1) (TOKENS) contains whitespace


    @param cell:
    @return: BASETYPE:len/SUBTYPE1:len-SUBTYPE2:len
             The BASETYPE can be EMPTY, EMAIL, URL, DATE, NUMBER, ALPHA, ALPHANUM, NUMALPHA
             A + at the end of a basetype indicates special characters
             The length of the BASETYPE is separated by : and is optionally given
             Some types have SUBTYPEs, e.g., NUMBER/INT:4+ (the plus indicates greater zero), or NUMALPHA/NUMBER/FLOAT:3.1-ALPHA+:3
    '''
    #basic cleaning
    cell = cell.strip()

    # EMPTY, simple case, empty
    if text_utils.is_none_type(cell):
        return "EMPTY"
    else:
        # check for email, url, date and text (because it could contain a number as well)
        #EMAIL?
        if text_utils.contains_ampersand(cell):
            #ampersand -> email?
            if text_utils.is_email(cell):
                return "EMAIL"
        #URL?
        if "/" in cell or ".":
            # / or . -> URL?
            if url_regex.match(cell):
                return "URL"

        #contains ALPHA?
        if text_utils.contains_alpha(cell) or text_utils.contains_unit_symbol(cell):
            #we have at least one character in the cell

            #contains numbers ? ALPHANUM, NUMALPHA
            if text_utils.contains_number(cell):
                #DATE
                try:
                    dateutil.parser.parse(cell)
                    return "DATE"
                except ValueError:
                    pass
                except TypeError:
                    pass
                    #print "TypeERROR",cell

                #NUMALPHA (e.g. 12cm or 12 cm)
                numalpha = True
                num = ''
                ending = ''
                for s in cell:
                    if s.isdigit() or text_utils.contains_commas(s):
                        if len(ending) > 0:
                            numalpha = False
                            break
                        num += s
                    else:
                        ending += s
                ending = ending.strip()
                if numalpha and len(num) > 0 and len(ending.split(" ")) == 1:
                    is_alph = ''
                    if not ending.isalpha():
                        is_alph = '+'
                    return 'NUMALPHA/'+contains_number(num)+'-ALPHA' + is_alph + \
                           ':'+str(len(ending))

                # ALPHANUM ending with numbers (e.g., $ 4.50, % 30)
                alphnum = True
                num = ''
                leading = ''
                for s in cell:
                    if s.isdigit() or text_utils.contains_commas(s):
                        num += s
                    else:
                        if len(num) > 0:
                            alphnum = False
                            break
                        leading += s
                leading = leading.strip()
                if alphnum and len(num) > 0 and len(leading.split(" ")) == 1:
                    is_alph = ''
                    if not leading.isalpha():
                        is_alph = '+'
                    return 'ALPHANUM/ALPHA' + is_alph + ':'+str(len(leading))+\
                           '-'+contains_number(num)

                #TOKENS
                if " " in cell:
                    for token in cell.split(" "):
                        if not token.isalnum():

                            return "ALPHANUM+/TOKENS:" + str(len(cell.split(" ")))
                    return "ALPHANUM/TOKENS:" + str(len(cell.split(" ")))

                #ok alpha +num and not a date
                if cell.isalnum():
                    return "ALPHANUM:" + str(len(cell))
                else:
                    #alpha + numbers + something
                    return "ALPHANUM+:" + str(len(cell))

            elif " " in cell:
                #no numbers
                for token in cell.split(" "):
                    if not token.isalpha():
                        return "ALPHA+/TOKENS:" + str(len(cell.split(" ")))
                return "ALPHA/TOKENS:" + str(len(cell.split(" ")))

            elif cell.isalpha():
                #we have only alphas
                return "ALPHA:" + str(len(cell))
            else:
                # ok we have alpha and special characters
                return "ALPHA+:" + str(len(cell))

        elif text_utils.contains_number(cell):
            return contains_number(cell)

    return "UNKNOWN"


def contains_number(cell):
    #numbers and maybe special charaters
    if "/" in cell or "-" in cell:
        try:
            dateutil.parser.parse(cell)
            return "DATE"
        except ValueError:
            pass
        except TypeError:
            print cell

    #TODO Time

    if text_utils.contains_commas(cell):
        #FLOAT DOUBLE
        #we have digits and commas

        type = detectFloat(cell)
        if type:
            return 'NUMBER/'+type

        #remove any whitespaces

    if cell.isdigit():
        cell = long(cell)

        p="+"
        if cell <0:
            cell = math.fabs(cell)
            p="-"

        magnitude = 1 if cell == 0 else int(math.log10(cell)) + 1
        return "NUMBER/INT:"+str(magnitude)+p

    #no alphas
    return "NUMBER+"


def detectFloat(cell):
    cell = cell.replace(" ", "")
    try:
        float(cell)

        t = cell.split(".")

        a = len(t[0]) if len(t[0])<4 else "*"
        b = len(t[1]) if len(t[1])<4 else "*"

        return "FLOAT:"+str(a)+"."+str(b)
    except Exception as e:

        pass
    if "," in cell:
        if "." in cell:
            if cell.rfind(".") > cell.rfind(", "):
                cell = cell.replace(".", "")
                cell = cell.replace(",", ".")
                return detectFloat(cell)
            else:
                cell = cell.replace(",", "")
                return detectFloat(cell)
        else:
            cell = cell.replace(",", ".")
            return detectFloat(cell)

    return None