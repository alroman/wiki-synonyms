# Wiki 2nd attempt

#NOTE:
# We'll need to permute names.. common pattern: abcd efgh -> Abcd Efgh -> ABCD Efgh -> Abcd_efgh -> ABCD_efgh -> ABCD_Efgh

# REF: http://www.mediawiki.org/wiki/API:Query#Resolving_redirects
# How to get titles:
# http://en.wikipedia.org/w/api.php?action=query&titles=Binary%20Tree|Binary%20Trees|Binary_Trees&indexpageids&format=xml

# REF: http://www.mediawiki.org/wiki/API:Properties
# How to get a category
# http://en.wikipedia.org/w/api.php?action=query&titles=Binary_tree&prop=categories

# How to get a template
# http://en.wikipedia.org/w/api.php?action=query&titles=Binary_tree&prop=templates&redirects

# How to get template body
# http://en.wikipedia.org/w/api.php?action=query&titles=Binary%20tree|Binary%20Tree|binary_tree&indexpageids&format=xml

import urllib
import string
import sys
import pprint
import json
from xml.dom import minidom

# Pretty print
pp = pprint.PrettyPrinter()


def generate_titles(word):
    # We'll need to permute names.. 
    # common patterns: 
    #   abcd efgh 
    #   Abcd Efgh
    #   Abcd efgh
    #   ABCD efgh
    #   ABCD Efgh
    #   ABCD EFGH

    vals = list()

    # Add original
    vals.append(word)

    # Add with first word capitalized
    vals.append(word.capitalize())

    # Add all caps
    vals.append(word.upper())

    words = word.split(' ')
    if(len(words) > 1):

        words[0] = words[0].capitalize()

        # Add with every word capitalized
        front = words.pop(0)
        frontcaps = front.upper()

        vals.append(frontcaps + ' ' + ' '.join(words))

        inner_caps = list()
        for s in words:
            inner_caps.append(s.capitalize())
            
        vals.append(front + ' ' + ' '.join(inner_caps))

    return vals

def wiki_query(params):
    '''
        Wrapper for the wiki API call.  This accepts a params dictionary of name 
        value pairs, and returns the response from the wiki API

        @params dictionary of name-value pairs
        @data return from wiki API
    '''

    encoded_params = urllib.urlencode(params)

    url = "http://en.wikipedia.org/w/api.php"

    data = urllib.urlopen(url, encoded_params)

    return data

def get_proper_wiki_titles(title):
    ''' 
        Given a title, this tries to disambiguate the title to the
        correct wiki title.  It will also collect the non-negative IDs
    '''

    titles = generate_titles(title)

    params = {
        'action': 'query',
        'titles': '|'.join(titles),
        'format': 'xml',
        'indexpageids': '',
        'redirects' : ''
    }

    dom = minidom.parse(wiki_query(params))

    redirects_list = list()
    pageids_list = list()
    normalized_titles = list()

    # Get the <query> element
    query = dom.getElementsByTagName('query')[0]
    
    # XML printout
    # print query.toprettyxml()
    
    # Capture the normalized title.  We don't know if this field will 
    # always exist, so we try to handle an exception
    try:
        normalized = query.getElementsByTagName('normalized')[0]
        
        if(normalized):
            normalized_n = query.getElementsByTagName('n')

            for n in normalized_n:
                normalized_titles.append(n.getAttribute('to'))

    except Exception:
        print "there was an error getting normalized"

 
    # Capture the pageids
    pageids = query.getElementsByTagName('pageids')[0]

    if(pageids):
        ids = pageids.getElementsByTagName('id')

        for i in ids:
            id_val = int(i.firstChild.data)
            if(id_val > 0):
                pageids_list.append(id_val)

    redirects = query.getElementsByTagName('redirects')

    # Capture redirections 
    if(redirects):

        redirects_r = redirects[0].getElementsByTagName('r')
        for r in redirects_r:
            redirects_list.append(r.getAttribute('to'))

    # Return all results
    return pageids_list, normalized_titles, redirects_list

