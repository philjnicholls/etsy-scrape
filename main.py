import os
import argparse
import click

from scrape_etsy.scrape_etsy import scrape

def parse_args():
    """Extract arguments from the command line and return in dictionatry

    Parameters:

    Returns:
    dict: A dictionary of command line arguments and values
    """

    parser = argparse.ArgumentParser(description='Scrape product information'
                                     ' from etsy.com into a CSV file.')
    parser.add_argument('url', help='URL for the first page of Etsy search '
                        'results', type=str)
    parser.add_argument('-o', '--output', help='Filepath to output csv',
                        type=str)
    parser.add_argument('-f', '--fail-log', help='Filepath to failure log',
                        type=str)
    parser.add_argument('-l', '--limit', help='Limit scraping to first LIMIT'
                        'products.', type=int)
    parser.add_argument('-d', '--get-details', help='Get full details for a'
                        ' listing.', action='store_true')
    parser.add_argument('-m', '--memcached', help='server:port of memcached '
                        'server to use for caching', type=str)
    args = parser.parse_args()

    return vars(args)

def check_existing_files(output, fail_log):
    """Check if output or fail log files exist and prompt for overwriting

    Parameters:
    output (str): Path to the output CSV file
    fail_log (str): Path to the failure log
    message_callback (function): Callback function for dealing
    with messages

    Returns:
    dict: A dictionary of command line arguments and values
    """
    if output and os.path.exists(output):
        if not click.confirm(f'{output} already exists, do you want to '
                             f'overwrite?', default=True):
            return False
    if fail_log and os.path.exists(fail_log):
        if not click.confirm(f'{fail_log} already exists, do you want to '
                             f'overwrite?', default=True):
            return False

    return True


if __name__ == '__main__':
    args = parse_args()

    if args['output']:
        """If we are writing to a file then we can use stdout to print progress
        and messages"""
        args['message_callback'] = lambda m: print(f'\n{m}')
        args['progress_callback'] = lambda m: print('.', flush=True, end='')

    if check_existing_files(args['output'], args['fail_log']):
        # Only pass argument that are not null
        scrape(**dict(filter(lambda a: a[1], args.items())))
