import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = dict ()
    if corpus[page]:
        for link in corpus:
            distribution[link] = (1-damping_factor) / len(corpus)
            if link in corpus[page]:
                distribution[link] += damping_factor / len(corpus[page])
        return distribution
    for link in corpus:
        distribution[link] = 1 / len(corpus)            
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict(zip(corpus.keys(), [0] * len(corpus)))
    sample = random.choice(list(corpus.keys()))
    for item in range(n):        
        distribution = transition_model(corpus, sample, damping_factor)
        sample = random.choices(list(distribution.keys()), distribution.values())[0]
        pagerank[sample] += 1
    for item in corpus:
        pagerank[item] /= n
    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageranks = dict(zip(corpus.keys(), [1/len(corpus)] * len(corpus)))
    new_pagerank = dict()
    proceed = True
    while proceed:
        for item in pageranks:
            prob = float(0)            
            for page, links in corpus.items():
                if not links:
                    links = corpus.keys()
                if item in links:
                    prob += pageranks[page] / len(links)
            new_pagerank[item] = (1 - damping_factor) / len(corpus) + damping_factor * prob
        proceed = False
        for page in pageranks:
            if not math.isclose(new_pagerank[page], pageranks[page], abs_tol=0.001):
                proceed = True
            pageranks[page] = new_pagerank[page]            
    return pageranks


if __name__ == "__main__":
    main()