def get_wiki_categories_by_title(title):
    '''
        Given a title, this tries to return the categories that title belongs to

        @title a title string
        @return a list of categories or None
    '''

    params = {
        'action': 'query',
        'titles': title,
        'prop': 'categories',
        'format': 'xml',
        'cllimit': 100
    }

    dom = minidom.parse(wiki_query(params))

    query = dom.getElementsByTagName('query')[0]
    
    # XML printout
    #print query.toprettyxml()

    # Try to traverse the tree and get the categories... If
    # we hit an exeption, then this title has no categories
    try:
        pages = query.getElementsByTagName('pages')[0]
        page = pages.getElementsByTagName('page')[0]
        categories = page.getElementsByTagName('categories')[0]
        cl = page.getElementsByTagName('cl')

        catlist = list()

        for cat in cl:
            catlist.append(cat.getAttribute('title'))
        
        return catlist
    except:
        return None

# INCLUSION/EXCLUSION LISTS
def open_exclusion_list():
    exclusion_list = 'exclusion_list'

    fp = open(exclusion_list, 'r+')

    out_list = list();

    for line in fp:
        line = string.rstrip(line)
        out_list.append(line)

    fp.close()
    
    return out_list

def save_exclusion_list(lst):
    exclusion_list = 'exclusion_list'
    fp = open(exclusion_list, 'w')

    for line in lst:
        line = string.rstrip(line)
        fp.write(line.encode('utf-8', 'ignore') + '\n')

    fp.close()


def get_templates_by_title(title):
    '''
        Given a title, return a list of all the matching templates for that title.

        @TODO: filter out known 'junk' templates to avoid API overhead

        @title string title
        @return template list or None on error
    '''

    params = {
        'action': 'query',
        'titles': title,
        'prop': 'templates',
        'format': 'xml',
        'tllimit': 200,
        'redirects': ''
    }

    dom = minidom.parse(wiki_query(params))

    query = dom.getElementsByTagName('query')[0]
    
    # XML printout
    # print query.toprettyxml()

    ignore_list = [
    'Template:=',
    'Template:!',
    'Template:Ambox',
    'Template:Ambox/category',
    'Template:Ambox/core',
    'Template:As of',
    'Template:Basepage subpage',
    'Template:By whom',
    'Template:Case preserving encode',
    'Template:Category handler',
    'Template:Category handler/blacklist',
    'Template:Category handler/numbered',
    'Template:Citation',
    'Template:Citation/core',
    'Template:Citation/identifier',
    'Template:Citation/make link',
    'Template:Citation needed',
    'Template:Cite book',
    'Template:Cite journal',
    'Template:Cite news',
    'Template:Cite web',
    'Template:Column-count',
    'Template:Column-width',
    'Template:Condense',
    'Template:DMCA',
    'Template:Dated maintenance category',
    'Template:Disambiguation needed',
    'Template:Distinguish',
    'Template:Dmoz',
    'Template:Dn',
    'Template:Expand section',
    'Template:FULLROOTPAGENAME',
    'Template:Fix',
    'Template:Fix/category',
    'Template:Harvard citation no brackets',
    'Template:Harvnb',
    'Template:Hatnote',
    'Template:Hide in print',
    'Template:Icon',
    'Template:If pagename',
    'Template:Ifsubst',
    'Template:Main',
    'Template:Namespace detect',
    'Template:Navbar',
    'Template:Navbox',
    'Template:Navbox with collapsible groups',
    'Template:Nowrap',
    'Template:Ns has subpages',
    'Template:Only in print',
    'Template:Quote',
    'Template:Refbegin',
    'Template:Refend',
    'Template:Refimprove',
    'Template:Reflist',
    'Template:Rellink',
    'Template:Sec link/relative url',
    'Template:Sec link/text',
    'Template:Sec link auto',
    'Template:Sec link image',
    'Template:Side box',
    'Template:Sister project links',
    'Template:Small',
    'Template:Transclude',
    'Template:Which?',
    'Template:Wikipedia books'
    ]

    try:
    
        
        pages = query.getElementsByTagName('pages')[0]
        page = pages.getElementsByTagName('page')[0]
        templates = page.getElementsByTagName('templates')[0]
        tl = templates.getElementsByTagName('tl')

        template_list = list()

        for template in tl:
            template_title = template.getAttribute('title')
            template_list.append(template_title)

        return template_list
    except:

        return None

