#!/usr/bin/python
# /* vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4: */

import os, re, time
import logging

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()
logging.debug('Starting')

descriptors = []
stats = {}
last_update = 0

MAX_UPDATE = 5
LLITE_DIR = "/proc/fs/lustre/llite"

def update_stats():
    logging.debug('update_stats')
    global last_update, stats

    cur_time = time.time()
    if cur_time - last_update < MAX_UPDATE:
        logging.debug('skipping update')
        return True

    stats = get_llite_stats(LLITE_DIR)

    logging.debug(stats)
    last_update = cur_time

##############################################################################
def get_llite_value(key, item):
    item.extend([None] * 6)
    return {
        'read_bytes'  : item[5],
        'write_bytes' : item[5],
        'snapshot_time' : int(float(item[0])),
    }.get(key, item[0])

def llite_fs(directory):
    for fs in os.listdir(directory):
        fs_name, _, fs_id = fs.partition('-')
        yield fs_name

def get_llite_stats(directory):
    out = {}

    for fs in os.listdir(directory):
        llite_stats = open("%s/%s/stats" % (directory, fs))

        fs_name, _, fs_id = fs.partition('-')

        for line in llite_stats:
            item = re.split("\s+", line.rstrip())
            key = item.pop(0)
            out['lustre_' + fs_name + '_' + key] = int(get_llite_value(key, item))

    return out
##############################################################################

def create_desc(skel, prop):
    d = skel.copy()
    for k, v in prop.iteritems():
        d[k] = v
    return d

def get_value(key):
    update_stats()

    return stats[key]

def metric_init(params):
    global descriptors
    logging.debug('metric_init: ' + str(params))
    update_stats()

    Desc_Skel = {
        'name'        : 'XXX',
        'call_back'   : get_value,
        'time_max'    : 60,
        'value_type'  : 'uint',
        'format'      : '%u',
        'units'       : 'ops',
        'slope'       : 'positive', # zero|positive|negative|both
        'description' : 'XXX',
        'groups'      : 'lustre',
    }

    for fs in llite_fs(LLITE_DIR):
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_dirty_pages_hits',
            'description' : 'Dirty page hits from %s' % fs,
            'units'       : 'hits/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_dirty_pages_misses',
            'description' : 'Dirty page misses from %s' % fs,
            'units'       : 'misses/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_read_bytes',
            'description' : 'Bytes read from %s' % fs,
            'units'       : 'bytes/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_write_bytes',
            'description' : 'Bytes written to %s' % fs,
            'units'       : 'bytes/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_brw_read',
            'description' : 'brw_read calls to %s' % fs,
            'units'       : 'pages/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_ioctl',
            'description' : 'ioctl calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_open',
            'description' : 'open calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_close',
            'description' : 'close calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_mmap',
            'description' : 'mmap calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_seek',
            'description' : 'seek calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_truncate',
            'description' : 'truncate calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_getattr',
            'description' : 'getattr calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_statfs',
            'description' : 'statfs calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_alloc_inode',
            'description' : 'alloc_inode calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_setxattr',
            'description' : 'setxattr calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_getxattr',
            'description' : 'getxattr calls to %s' % fs,
            'units'       : 'calls/s',
        }))
        descriptors.append(create_desc(Desc_Skel, {
            'name'        : 'lustre_' + fs + '_inode_permission',
            'description' : 'inode_permission calls to %s' % fs,
            'units'       : 'calls/s',
        }))

    # Remove descriptors that aren't in our stats data
    descriptors = [d for d in descriptors if (d['name'] in stats)]

    return descriptors

def metric_cleanup():
    '''Clean up the metric module.'''
    pass

# For testing
if __name__ == '__main__':
    metric_init({})
    for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %d' % (d['name'],  v)

