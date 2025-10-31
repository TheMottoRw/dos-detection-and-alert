import re, sys, subprocess
from api.webmonitor import constants

# import constants

domain_whois_info = []


def run_whois_command(domain):
    cmd = 'whois'
    data = {}
    if sys.platform == 'linux':
        # remove domain prefix:
        domaine = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, '', domain)
        gov_pattern = re.compile('([a-z://]+.gov.rw)')
        gov_found = gov_pattern.findall(domaine)
        if len(gov_found) > 0 and domaine != "gov.rw":
            domain_whois_info.append([domain, ''])
        else:
            output = subprocess.run([cmd, domaine], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT).stdout.decode('UTF-8')
            if output.__contains__("Lookup quota exceeded"):
                return None

            data = decode_whois_info(domain, output)

    return data
    # domain_whois_info.append([domain, ''])


def decode_whois_info(domain, output):
    response = []
    decoded_object = {}
    # print(output)
    pattern_keyword = ["Registrant", "Admin", "Billing", "Registrar", "Registry", "Name Server", "Creation Date"
        , "Updated Date"]
    for patt in pattern_keyword:
        nameserver_list = []
        decoded_object[patt.lower().replace(" ", "_")] = {}
        # pattern = re.compile("([a-zA-Z ]+ " + patt + ":(:?)[a-zA-Z0-9.@+:\- ]+)\\n")  # str pattern
        pattern = re.compile(patt + "[a-zA-Z0-9.@+:'\- ]+\\n")  # str pattern
        out = pattern.findall(output)
        # loop output array,split by : and format into json
        for item in out:
            # print("Keypattern " + item)
            item_arr = item.split(":")
            if patt == "Name Server":
                nameserver_list.append(item_arr[1].strip())
            else:
                if patt.endswith("Date"):
                    key = item_arr.pop(0)
                    val = ":".join(str(i) for i in item_arr)
                    decoded_object[str(patt.lower().replace(" ", "_"))] = val.strip()
                elif len(item_arr) > 2:
                    key = item_arr.pop(0)
                    val = ":".join(str(i) for i in item_arr)
                    decoded_object[str(patt.lower().replace(" ", "_"))][
                        key.lower().replace(" ", "_").replace(key.lower() + "_", "").replace(patt.lower() + "_",
                                                                                             "")] = val.strip()
                else:
                    decoded_object[str(patt.lower().replace(" ", "_"))][
                        str(item_arr[0].lower().replace(" ", "_").replace(patt.lower() + "_", ""))] = \
                        item_arr[1].strip() if len(item_arr) > 1 else ""
        if patt == "Name Server":
            decoded_object[str(patt.lower().replace(" ", "_"))] = nameserver_list
        # print(obj)

    with open(f"{constants.DATA_PATH}/whoisinfo.json", "w") as f:
        f.write(str(decoded_object).replace('\'', '"'))
    domain_whois_info.append([domain, response])
    # write_domains_to_file(domain_whois_info)
    return decoded_object

    # print(response)


def run_nslookup_command(domain):
    cmd = 'nslookup'
    data = {}
    # remove domain prefix
    domaine = re.sub(constants.REMOVE_DOMAIN_PREFIX_PATTERN, '', domain)
    print(domaine)
    gov_pattern = re.compile('([a-z://]+.gov.rw)')
    gov_found = gov_pattern.findall(domaine)

    try:
        output = subprocess.run([cmd, domaine], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT).stdout.decode('UTF-8')
        nslookup_addr_pattern = re.compile("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})")
        domain_addr = nslookup_addr_pattern.findall(output)
        if len(domain_addr) > 2:
            domain_addr.pop(0)
            domain_addr.pop(0)
            data[domaine] = domain_addr
    except Exception as ex:
        print("NSLOOKUP::Something went wrong " + str(ex),True)
    return data


def check_ip_status(ip,waiting_time=2):
    cmd = 'ping'
    data = {}
    keys = ["transmitted", "received", "lost_percentage", "time_used_ms"]
    percentage_pattern = "[0-9]+"
    try:
        output = subprocess.run([cmd, ip, "-w", str(waiting_time)], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT).stdout.decode('UTF-8')
        ping_pattern = re.compile(constants.PING_RESPONSE_PATTERN)
        data = ping_pattern.findall(output)
        if len(data) > 0:
            received_percentage_loss_patt = re.compile(percentage_pattern)
            received_percentage_loss = received_percentage_loss_patt.findall(data[0])
            if len(received_percentage_loss) > 0:
                data = dict(zip(keys, received_percentage_loss))
    except Exception as ex:
        print(f"SOPHOS PING Error::{ip} - {data} - " + str(ex),True)
    return data


if __name__ == "__main__":
    print(sys.argv)
    data: dict = run_whois_command(sys.argv[1])
    print(data)
    if data:
        print(sys.argv[1], ":",
              data.get("registry").get("expiry_date") if data.get("registry") != {} else "Quota Exceed")
    else:
        print("Quota exceeded")

