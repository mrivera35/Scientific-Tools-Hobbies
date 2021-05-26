# Mixed Matrix Membranes Reproducibility Web-scraping Script

#Clear all
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import math
import selenium
from selenium import webdriver
import time
import os
from selenium.webdriver import ActionChains

#User Input 
sc=["ZIF-8",'Matrimid'] #enter search terms as a list of strings

driverpath='C:/Users/mrivera35/chromedriver.exe' #path for chromedriver program

driver=webdriver.Chrome(executable_path=driverpath)


#%%
#Search ScienceDirect URLs
#Initial webpage search
baseurl="https://www.sciencedirect.com/search/advanced?qs="
searchterms=''
for q in np.arange(0,len(sc)):
    if len(sc[q].split())==1:
        searchterms=searchterms+sc[q]+"%2C%20"
    else:
        scx=sc[q].split()
        searchterms=searchterms+"%20".join(scx)

urlsd=baseurl+searchterms+"&articleTypes=FLA&lastSelectedFacet=articleTypes"

driver.get(urlsd)
time.sleep(2)
numpages=driver.find_element_by_xpath("//body//div[@class='col-xs-24']//div[@class='Search']//div[@id='main_content']//main//div[@class='col-xs-24']//ol[@id='srp-pagination']//li").text
number = []
for word in numpages.split():
    if word.isdigit():
        number.append(int(word))
numpages=int(number[1])

linksd=pd.Series(["0"])

for j in np.arange(0,numpages):
    urlsdpg=urlsd+'&offset='+str(j*25)
    
    driver.get(urlsdpg)
    time.sleep(2)
    searchresultssd=driver.find_elements_by_xpath("//body//div[@class='sd-flex-container']//div[@class='SearchPage']//div[@class='col-xs-24']//div[@id='main_content']//main[@class='SearchBody row transparent']//div[@class='col-xs-24']//ol[@class='search-result-wrapper']//li[@class='ResultItem col-xs-24 push-m']") 

    for k in np.arange(0,len(searchresultssd)):
        result=BeautifulSoup(searchresultssd[k].get_attribute('innerHTML'),'lxml')
        resultlink=pd.Series(result.find("a")['href'])
        linksd=pd.concat([linksd,resultlink],ignore_index=True)
        
linksd=linksd.drop(0)

#Scrape individual article pages for information
resdoi=pd.Series(["0"]) #dummy series to concatenate onto
resabstracts=pd.Series(['0'])
resauthors=pd.Series(['0'])
reslinks=pd.Series(['0'])
resyear=pd.Series(['0'])
resjournal=pd.Series(['0'])
rescitations=pd.Series(['0'])
restitles=pd.Series([0])
for i in np.arange(0,len(linksd.index)): 
    resurl="https://www.sciencedirect.com"+str(linksd.iloc[i])
    driver.get(resurl) #opens webpage by controlling Chrome with python
    time.sleep(2)
    ressoupsd=BeautifulSoup(driver.find_elements_by_class_name("Article")[0].get_attribute('innerHTML'),'lxml')
   
     
   
    title=pd.Series(ressoupsd.find("span",class_="title-text").text) #get paper title
    abstract=pd.Series(ressoupsd.find("div",class_="abstract author").text[8:]) #get paper abstract
    doi=pd.Series(ressoupsd.find('a',class_='doi')['href'][8:])
    try:
        journal=pd.Series(ressoupsd.find("a",class_="publication-title-link").text)
    except:
        journal=pd.Series('')
        
    try: #can't find this sometimes, usually because it's 0 
        citations=pd.Series(int(driver.find_element_by_xpath("//div[@class='sd-flex-container']//aside[@class='RelatedContent']").find_elements_by_xpath("//section")[2].find_element_by_xpath("//div[@class='plum-sciencedirect-theme']//div[@class='pps-col plx-citation']//span[@class='pps-count']").text))
    except:
        citations=pd.Series('')
        
    authors=ressoupsd.find('div',class_='author-group') #get list of authors
    authors=authors.find_all('span',class_='text surname')
    allauthors=pd.Series(["0"])
    for k in range(len(authors)): #loops over number of authors to get all last names
        aut=pd.Series(authors[k].text)
        allauthors=pd.concat([allauthors,aut],ignore_index=True)
    allauthors=allauthors.drop(0)
    allauthors=pd.Series(",".join(allauthors)) #joins list into single string with authors separated by comma
    try: 
        year=ressoupsd.find("span",class_="copyright-line").text #gets article year as only integer in copyright line at bottom of page
        number = []
        for word in year.split():
            if word.isdigit():
                number.append(int(word))
        number=pd.Series(number)   
    except:
        continue
    
    resdoi=pd.concat([resdoi,doi],ignore_index=True)
    resurl=pd.Series([resurl])
    restitles=pd.concat([restitles,title],ignore_index=True)
    resabstracts=pd.concat([resabstracts,abstract],ignore_index=True)
    resauthors=pd.concat([resauthors,allauthors],ignore_index=True)
    reslinks=pd.concat([reslinks,resurl],ignore_index=True)
    resjournal=pd.concat([resjournal, journal], ignore_index=True)
    resyear=pd.concat([resyear,number], ignore_index=True)
    rescitations=pd.concat([rescitations,citations],ignore_index=True)
    
