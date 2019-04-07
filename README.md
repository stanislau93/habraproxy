simple HTTP proxy

can be launched locally on port 4443
shows habr.com content only
only standard python libraries used.

after every word that contains exactly 6 letters there should be a tm sign
when clicking any of the internal habr.com links the user must stay on the localhost

python 3.5+
all content shown correctly (incl. fonts, images, css)

tests in the test folder (pytest tests/)

Launching the app:
1) python3 proxy.py
2) make - will automatically dockerize the app on the network of the host on port 4443

TODOs: 

1) Consider caching the pages content in a database to not load the page every time anew (but what about updates??) or removing the 'page_' files and writing directly to the output buffer.
2) Add more tests