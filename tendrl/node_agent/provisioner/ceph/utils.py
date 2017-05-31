import json
import os
import struct
import time
import base64

DEFAULT_JOURNAL_SIZE = 5 * 1024 * 1024 * 1024
MAX_JOURNALS_ON_SSDS = 4


def generate_auth_key():
    """
    Generates a secret key to be used in ceph cluster keyring.

    It generates a base64 encoded string out of a byte string
    created by packing random data into struct. This is used
    while cluster creation as keyring secret key
    """

    key = os.urandom(16)
    header = struct.pack(
        '<hiih',
        1,                 # le16 type: CEPH_CRYPTO_AES
        int(time.time()),  # le32 created: seconds
        0,                 # le32 created: nanoseconds,
        len(key),          # le16: len(key)
    )
    return base64.b64encode(header + key).decode('utf-8')


def generate_journal_mapping(node_configuration, integration_id=None):

    """This fuction works based on a simple algorithm which maps
    smaller sized disks as journal for bigger sized disks.
    To achieve this, it first sorts the list of disks based on
    size in descending order and then start the mapping of disks
    with their journal disks.

    There are below listed four scenarios to be handled

    CASE-1: All the disks are rotational
    RESTRICTION: In this case one disk can be used as journal
    for one disk only
    LOGIC: Here the logic is very simple. If the no of disks is
    even, the valid possible no of OSDs would be (no of disks / 2)
    else if the no of disks is  odd, the valid no of OSDs would be
    (no of disks - 1) / 2. Now in sorted list of disks on descending
    size, first half set of disks get mapped to second half set of
    disks to use them as journals.

    CASE-2: All the disks are SSDs
    RESTRICTION: In this case one disk can be used as journal for
    upto 4 disks
    LOGIC: Here in sorted list of disks on descending size, it starts
    from first disk and starts mapping the last entry in the list as
    journal. Once 4 disks are mapped to last entry in list, next set
    of disks start mapping to one but last disk in list as their
    journal. This continues till all the disks are mapped to their
    journals. Also while mapping disks to their journal, if no more
    space available on journal disk, it moves mapping to the next
    higher sized disk from last.
    The below diagram explains the logic well

    ----------------------------------------------------
    |    -----------------------------------------------
    |    |    ------------------------------------------
    |    |    |    -------------------------------------
    |    |    |    |    -------------------------|    |
    |    |    |    |    |    --------------------|    |
    |    |    |    |    |    |    ---------------|    |
    |    |    |    |    |    |    |    ----------|    |
    |    |    |    |    |    |    |    |         |    |
    |    |    |    |    |    |    |    |         |    |
    ---  ---  ---  ---  ---  ---  ---  ---  ---  ---  ----
    |0|  |1|  |2|  |3|  |4|  |5|  |6|  |7|  |8|  |9|  |10|
    ---  ---  ---  ---  ---  ---  ---  ---  ---  ---  ----

    CASE-3: Few disks are rotational and few are SSDs
    RESTRICTION: First SSDs should be used as journals and a maximum
    of 4 disks can use one SSD as journal.
    LOGIC: In this case, first it segregates the list of SSDs and
    rotational disks. Then starts mapping SSD disk as journal for
    rotational disk. Once already 4 disks marked to use an SSD as
    journal or no space available in the selected SSD, it moves to
    next SSD to use as journal.
    After this mapping done, we might end up in a situation where
    more rotational or SSDs disks are left

    SUB CASE-3a: More rotational disks left
    LOGIC: Logic in case-1 is repeated for the left out disks

    SUB CASE-3b: More SSDs are left
    LOGIC: Logic in case-2 is repeated for the left out disks
    """

    mapping = {}
    for node_id in node_configuration.keys():

        # Get the node specific journal details from central store
        # if integration_id is passed. This is the case when this
        # utility is called during expand cluster. We should check
        # if pre-existing journal details available for the node
        # and consider any SSD disk available for journal mapping
        if integration_id and NS.integrations.ceph.objects.Journal(
            integration_id=integration_id,
            node_id=node_id).exists():
            journal_details = json.loads(NS.integrations.ceph.objects.Journal(
                integration_id=integration_id,
                node_id=node_id
            ).load().data)

        ssd_count = hdd_count = osd_count = 0
        storage_disks = node_configuration[node_id]['storage_disks']
        for storage_disk in storage_disks:
            if storage_disk['ssd']:
                ssd_count += 1
            else:
                hdd_count += 1

        # If all the disks are rotational in nature
        mapped_storage_disks = []
        unallocated_disks = []
        if hdd_count == len(storage_disks):
            sorted_disks = sort_disks_on_size(storage_disks)
            if len(storage_disks) % 2 == 0:
                valid_count = len(storage_disks) / 2
            else:
                valid_count = (len(storage_disks) - 1) / 2
            for index in range(0, valid_count):
                mapped_storage_disks.append(
                    {
                        "device": sorted_disks[index]['device'],
                        "journal": sorted_disks[
                            (len(sorted_disks) - index) - 1
                        ]['device']
                    }
                )
            unallocated_disks = get_unallocated_disks(
                storage_disks, mapped_storage_disks
            )
            mapping[node_id] = {
                "storage_disks": mapped_storage_disks,
                "unallocated_disks": unallocated_disks
            }
            continue

        # All the disks are SSD
        journal_disk_idx = mapped_disk_count_for_journal = 0
        ssd_disk_size = 0
        if ssd_count == len(storage_disks):
            sorted_disks = sort_disks_on_size(storage_disks)
            ssd_disk_size = sorted_disks[
                len(sorted_disks) - journal_disk_idx - 1
            ]['size']
            for index in range(0, len(sorted_disks) - journal_disk_idx - 2):
                ssd_disk_size = ssd_disk_size - DEFAULT_JOURNAL_SIZE

                # If already max possible journals mapped on SSD continue
                if integration_id and journal_details:
                    mapped_disk_count_for_journal = journal_details[
                        sorted_disks[
                            len(sorted_disks) - journal_disk_idx - 1
                        ]['device']
                    ]['journal_count']
                    if mapped_disk_count_for_journal == MAX_JOURNALS_ON_SSDS:
                        continue

                mapped_disk_count_for_journal += 1
                if integration_id and journal_details:
                    journal_details[
                        sorted_disks[
                            len(sorted_disks) - journal_disk_idx - 1
                        ]['device']
                    ]['journal_count'] = mapped_disk_count_for_journal
                osd_count += 1
                mapped_storage_disks.append(
                    {
                        "device": sorted_disks[index]['device'],
                        "journal": sorted_disks[
                            len(sorted_disks) - journal_disk_idx - 1
                        ]['device']
                    }
                )
                if mapped_disk_count_for_journal == MAX_JOURNALS_ON_SSDS or \
                    ssd_disk_size < DEFAULT_JOURNAL_SIZE:
                    mapped_disk_count_for_journal = 0
                    journal_disk_idx += 1
                    ssd_disk_size = sorted_disks[
                        len(sorted_disks) - journal_disk_idx - 1
                    ]['size']
            unallocated_disks = get_unallocated_disks(
                storage_disks, mapped_storage_disks
            )
            mapping[node_id] = {
                "storage_disks": mapped_storage_disks,
                "unallocated_disks": unallocated_disks
            }
            continue

        # If few of the disks are SSD and few rotational in nature
        ssd_disks = []
        hdd_disks = []
        for storage_disk in storage_disks:
            if storage_disk['ssd']:
                ssd_disks.append(storage_disk)
            else:
                hdd_disks.append(storage_disk)

        journal_disk_idx = mapped_disk_count_for_journal = 0
        for hdd_disk in hdd_disks:
            if journal_disk_idx < len(ssd_disks):
                ssd_disk_size = ssd_disks[journal_disk_idx]['size'] - \
                    DEFAULT_JOURNAL_SIZE * \
                    (mapped_disk_count_for_journal + 1)

                # If already max possible journals mapped on SSD continue
                if integration_id and journal_details:
                    mapped_disk_count_for_journal = journal_details[
                        ssd_disks[journal_disk_idx]['device']
                    ]['journal_count']
                    if mapped_disk_count_for_journal == MAX_JOURNALS_ON_SSDS:
                        continue

                mapped_disk_count_for_journal += 1
                if integration_id and journal_details:
                    journal_details[
                        ssd_disks[journal_disk_idx]['device']
                    ]['journal_count'] = mapped_disk_count_for_journal
                osd_count += 1
                mapped_storage_disks.append(
                    {
                        "device": hdd_disk['device'],
                        "journal": ssd_disks[journal_disk_idx]['device']
                    }
                )
                if mapped_disk_count_for_journal == MAX_JOURNALS_ON_SSDS \
                    or ssd_disk_size < DEFAULT_JOURNAL_SIZE:
                    mapped_disk_count_for_journal = 0
                    journal_disk_idx += 1
            else:
                break
        # If still ssd disks pending map them among themselves
        # There should not be any rotational disks left out by this time
        if journal_disk_idx < len(ssd_disks):
            pending_disks = []
            for index in range(journal_disk_idx, len(ssd_disks)):
                pending_disks.append(ssd_disks[index])
            sorted_disks = sort_disks_on_size(pending_disks)

            journal_disk_idx = mapped_disk_count_for_journal = 0
            ssd_disk_size = sorted_disks[
                len(sorted_disks) - journal_disk_idx - 1
            ]['size']
            for index1 in range(0, len(sorted_disks) - journal_disk_idx - 1):
                ssd_disk_size = ssd_disk_size - DEFAULT_JOURNAL_SIZE

                # If already max possible journals mapped on SSD continue
                if integration_id and journal_details:
                    mapped_disk_count_for_journal = journal_details[
                        sorted_disks[
                            len(sorted_disks) - journal_disk_idx - 1
                        ]['device']
                    ]['journal_count']
                    if mapped_disk_count_for_journal == MAX_JOURNALS_ON_SSDS:
                        continue

                mapped_disk_count_for_journal += 1
                if integration_id and journal_details:
                    journal_details[
                        sorted_disks[
                            len(sorted_disks) - journal_disk_idx - 1
                        ]['device']
                    ]['journal_count'] = mapped_disk_count_for_journal
                osd_count += 1
                mapped_storage_disks.append(
                    {
                        "device": sorted_disks[index1]['device'],
                        "journal": sorted_disks[
                            len(sorted_disks) - journal_disk_idx - 1
                        ]['device']
                    }
                )
                if mapped_disk_count_for_journal == MAX_JOURNALS_ON_SSDS or \
                    ssd_disk_size < DEFAULT_JOURNAL_SIZE:
                    mapped_disk_count_for_journal = 0
                    journal_disk_idx += 1
                    ssd_disk_size = sorted_disks[
                        len(sorted_disks) - journal_disk_idx - 1
                    ]['size']
            unallocated_disks = get_unallocated_disks(
                storage_disks, mapped_storage_disks
            )
            mapping[node_id] = {
                "storage_disks": mapped_storage_disks,
                "unallocated_disks": unallocated_disks
            }
            continue

        # If still left with rotational disks, map them among themselves
        if osd_count < len(hdd_disks):
            pending_disks = []
            pending_disk_count = len(hdd_disks) - osd_count
            for index in range(osd_count, len(hdd_disks)):
                pending_disks.append(hdd_disks[index])
            sorted_disks = sort_disks_on_size(pending_disks)

            if pending_disk_count % 2 == 0:
                valid_count = pending_disk_count / 2
            else:
                valid_count = (pending_disk_count - 1) / 2
            for index in range(0, valid_count):
                mapped_storage_disks.append(
                    {
                        "device": sorted_disks[index]['device'],
                        "journal": sorted_disks[
                            len(pending_disks) - index - 1
                        ]['device']
                    }
                )
            unallocated_disks = get_unallocated_disks(
                storage_disks, mapped_storage_disks
            )
            mapping[node_id] = {
                "storage_disks": mapped_storage_disks,
                "unallocated_disks": unallocated_disks
            }
            continue

        mapping[node_id] = {
            "storage_disks": mapped_storage_disks,
            "unallocated_disks": unallocated_disks
        }


    return mapping


def sort_disks_on_size(disks):
    if len(disks) <= 1:
        return disks

    mid = len(disks) / 2
    left = disks[:mid]
    right = disks[mid:]

    left = sort_disks_on_size(left)
    right = sort_disks_on_size(right)

    return merge(left, right)


def merge(left, right):
    result = []
    while len(left) > 0 or len(right) > 0:
        if len(left) > 0 and len(right) > 0:
            if left[0]['size'] >= right[0]['size']:
                result.append(left[0])
                left = left[1:]
            else:
                result.append(right[0])
                right = right[1:]
        elif len(left) > 0:
            result.append(left[0])
            left = left[1:]
        elif len(right) > 0:
            result.append(right[0])
            right = right[1:]
    return result

def get_unallocated_disks(full_list, mapped_disks):
    old_list = []
    for storage_disk in full_list:
        old_list.append(storage_disk['device'])
    allocated_disks = []
    for mapped_disk in mapped_disks:
        allocated_disks.append(mapped_disk['device'])
        allocated_disks.append(mapped_disk['journal'])
    return list(set(old_list) - set(allocated_disks))
