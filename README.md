simple HTTP proxy

can be launched locally on port 4443
shows habr.com content only
only standard python libraries used.

after every word that contains exactly 6 letters there should be a tm sign
when clicking any of the internal habr.com links the user must stay on the localhost

python 3.5+
all content shown correctly (incl. fonts, images, css)
PEP8 compliance checked with pylint 1.8.3
tests in the test folder (pytest tests/)

Launching the app:
1) python3 server.py
2) make - will automatically dockerize the app on the network of the host on port 4443
