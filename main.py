import os
import argparse
import click

import scrape_etsy

def parse_args():
    """Extract arguments from the command line and return in dictionatry

    Parameters:

    Returns:
    dict: A dictionary of command line arguments and values
    """

    parser = argparse.ArgumentParser(description='Scrape product information'
                                     ' from etsy.com into a CSV file.')
    parser.add_argument('url', help='URL for the first page of Etsy search'
                        'results', type=str)
    parser.add_argument('output', help='Filepath to output csv',
                        type=str,
                        default='output.csv')
    parser.add_argument('-f', '--fail-log', help='Filepath to failure log',
                        type=str, default='fail.log')
    parser.add_argument('-l', '--limit', help='Limit scraping to first LIMIT'
                        'products.', type=int)
    parser.add_argument('-d', '--get-details', help='Get full details for a'
                        ' listing.', action='store_true')
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
    if os.path.exists(output):
        if not click.confirm(f'{output} already exists, do you want to '
                             f'overwrite?', default=True):
            return False
    if os.path.exists(fail_log):
        if not click.confirm(f'{fail_log} already exists, do you want to '
                             f'overwrite?', default=True):
            return False

    return True


if __name__ == '__main__':
    args = parse_args()

    if check_existing_files(args['output'], args['fail_log']):
        scrape_etsy.scrape_etsy(**args, progress_callback=lambda m: print('.', flush=True, end=''))