resdoi=resdoi.drop(0) #drop initial dummy 0     
restitles=restitles.drop(0)
resabstracts=resabstracts.drop(0)
resauthors=resauthors.drop(0)
reslinks=reslinks.drop(0)
resjournal=resjournal.drop(0)
resyear=resyear.drop(0)
rescitations=rescitations.drop(0)

scidirresults=pd.concat([restitles,resauthors,resyear, resjournal, rescitations, resdoi,reslinks,resabstracts],axis=1,ignore_index=True)
scidirresults.columns=['Title','Authors','Year','Journal', 'Citations','DOI','Link to Full Paper','Abstract']
    

#%%
#Search ACS URLs
#Initial publisher webpage search

baseurl="https://pubs.acs.org/action/doSearch?AllField="
searchterms=''
for q in np.arange(0,len(sc)):
    if len(sc[q].split())==1:
        searchterms=searchterms+sc[q]+"%2C+"
    else:
        scx=sc[q].split()
        searchterms=searchterms+"+".join(scx)
        
urlacs="https://pubs.acs.org/action/doSearch?AllField="+searchterms

driver.get(urlacs) #opens webpage by controlling Chrome with python

numres=driver.find_elements_by_class_name('result__count')[0].text #finds total number of results

numpages=math.ceil(int(numres)/20) #create number of pages needed with 20 results per page
pages=np.arange(0,numpages) #create list of page numbers

time.sleep(2) #wait between webpage requests so server doesn't block IP address

#Pull relevant info from search results
acsresults=pd.Series([0])
for i in pages: #loop over each search result page 
    urlacspg=urlacs+"&startPage="+str(i)+"&pageSize=20" 
    driver.get(urlacspg)
    time.sleep(2)
    results=driver.find_elements_by_class_name('issue-item_metadata') #find info for all results on page
    
    for j in np.arange(0,len(results)): #loop over each result on a given page 
        soup=BeautifulSoup(results[j].get_attribute('innerHTML'),'lxml') #finds html for search result and converts to BeautifulSoup object
        title=pd.Series([soup.find('a').text])
        authors=soup.find_all('span',class_='hlFld-ContribAuthor') #finds all author tags
        allauthors=pd.Series(['0'])
        for k in range(len(authors)): #loop over number of author tags
            aut=pd.Series(authors[k].text)
            allauthors=pd.concat([allauthors,aut],ignore_index=True) #combines author fields into one pandas Series
        allauthors=allauthors.drop(0)
        allauthors=pd.Series(",".join(allauthors)) #joins list into single string with authors separated by comma
        doi=soup.find('span',class_='issue-item_doi').text[5:]
        link='https://pubs.acs.org/doi/'+str(doi) #need to combine strings before converting to pandas Series so they combine correctly
        doi=pd.Series([doi])
        link=pd.Series([link])
        journal=pd.Series(soup.find("span",class_="issue-item_jour-name").text)
        try: #the abstract isn't available for some results and it gives a link to the first page instead
            abstract=pd.Series([soup.find('span',class_='hlFld-Abstract').text])
        except:
            abstract=pd.Series(["Not available"]) #if the abstract isn't available 
        resultinfo=pd.concat([title,allauthors, journal, doi,link,abstract],axis=1,ignore_index=True) #combines all relevant info for single results

        acsresults=pd.concat([acsresults,resultinfo],ignore_index=True) #adds single result info to comprehensive list


