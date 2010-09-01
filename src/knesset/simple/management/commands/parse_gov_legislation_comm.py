#encoding: utf-8
import urllib2
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import re
import logging

logger = logging.getLogger("open-knesset.parse_gov_legislation_comm")

def soupifyPage(url):
    html_page = None
    retry_count = 0
    while not(html_page):
        try:
            html_page = urllib2.urlopen(url, timeout=15).read()
        except urllib2.URLError:
            retry_count += 1
            if retry_count >= 10:
                raise urllib2.URLError('URL %s failed too many times' % url)
    return BeautifulSoup(html_page)


class ParseGLC:
    """Parse Government Legislation Committee decisions, from their webpage http://www.pmo.gov.il/PMO/vadot/hakika/"""
    
    def __init__(self, year_num, month):
        self.pmo_url = r"http://www.pmo.gov.il"
        self.base_url = r"http://www.pmo.gov.il/PMO/vadot/hakika/2008-2010/"
        self.scraped_data = self.parse_pages_per_month(year_num, month)
        
    def parse_pages_per_month(self, year_num, month):
        res = []
        num_pages = self.figure_number_of_page_per_month(year_num, month)
        for page in range(1, num_pages + 1):
            res += self.parse_page(year_num, month, page)
            
        return res
        
    def figure_number_of_page_per_month(self, year, month):
        # Build the suffix of the URL (i.e '06-2010/deslist0610.htm?Page=1')
        pageURLSuffix = "%02d-20%02d/" % (month, year)
        
        # Fetch the soup
        soup = soupifyPage(self.base_url + pageURLSuffix)
        
        matches = soup.findAll(lambda tag: tag.name == 'a' and tag.has_key('class') and tag['class'] == u"PathChannelLink")
        if len(matches) == 0:
            #print "no pages found for url %s " % (self.base_url + pageURLSuffix)
            return 1

        return int (matches[-1].string)
        
    def parse_page(self, year, month, page):
        # Build the suffix of the URL (i.e '06-2010/deslist0610.htm?Page=1')
        pageURLSuffix = "%02d-20%02d/deslist%02d%02d.htm?Page=%d" % (month, year, month, year, page)

        # Fetch the soup
        soup = soupifyPage(self.base_url + pageURLSuffix)

        # Parse the individual entires by following their URL
        return self.parse_entries(soup)

    def parse_entries(self, soup):
        # Find and follow all links to single entries, return their parsed content
        matches = soup.findAll(lambda tag: tag.name == 'a' and tag.has_key('href') and tag.has_key('title')  and tag['title'] == u"קרא בהרחבה")
        res = []
        for match in matches:
            url = self.pmo_url + match['href']
            
            # Not using beautiful soup since it can't handle this page =(
            html_page = None
            retry_count = 0
            while not(html_page):
                try:
                    html_page = urllib2.urlopen(url, timeout=15).read()
                    break
                except urllib2.URLError:
                    retry_count += 1
                    if retry_count >= 10:
                        raise urllib2.URLError('URL %s failed too many times')
                
            parsed = self.parse_entry(html_page)
            parsed['url'] = url
            res.append(parsed)
            
        return res
        
    # Parse the content of an entry page
    def parse_entry(self, html_page):
        #subtitle = self.parse_entry_part_by_span_id(html_page, "SUB_TITLE_PH")
        #title = self.parse_entry_part_by_span_id(html_page, "SUBJECT_PH")
        #decision = self.parse_entry_part_by_span_id(html_page, "TEXT_PH")
        title = None
        subtitle = None
        decision = None
        number = None
        soup = BeautifulSoup(html_page)
        try:
            decision = soup.find('span',{'id':"TEXT_PH"}).contents
            decision = '\n'.join([unicode(x) for x in decision])
            decision = decision.replace('&nbsp;',' ').replace('<br />','')
            decision = self.decode_html_chars(decision)
            title = soup.find('span',{'id':"SUBJECT_PH"}).contents
            title = '\n'.join([unicode(x) for x in title])
            title = title.replace('&nbsp;',' ').replace('<br />','')
            title = self.decode_html_chars(title)
            subtitle = soup.find('span',{'id':"SUB_TITLE_PH"}).contents
            subtitle = '\n'.join([unicode(x) for x in subtitle])
            subtitle = subtitle.replace('&nbsp;',' ').replace('<br />','')
            subtitle = self.decode_html_chars(subtitle)
            number = re.search(r'הוא (\d+)'.decode('utf8'),subtitle).group(1)
        except Exception,e:
            print e
            
        return {'subtitle': subtitle, 'title':title, 'decision':decision,'number':number}
        
    # Parse the content of the span with the given id from a given entry page.
    def parse_entry_part_by_span_id(self, html_page, span_id):
        val_re = re.search("\<span id=\"%s\"[^\>]*\>([^\<]*)\<span>" % span_id, html_page)
        if not val_re or (len(val_re.groups()) == 0):
            return None        

        # For some reason the text is weirdly HTML-char-code encoded, decode.
        return self.decode_html_chars(val_re.groups()[0])
        
    def decode_html_chars(self, string):
        return str(BeautifulStoneSoup(string, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)).decode('UTF-8')
                
    
def main():
    parser = ParseGLC(10, 6)
    for d in parser.scraped_data:
        print "sub_subject:%s\n\nsubject: %s\n\ntext: %s\n\n\n\n" % (d["subtitle"], d["title"], d["decision"])

if __name__ == "__main__":
    main()
