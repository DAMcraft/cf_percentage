import threading
from urllib.request import Request, urlopen
import socket
import textwrap
from typing import List, Tuple

thread_count = 100


def get_100k_domains() -> List[str]:
    domain_list = []
    with open('100k.csv', 'r') as f:
        for line in f.readlines()[1:]:  # Skip the header of the CSV
            domain_list.append(line.strip())
    return domain_list


def get_cf_ranges() -> List[range]:
    # https://www.cloudflare.com/ips-v4 contains a list of Cloudflare IP ranges
    req = Request('https://www.cloudflare.com/ips-v4', headers={'User-Agent': ''})
    response = urlopen(req)
    cf_ips = response.read().decode('utf-8').split('\n')
    cf_ranges = []
    for ip in cf_ips:
        cf_ranges.append(cidr_to_range(ip))
    return cf_ranges


def is_in_ranges(ip_as_int: int, ranges: List[range]) -> bool:
    # Check if an IP address is in a list of ranges
    for r in ranges:
        if ip_as_int in r:
            return True
    return False


def cidr_to_range(cidr: str) -> range:
    # Convert a CIDR notation to a range of IP addresses
    # Example:
    # cidr_to_range('127.0.0.1/24') -> range(2130706432, 2130706687)
    ip, mask = cidr.split('/')
    ip = ip_to_int(ip)
    mask = (1 << 32) - (1 << (32 - int(mask)))
    return range(ip, ip + mask)


def ip_to_int(ip):
    # Simple function to convert an IP address to a decimal format
    # Allows you to check simply if an IP is in a range
    # Example:
    # ip_to_int('127.0.0.1') -> 2130706433
    return int(''.join([f'{int(octet):08b}' for octet in map(int, ip.split('.'))]), 2)


def is_cf_domain(domain: str, cf_ranges: List[range]) -> bool:
    # Check if a domain is a Cloudflare domain,
    # by resolving it to an IP address and checking if it's in the Cloudflare ranges
    ip = socket.gethostbyname(domain)
    ip_as_int = ip_to_int(ip)
    return is_in_ranges(ip_as_int, cf_ranges)


def check_domains_threaded(domains: List[str], cf_ranges: List[range], response_list: list, index: int):
    # Check if a list of domains are Cloudflare domains
    # Returns a tuple with the number of Cloudflare domains and the number of non-Cloudflare domains
    # Ignores domains that don't resolve to an IP address
    cf_domains = 0
    non_cf_domains = 0
    unresolved_domains = 0
    for i, domain in enumerate(domains):
        if index == 0:
            print(f'Approximately {i / len(domains):.2%} done', end='\r')
        try:
            if is_cf_domain(domain, cf_ranges):
                cf_domains += 1
            else:
                non_cf_domains += 1
        except socket.gaierror:
            unresolved_domains += 1

    response_list[index] = (cf_domains, non_cf_domains, unresolved_domains)


def main():
    print(textwrap.dedent(
        '''\
        This script is not meant to be run on your local machine.
        It will generate a lot of traffic (100k DNS lookups), which may lead to your Internet not working for a while.
        It is recommended to run this program on a server or a cloud instance.
        '''
    ))
    should_continue = input('Do you want to continue anyway? (y/n) ')
    if should_continue.lower() != 'y':
        print('Exiting...')
        return
      
    cf_ranges = get_cf_ranges()
    domains = get_100k_domains()
    domains_per_thread = len(domains) // (thread_count - 1)
    batches = [domains[i:i + domains_per_thread] for i in range(0, len(domains), domains_per_thread)]
    results: List[Tuple[int, int] | None] = [None] * thread_count
    threads = []
    for i, batch in enumerate(batches):
        t = threading.Thread(
            target=check_domains_threaded,
            args=(batch, cf_ranges, results, i)
        )
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    total_cf = 0
    total_non_cf = 0
    unresolved_domains = 0
    for result in results:
        if result is None:
            continue
        total_cf += result[0]
        total_non_cf += result[1]
        unresolved_domains += result[2]
    print(f'Total Cloudflare domains: {total_cf}')
    print(f'Total non-Cloudflare domains: {total_non_cf}')
    print(f'Total unresolved domains: {unresolved_domains}')


if __name__ == '__main__':
    main()