#go to article page to get citations
citations=pd.Series(0)
year=pd.Series(0)
for i in np.arange(1,len(acsresults.index)): 
    resurl=acsresults.iloc[i,4]
    driver.get(resurl)
    time.sleep(2)
    try:
        cite=pd.Series([int(driver.find_elements_by_xpath(("//div[@class='article_header-left pull-left']//div[@class='articleMetrics_table']//div[@class='articleMetrics_count']//a[@class='internalNav']"))[0].text)])
    except:
        cite=pd.Series([''])
    citations=pd.concat([citations,cite],ignore_index=True) 
    
    resyear=pd.Series(int(driver.find_element_by_xpath("//div[@class='article_header']//div[@class='article_header-meta clearfix']//span[@class='cit-year-info']").text))
    year=pd.concat([year,resyear],ignore_index=True)

acsresults=pd.concat([acsresults.iloc[:,0:2],year,acsresults.iloc[:,2],citations,acsresults.iloc[:,3:6]],axis=1,ignore_index=True)                             
acsresults.columns=['Title','Authors','Year','Journal', 'Citations','DOI','Link to Full Paper','Abstract']
acsresults=acsresults.drop(0)

#%%
#Search Wiley

baseurl="https://onlinelibrary.wiley.com/action/doSearch?AllField="
searchterms=''
for q in np.arange(0,len(sc)):
    if len(sc[q].split())==1:
        searchterms=searchterms+sc[q]+"%2C"
    else:
        scx=sc[q].split()
        searchterms=searchterms+"+".join(scx)


urlwiley=baseurl+searchterms+"&startPage=&PubType=journal"

driver.get(urlwiley)

numres=driver.find_elements_by_class_name('result__count')#finds total number of results
numres=numres[0].text

numpages=math.ceil(int(numres)/20) #create number of pages needed with 20 results per page
pages=range(0,numpages) #create list of page numbers


#Pull relevant info from search results
wileyresults=pd.Series([0])
for i in pages: #loop over each search result page
    resurlwiley=baseurl+searchterms+'&PubType=journal&startPage='+str(i)+'&pageSize=20'
    driver.get(resurlwiley)
    time.sleep(2)
    results=driver.find_elements_by_class_name('item__body') #find info for all results on page
    
    for j in np.arange(0,len(results)): #loop over each result on a given page
        soup=BeautifulSoup(results[j].get_attribute('innerHTML'),'lxml') #finds html for search result and converts to BeautifulSoup object
        title=pd.Series([soup.find('a',class_='publication_title visitable').text])
        authors=soup.find_all('a',class_='publication_contrib_author') #finds all author tags
        allauthors=pd.Series(['0'])
        for k in range(len(authors)): #loop over number of author tags
            aut=pd.Series(authors[k].text)
            allauthors=pd.concat([allauthors,aut],ignore_index=True) #combines author fields into one pandas Series
        allauthors=allauthors.drop(0)
        allauthors=pd.Series(",".join(allauthors)) #joins list into single string with authors separated by comma
        doi=soup.find('a')['href']
        link='https://onlinelibrary.wiley.com'+str(doi) #need to combine strings before converting to pandas Series so they combine correctly
        doi=pd.Series([doi])
        link=pd.Series([link])
        journal=pd.Series(soup.find("a",class_="publication_meta_serial").text)
        year=soup.find("p",class_="meta__epubDate").text
        number = []
        for word in year.split():
            if word.isdigit():
                number.append(int(word))
        year=pd.Series(int(number[1]))   
      
        resultinfo=pd.concat([title,allauthors,year, journal,doi,link],axis=1,ignore_index=True) #combines all relevant info for single results

        wileyresults=pd.concat([wileyresults,resultinfo],ignore_index=True) #adds single result info to comprehensive list
       
       
