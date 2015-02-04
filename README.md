ConParser
=========
Because sometimes you only need simple way to get data from various types of contact files.

ConParser is a Python wrapping library intended to parse multiple formats of contact/business card files, including:

* CSV - Comma Separated Values [**WIP**]
* vCard - Business cards in formats:
 * vCard (2.1, 3.0, 4.0) [**WIP, but working**]
 * jCard [**Not started**]
 * hCard (1.0) [**Not started**]
 * h-card [**Not started**]

# Usage examples

```python

import sys
import conparser.utils as utils

with open("tests/contacts.vcf", mode="r") as cfile:
    # Using universal get_object method you get object with your data ready to be accessed
    # raw argument should be an iterable with file lines encoded in utf-8,
    # strict argument controls if during validation there should be run checks for valid parameters
    # according to given format specification and version
    obj = utils.get_object(raw=cfile.readlines(), strict=True)
    
    # You can check if file was parsed as vCard file
    if not obj.is_valid("vcard"):
        print("Given file is not a valid vCard file")
        sys.exit()
        
```
Now you have access to all data from given file and you can retrieve it using some methods
```python
    # You can in example get all entries which have email defined
    entries_with_email = obj.get_entries_with_tag("email")

    # Access all the entries
    for entry in obj.get_entries():
        # Get values
        if entry.has_tag('LOGO'):
            print(entry.get_single('LOGO').get_value())

        # And get tag parameters
        if entry.has_tag('email'):
            params = entry.get_single("email").get_params()
            for param in params:
                print(param.data)
```
