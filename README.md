# Scientific-Tools-Hobbies

Hi random internet user,

This is just a place for a nerdy grad student to upload things I thought other other people in the scientific community might find useful. I created the code here myself to help with things related to my thesis work, or just because I thought it'd be a fun project. I'm not a coder by training and this is primarily a hobby so I apologize in advance for any clunkiness/lack of user-friendliness. I'm always open to advice for improvement! I hope there's something here you find helpful or interesting!

Happy coding!
mrivera35


List of programs and descriptions:
1. WebscrapingScript: Written in Python. Will need all of the packages listed at the top of the program and chromium webdriver. Scrapes scientific journal publishers (ScienceDirect, ACS, Wiley, RSC, Nature, Science) for some basic article info ('Title','Authors','Year','Journal', 'Citations','DOI','Link to Full Paper','Abstract'). You can enter as many search criterion as you want at the top. You also need to the enter the filepath where the webdriver is saved and filepath where you want to results saved. The program then uses Selenium to visit the publisher search pages and then article pages for the info. You can search them all at once, or run section by section for specific publishers. I wrote this to help write a review paper thinking it would help narrow things down a bit more than a Google Scholar search. I found it helpful to further refine the initial search with sub-searches for strings in the abstracts (although I did that separately).  