wileyresults=wileyresults.drop(0)


citations=pd.Series(0)
abstracts=pd.Series(0)

for r in np.arange(0,len(wileyresults)): 
    driver.get(wileyresults.iloc[r,5])
    time.sleep(2)
    try:
        cite=pd.Series(int(driver.find_element_by_xpath(("//div[@class='epub-section cited-by-count']//a")).text))
    except:
        cite=pd.Series([''])
    citations=pd.concat([citations,cite],ignore_index=True)
    
    try: #sometimes the abstract isn't available for some results and it gives a link to the first page instead
        resabstract=pd.Series(driver.find_element_by_xpath("//div[@id='pb-page-content']//main[@id='main-content']//div[@class='article-section__content en main']").text)
    except:
        resabstract=pd.Series(["Not available"]) #if the abstract isn't available 
    
    abstracts=pd.concat([abstracts,resabstract],ignore_index=True)

citations=citations.drop(0)
abstracts=abstracts.drop(0)

wileyresults=pd.concat([wileyresults.iloc[:,0:4],citations,wileyresults.iloc[:,4:6],abstracts],axis=1,ignore_index=True)
    
wileyresults.columns=['Title','Authors','Year','Journal', 'Citations','DOI','Link to Full Paper','Abstract']



#%%
#Royal Society of Chemistry Results

baseurl="https://pubs.rsc.org/en/results?searchtext="
searchterms=''
for q in np.arange(0,len(sc)):
    searchterms=searchterms+sc[q]+"%20"


urlrsc=baseurl+searchterms
driver.get(urlrsc)
time.sleep(3)
pages=int(driver.find_element_by_class_name('paging--label').text[-1])

mainresults=driver.find_elements_by_class_name('capsule__action') #main article info in different tags
linkresults=driver.find_elements_by_class_name('capsule__footer') #link to paper in footer under different tag

#get initial result set
rscresults=pd.Series([0])
for k in np.arange(0,len(mainresults)):
    try:
        soup1=BeautifulSoup(mainresults[k].get_attribute('innerHTML'),'lxml')
        soup2=BeautifulSoup(linkresults[k].get_attribute('innerHTML'),'lxml')
        title=pd.Series([soup1.find("h3",class_="capsule__title").text])
        authors=pd.Series([soup1.find("div",class_="article__authors article__author-link").text])
        link=pd.Series([soup2.find("a").text])
        doi=pd.Series([soup2.find('a').text[8:-1]])
        year=soup2.find('span',class_='block fixpadv--xs').text
        number = []
        for word in year.split():
            if word.isdigit():
                number.append(int(word))
        year=pd.Series(int(number[1])) 
        resinfo=pd.concat([title,authors,year,doi,link],axis=1)
        rscresults=pd.concat([rscresults,resinfo],ignore_index=True)
    except:
        continue

