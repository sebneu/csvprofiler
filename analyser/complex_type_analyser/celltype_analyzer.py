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
        2) check if the cell contains characters or not
            2.1) contains characters
                2.1.1 (EMAIL) contains @ -> prop for EMAIL
                2.1.2 (URL) contains / or . -> prop for URL
                2.1.3 contains numbers
                    2.1.3.1) (DATE) try to parse the cell as a date
                    2.1.3.1) (TOKENS) contains whitespace


    @param cell:
    @return:
    '''
    '''
    @param cell:
    @return:
    '''
    #basic cleaning
    cell = cell.strip()

    # EMPTY, simple case, empty
    if cell is None or len(cell) == 0 or cell == 'null' or cell == 'None':
        return "EMPTY"
    else:

        #contains ALPHA?
        if text_utils.contains_alpha(cell) or text_utils.contains_unit_symbol(cell):
            #we have at least one character in the cell
            # check for email, url, date and text

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

            #contains numbers ? ALPHANUM
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
                if numalpha and len(num) > 0 and len(ending.strip().split(" ")) == 1:
                    return 'NUMALPHA/'+contains_number(num)+':ALPHA+/'+str(len(ending.strip()))

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
                if alphnum and len(num) > 0 and len(leading.strip().split(" ")) == 1:
                    return 'ALPHANUM/'+'ALPHA+/'+str(len(leading.strip()))+':'+contains_number(num)

                #TOKENS
                if " " in cell:
                    for token in cell.split(" "):
                        if not token.isalnum():

                            return "ALPHANUM+/TOKENS"
                    return "ALPHANUM/TOKENS"

                #ok alpha +num and not a date
                if cell.isalnum():
                    return "ALPHANUM"
                else:
                    #alpha + numbers + something
                    return "ALPHANUM+"

            elif " " in cell:
                #no numbers
                for token in cell.split(" "):
                    if not token.isalpha():
                        return "ALPHA+/TOKENS"
                return "ALPHA/TOKENS"

            elif cell.isalpha():
                #we have only alphas
                return "ALPHA"
            else:
                # ok we have alpha and special characters
                return "ALPHA+"

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

    if text_utils.contains_commas(cell) :
        #FLOAT DOUBLE
        #we have digits and commas

        type = detectFloat(cell)
        if type:
            return type

        #remove any whitespaces

    if cell.isdigit():
        cell = long(cell)

        p="+"
        if cell <0:
            cell = math.fabs(cell)
            p="-"

        magnitude = 1 if cell == 0 else int(math.log10(cell)) + 1
        return "NUMBER/"+str(magnitude)+p

    #no alphas
    return "NUMERIC+"




def detectFloat(cell):
    cell = cell.replace(" ","")
    try:
        float(cell)

        t= cell.split(".")

        a= len(t[0]) if len(t[0])<4 else "*"
        b= len(t[1]) if len(t[1])<4 else "*"

        return "FLOAT/"+str(a)+"."+str(b)
    except Exception as e:

        pass
    if "," in cell:
        if "." in cell:
            if cell.rfind(".") > cell.rfind(", "):
                cell = cell.replace(".","")
                cell = cell.replace(",",".")
                return detectFloat(cell)
            else:
                cell = cell.replace(",","")
                return detectFloat(cell)
        else:
            cell = cell.replace(",",".")
            return detectFloat(cell)

    return None