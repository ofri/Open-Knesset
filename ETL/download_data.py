 # This Python file uses the following encoding: utf-8

import urllib2
import re
import gzip

def ReadPage(voteId):
    url = "http://www.knesset.gov.il/vote/heb/Vote_Res_Map.asp?vote_id_t=%d" % voteId
    urlData = urllib2.urlopen(url)
    page = urlData.read().decode('windows-1255').encode('utf-8')
    return page

def ReadMemberVotes(page):
    results = []
    pattern = re.compile("""Vote_Bord""")
    match = pattern.split(page)
    for i in match:
        vote = ""
        if(re.match("""_R1""", i)):
            vote = "for"
        if(re.match("""_R2""", i)):
            vote = "against"
        if(re.match("""_R3""", i)):
            vote = "abstain"
        if(re.match("""_R4""", i)):
            vote = "no-vote"
        if(vote != ""):
            name = re.search("""DataText4>([^<]*)</a>""",i).group(1);
            name = re.sub("""&nbsp;""", " ", name)
            party = re.search("""DataText4>([^<]*)</td>""",i).group(1);
            party = re.sub("""&nbsp;""", " ", party)
            if(party == """ " """):
                party = lastParty
            else:
                lastParty = party 
            results.append((name, party, vote))  
    return results


def PageTitle(page):
    title = re.search("""<TITLE>([^<]*)</TITLE>""", page)
    return title.group(1)

def VoteData(page):
    name = re.search("""שם החוק: </td>[^<]*<[^>]*>([^<]*)<""", page).group(1)
    name = name.replace("\t"," ")
    name = name.replace("\n"," ")
    name = name.replace("\r"," ")
    name = name.replace("&nbsp;"," ")
    date = re.search("""תאריך: </td>[^<]*<[^>]*>([^<]*)<""",page)
    return (name, date.group(1))
    
if __name__ == '__main__':
    f = gzip.open("data/results.tsv.gz", "wb")
    f2 = gzip.open("data/votes.tsv.gz","wb")
    r = range(1,12000) # this is the range of page ids to go over. currently its set manually.
    for id in r:
        page = ReadPage(id)
        title = PageTitle(page)
        if(title == """הצבעות במליאה-חיפוש"""): # found no vote with this id
            print "no vote found at id %d" % id
        else:
            countFor = 0
            countAgainst = 0
            countAbstain = 0
            countNoVote = 0
            (name,date) = VoteData(page)
            results = ReadMemberVotes(page)
            for i in results:
                f.write("%d\t%s\t%s\t%s\t%s\t%s\n" % (id,name,date,i[0],i[1],i[2]))
                if(i[2]=="for"):
                    countFor+=1
                if(i[2]=="against"):
                    countAgainst+=1
                if(i[2]=="abstain"):
                    countAbstain+=1
                if(i[2]=="no-vote"):
                    countNoVote+=1
            f2.write("%d\t%s\t%s\t%d\t%d\t%d\t%d\n" % (id, name, date, countFor,countAgainst,countAbstain,countNoVote))
            print "parsed data at id %d" % id
        print " %.1f%% done" % ( (100.0*(float(id)-r[0]))/(r[-1]-r[0]) )
    f.close()
    f2.close()
