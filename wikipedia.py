import wikipediaapi
wiki_wiki = wikipediaapi.Wikipedia('MyProjectName (merlin@example.com)', 'en')

page_py = wiki_wiki.page('Language Modeling')

print("Page - Title: %s" % page_py.title)


print("Page - Summary: %s" % page_py.summary)