# We do this to filter out bogus templates that are not 'transcluded'
def check_transclusion(nodes):
    for n in nodes:
        if(n.firstChild.data == 'Template:Transclude'):
            return True

    return False


def get_template_body(template):
    ''' 
        Given a template string of format: Template:x, this returns the 
        associated links of that template. 

        These links can effectively serve as sysnonyms

        @template string

        @return dictionary with links
    '''

    params = {
        'action': 'parse',
        'text': '{{' + template.encode('utf-8') + '}}',
        'format': 'xml'
    }

    dom = minidom.parse(wiki_query(params))

    # Try to walk the XML tree until we get the links, if an error occurs,
    # it means this template has no links (it's a 'junk' template)
    try:
        parse = dom.getElementsByTagName('parse')[0]

        transclude = parse.getElementsByTagName('templates')[0]
        tl = transclude.getElementsByTagName('tl')

        if(check_transclusion(tl) == False):
            return None

        links = parse.getElementsByTagName('links')[0]
        pl = links.getElementsByTagName('pl')

        #print "[@] " + template


        metadata = dict()
        matches = list()

        # When we have the links, we want to split them up into a dictionary
        # result that will separate other metadata included in the link text
        # For example, we'll get matches that look like:
        #       Template:x
        #       Category:y
        #       Book:z
        # and so forth... We want to save those for future use.  The final 
        # results will be saved in: 'Template matches'

        for link in pl:
            data = link.firstChild.data
            if(string.find(data, ':') != -1):
                sp = data.split(':')

                if sp[0] in metadata:
                    metadata[sp[0]].append(sp[1])
                else:
                    lst = list()
                    lst.append(sp[1])

                    metadata[sp[0]] = lst
            else:
                matches.append(data)

        # Include the matches in the final results
        metadata['Links'] = matches

        return metadata
        
    except:
        return None 


# Function to get our desired data
def get_wiki_data(title):

    # title = 'Binary tree'

    print "@getting wiki data"

    # Get the categories
    categories = get_wiki_categories_by_title(title)

    # We keep an exclusion list to avoid calling the API for junk templates
    exclusion_list = open_exclusion_list()

    # Get the templates corresponding to a title
    templates = get_templates_by_title(title)

    out_list = []

    for t in templates:
        # get the template body.. if None, then we add the 
        # template to the exclusion list
        
        if t.encode('utf-8') in exclusion_list:
            # print "[x] " + t
            # print "@excluded"
            continue

        template_body = get_template_body(t)

        if(template_body == None):
            exclusion_list.append(t)
        else:
            out_list.append(template_body)


    # Save the final results
    results = {}

    # if(len(categories) != 0):
    #     results['Categories'] = categories

    results[title] = out_list

    save_exclusion_list(exclusion_list)

    return results


def main():
    args = sys.argv[1:]

    params = ' '.join(args)

    # Retrieve disambiguation of a wiki name.  This may be a
    # set of IDs or new titles, or..?
    ids, titles, redirects = get_proper_wiki_titles(params)

    # Give preference to redirects
    title = ""

    if(len(ids) > 0):
        if(len(redirects) > 0):
            title = redirects[0]
        else:
            title = titles[0]

    print "[@] " + title

    tree_data = get_wiki_data(title)

    print json.dumps(tree_data, sort_keys=True, indent=4)
    # pp.pprint(tree_data)
    
 
if __name__ == '__main__':
  main()