#have to click through buttons to get other results because url doesn't change
for i in np.arange(0,pages-1):
    nextbutton=driver.find_element_by_xpath("//a[@class='paging__btn paging__btn--next']")
    nextbutton.click()
    time.sleep(3)
    mainresults=driver.find_elements_by_class_name('capsule__action') #main article info in different tags
    linkresults=driver.find_elements_by_class_name('capsule__footer') #link to paper in footer under different tag

    for j in np.arange(0,len(mainresults)):
        try: #some results are books that won't conform to this search
            soup1=BeautifulSoup(mainresults[j].get_attribute('innerHTML'),'lxml')
            soup2=BeautifulSoup(linkresults[j].get_attribute('innerHTML'),'lxml')
            title=pd.Series([soup1.find("h3",class_="capsule__title").text])
            authors=pd.Series([soup1.find("div",class_="article__authors article__author-link").text])
            link=pd.Series([soup2.find("a").text])
            doi=pd.Series([soup2.find('a').text[8:-1]])
            year=soup2.find('span',class_='block fixpadv--xs').text
            number = []
            for word in year.split():
                if word.isdigit():
                    number.append(int(word))
            year=pd.Series(int(number[1]))   
            
            resinfo=pd.concat([title,authors,year, doi,link],axis=1)
            rscresults=pd.concat([rscresults,resinfo],ignore_index=True)
        except:
            continue

#go to article pages and get metadata and abstract
abstracts=pd.Series([0])
journal=pd.Series([0])
citations=pd.Series([0])
for i in np.arange(0, len(rscresults.index)-1): 
    driver.get(rscresults.iloc[i+1,4])
    resabs=pd.Series([driver.find_element_by_class_name('capsule__column-wrapper').text])
    abstracts=pd.concat([abstracts,resabs],ignore_index=True)
    resjour=pd.Series([driver.find_element_by_xpath("//h3[@class='h--heading3 no-heading']").text])
    journal=pd.concat([journal,resjour],ignore_index=True)
    try:
        citedtab=driver.find_element_by_xpath("//a[@aria-label='Cited by tab: A list of other articles that have cited this article.']")
        citedtab.click()
        time.sleep(5)
        rescite=driver.find_element_by_xpath("//section[@class='layout__content']//div[@class='pnl pnl--border pnl--drop autopad']").text
        numbers = []
        for word in list(rescite):
            if word.isdigit():
                numbers.append(word)            
        cite=pd.Series(int(''.join(numbers))) 
        
    except:
        cite=pd.Series('')
    citations=pd.concat([citations,cite],ignore_index=True)

    
rscresults=pd.concat([rscresults.iloc[:,0:3],journal,citations,rscresults.iloc[:,3:5],abstracts],axis=1,ignore_index=True)
rscresults.columns=['Title','Authors','Year','Journal', 'Citations','DOI','Link to Full Paper','Abstract']
rscresults=rscresults.drop(0)

#%%
# Nature Results

baseurl="https://www.nature.com/search?q="
searchterms=''
for q in np.arange(0,len(sc)):
    if len(sc[q].split())==1:
        searchterms=searchterms+sc[q]+"%2C%20"
    else:
        scx=sc[q].split()
        searchterms=searchterms+"+".join(scx)
        
urlnat=baseurl+searchterms+'&order=relevance'
driver.get(urlnat)

time.sleep(2) 

numresults=driver.find_element_by_xpath("//div[@class='pin-left pl10 filter-results']").text
number = []
for word in numresults.split():
    if word.isdigit():
        number.append(int(word))
numresults=int(number[0])
pages=math.ceil(numresults/50)


natres=pd.Series([0])

for i in np.arange(0,pages):
    searchurl=urlnat+'&page='+str(i+1)
    driver.get(searchurl)
    
    time.sleep(2)
    
    soup=BeautifulSoup(driver.find_element_by_class_name('home-page').get_attribute('innerHTML'),'lxml')
    searchresults=soup.find_all('li',class_='mb20 pb20 cleared')
    
    for j in np.arange(0,len(searchresults)):
        result=searchresults[j]
        title=pd.Series(result.find('h2',role='heading').text)
        authors=result.find_all('li',itemprop='creator')
        allauthors=[]
        for k in np.arange(0,len(authors)):
            aut=authors[k].text
            allauthors.append(aut)
        allauthors=pd.Series(' '.join(allauthors))
        link=pd.Series('https://www.nature.com'+result.find('h2',role='heading').find('a')['href'])

        resinfo=pd.concat([title,allauthors,link],axis=1,ignore_index=True)
        natres=pd.concat([natres,resinfo],ignore_index=True)

