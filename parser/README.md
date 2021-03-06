## TABLEMAGICIAN
This is a simple CSV validator and parser based on messytables (https://messytables.readthedocs.org/).

### INSTALL
##### Create a virtualenv or use an existing one:
$ virtualenv csvparser   
$ . csvparser/bin/activate

##### Check out the git repository:
$ git clone git@github.com:sebneu/csvprofiler.git   
$ cd csvprofiler/parser

##### Install the parser into the virtualenv:
$ python setup.py install

##### You can use develop mode instead if you want to edit your installed version:
$ python setup.py develop

##### For further commands find the help:
$ tablemagician -h


### EXAMPLES
##### Output the file as an RFC 4180 conform table to the terminal:
$ tablemagician -rfc test.csv

##### Process all files in a directory:
$ for f in *.csv;   
$   do tablemagician --rfc $f -o ~/test/$f ;   
$ done
