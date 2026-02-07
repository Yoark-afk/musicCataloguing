import os.path

from crawl_carl_nielsen_works import crawl_carl_nielsen_works
from crawl_frederick_delius_works import crawl_frederick_delius_works

if __name__ == "__main__":
    carl_nielsen_works = crawl_carl_nielsen_works(os.path.join('xml-files', 'Carl Nielsen'))
    print(len(carl_nielsen_works))
    for work in carl_nielsen_works:
        print(work)
    with open('Carl Nielsen.txt', 'w') as f:
        for work in carl_nielsen_works:
            f.write(str(work))
            f.write('\n')

    frederick_delius_works = crawl_frederick_delius_works(os.path.join('xml-files', 'Frederick Delius'))
    print(len(frederick_delius_works))
    for work in frederick_delius_works:
        print(work)
    with open('Frederick Delius.txt', 'w') as f:
        for work in frederick_delius_works:
            f.write(str(work))
            f.write('\n')