natres=natres.drop(0)

natureresults=pd.Series([0])
for i in np.arange(0,len(natres.index)):
    driver.get(natres.iloc[i,2])
    
    journal=pd.Series(driver.find_element_by_xpath("//i[@data-test='journal-title']").text)
    year=pd.Series(driver.find_element_by_xpath("//span[@data-test='article-publication-year']").text)
    cite=driver.find_elements_by_xpath("//p[@class='c-article-metrics-bar__count']")[1].text
    number = []
    for word in cite.split():
        if word.isdigit():
            number.append(int(word))
    try:
        cite=pd.Series(int(number[0]))
    except:
        cite=pd.Series('')
    abstr=pd.Series(driver.find_element_by_xpath("//div[@class='c-article-body']//div[@class='c-article-section__content']").text)
    allinfo=pd.concat([pd.Series(natres.iloc[i,0]),pd.Series(natres.iloc[i,1]),year,journal,cite,pd.Series(''),pd.Series(natres.iloc[i,2]),abstr],axis=1,ignore_index=True)
    natureresults=pd.concat([natureresults,allinfo],ignore_index=True)
   
natureresults=natureresults.drop(0)
natureresults.columns=['Title','Authors','Year','Journal', 'Citations','DOI','Link to Full Paper','Abstract']

#%%
#Science Search Results
baseurl="https://search.sciencemag.org/?searchTerm="
searchterms=''
for q in np.arange(0,len(sc)):
    if len(sc[q].split())==1:
        searchterms=searchterms+sc[q]+"%2C%20"
    else:
        scx=sc[q].split()
        searchterms=searchterms+"%20".join(scx)
        
urlsci=baseurl+searchterms+'&order=tfidf&limit=textFields&pageSize=100&articleTypes=Research%20and%20reviews&'
driver.get(urlsci)

time.sleep(2)

numres=driver.find_element_by_xpath("//p[@class='ss-summary standout']").text
number = []
for word in numres.split():
        if word.isdigit():
            number.append(int(word))
numres=int(number[0])
numpages=math.ceil(numres/100)


scienceresults=pd.Series(0)
link=pd.Series(0)
title=pd.Series(0)
year=pd.Series(0)
doi=pd.Series(0)

    
pageres=driver.find_elements_by_xpath("//div[@id='main-content']//div[@class='ss-primary ss-primary--reversed']//ul[@class='headline-list']//li")
    
for j in np.arange(0,10):
    #resultj=BeautifulSoup(pageres[j].get_attribute('innerHTML'),'lxml')
    resultj=pageres[j]
    restitle=resultj.find_element_by_xpath("//a").text
    reslink=resultj.find_element_by_xpath("//h2").find_element_by_partial_link_text(restitle[0:10])
    #reslink=pd.Series(resultj.find('h2',class_='media__headline').find('a')['href'])
    resyear=resultj.find('p',class_='ss-byline').text
    number = []
    for word in resyear.split():
        if word.isdigit():
            number.append(int(word))
    resyear=pd.Series(int(number[0]))
    resdoi=pd.Series(resultj.find('ul',class_='ss-media__meta list-inline').find('li').text)
    
    scienceresults=pd.concat([restitle,resyear,resdoi,reslink],axis=1,ignore_index=True)
        
     
        
#%%
driver.close() #closes webpages when finished

allresults=pd.concat([scidirresults,acsresults,wileyresults,rscresults,natureresults,scienceresults],ignore_index=True)

os.chdir('C:/Users/mrivera35/Desktop/Group Documents/My Papers/MMM Reproducibility')

namestring=''
for n in np.arange(0,len(sc)):
    namestring=namestring+', '+sc[n]
namestring=namestring[2:]

allresults.to_csv(namestring+' Literature References.csv')


