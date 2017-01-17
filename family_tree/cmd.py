import argparse as ap

def main():

    description = '''
    Read chapter directory information and output a big-little family tree.
    '''

    parser = ap.ArgumentParser(description=description)

    parser.add_argument('directory',
            metavar = 'd',
            type='str',
            help='''path to directory CSV file with the following fields: badge, first_name,
            last_name, preferred_name, status, pledge_semester, big_badge, and
            refounder_class''',
            default='directory.csv',
            )

    parser.add_argument('bnks',
            metavar = 'b',
            type='str',
            help='''path to a CSV storing brothers that were not made knights, with
            the following fields: big_badge, last_name, pledge_semester, and
            status''',
            default='bnks.csv',
            )

    parser.add_argument('chapters',
            metavar = 'h',
            type='str',
            help='''path to a CSV storing chapters with the following fields:
            chapter_designation (in English words, not Greek Letters),
            chapter_location, and chapter_founding''',
            default='chapters.csv',
            )

    parser.add_argument('colors',
            metavar = 'c',
            type='str',
            help='''path to a CSV whose rows map the badge number of a family head
            to a specific Graphviz color, with field names: family and color''',
            default='colors.csv',
            )

    paths = vars(parser.parseargs())



