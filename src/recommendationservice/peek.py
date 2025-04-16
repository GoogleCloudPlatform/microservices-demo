#!/usr/bin/python3
import copy
import datetime
import logging
import optparse
import sys
import time
import yaml
from collections import Counter
from jinja2 import Environment
from jinja2 import FileSystemLoader
from pathlib import Path
from plib import util
from plib import phabapi
from plib import asanaapi
from plib import format


def getname():
    """ get stem name of this script"""
    return Path(__file__).stem


def get_wclass(backend):
    backend_classes = {
        'asana': asanaapi,
        'phab': phabapi,
    }
    return backend_classes[backend]


def get_wobj(backend, config):
    wclass = get_wclass(backend)
    try:
        wobj = wclass.Status(**config['backends'][backend])
        return wobj
    except Exception as e:
        logging.critical('Failed to connect: {}'.format(e))
        sys.exit(1)


def main():

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', default='config.yml', dest="config", type="str")
    parser.add_option('-j', '--job', default='', dest="job", type="str")
    parser.add_option('-p', action='store_true', default=False, dest='echo')
    parser.add_option('-s', action='store_true', default=False, dest='send')
    parser.add_option('-v', action='store_true', default=False, dest='verbose')

    options, remainder = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if options.verbose else logging.INFO,
        format="%(asctime)s:%(levelname)s:%(message)s"
    )
    logging.debug(options)

    def loadconfig(configs):
        out = {}
        for c in configs.split(','):
            if not c:
                continue
            try:
                with open(c, 'r') as ymlfile:
                    v = yaml.load(ymlfile)
                    logging.debug(v)
                    out.update(v)
            except Exception:
                logging.critical('failed to read config file {}'.format(c))
        return out

    cfg = loadconfig(options.config)
    if not cfg:
        sys.exit(1)
        raise Exception('Failure to gather configuration from {}'.format(options.config))

    if options.job:
        logging.debug("Overriding job name to: {}".format(options.job))
        cfg['job'] = options.job

    meta = {}
    meta['starttime'] = time.time()
    meta['enabled_projects'] = []
    meta['enabled_backends'] = []

    total = {}
    total['max'] = max(cfg['history'])
    total['columns'] = {}
    total['projects'] = {}
    total['projects']['history'] = {}
    total['users'] = {}
    total['users']['group'] = {}
    total['users']['group']['assigned'] = []
    total['users']['individual'] = {}
    total['summary_header'] = {}

    total['anti'] = {}

    bes = {}
    for be, beinfo in sorted(cfg['backends'].items(), reverse=True):
        bes[be] = {}
        logging.info('Processing backend: {}'.format(be))

        if not beinfo.get('enabled', False):
            logging.warning('skipping {} as not enabled'.format(be))
            continue

        meta['enabled_backends'].append(be)

        wobj = get_wobj(be, cfg)
        wobj.logger = logging

        # Projects
        projects = {}
        for project in sorted(beinfo['projects'].keys()):
            logging.info('Processing {} project {}'.format(be, project))
            meta['enabled_projects'].append(project)

            projects[project] = {}
            projects[project]['history'] = {}
            projects[project]['show'] = {}

            for duration in sorted(cfg['history'], reverse=True):

                tasks = wobj.get_tasks_created_since(project, duration)
                logging.debug("{}: {} duration at task count {}".format(project, duration, len(tasks)))

                summary_fields = cfg['backends'][be].get('summary_fields', cfg['summary_fields'])

                stats = wobj.tasks_summary(tasks, summary_fields)

                projects[project]['history'][duration] = {}
                projects[project]['history'][duration]['tasks'] = tasks
                projects[project]['history'][duration]['stats'] = stats

                if duration not in total['projects']['history']:
                    total['projects']['history'][duration] = {}
                    total['projects']['history'][duration]['stats'] = copy.deepcopy(stats)

                for field, values in stats.items():
                    thisproj = stats[field]
                    sofar = total['projects']['history'][duration]['stats'][field]
                    new = Counter(thisproj) + Counter(sofar)
                    total['projects']['history'][duration]['stats'][field] = dict(new)

        summary_header = {}
        for project, pinfo in projects.items():
            headers = format.tasks_summary_header(pinfo['history'])
            for k, v in headers.items():
                if k not in summary_header:
                    summary_header[k] = v
                else:
                    summary_header[k] = list(set(summary_header[k] + v))

                if k not in total['summary_header']:
                    total['summary_header'][k] = v
                else:
                    total['summary_header'][k] = list(set(total['summary_header'][k] + v))

        for project, pinfo in projects.items():
            projects[project]['show']['uri'] = wobj.generate_project_link(project)
            projects[project]['history']['summary_table'] = format.tasks_summary_table(summary_header, pinfo['history'])

        # Columns
        for project, pinfo in beinfo['projects'].items():
            projects[project]['columns'] = {}
            for column, id in beinfo['projects'][project]['columns'].items():
                ctasks = wobj.column_tasks(id, project)
                logging.debug('Get {} id {} for {}: {}'.format(column, id, project, len(ctasks)))

                if column not in projects[project]['columns']:
                    projects[project]['columns'][column] = ctasks
                else:
                    projects[project]['columns'][column] += util.dedupe_list_of_dicts(ctasks)

                if column not in total['columns']:
                    total['columns'][column] = ctasks
                else:
                    total['columns'][column] += util.dedupe_list_of_dicts(ctasks)

        if 'anti' in beinfo:
            if 'total' not in total['anti']:
                total['anti']['total'] = 0
            if 'patterns' not in total['anti']:
                total['anti']['patterns'] = {}
            for project, pinfo in projects.items():
                for anti, antidetails in beinfo['anti'].items():
                    if antidetails['name'] not in total['anti']['patterns']:
                        total['anti']['patterns'][antidetails['name']] = []

                    anti_result = getattr(wobj, antidetails['method'])(antidetails, pinfo)
                    if anti_result:
                        logging.info("{} anti found count {}".format(project, len(anti_result)))
                        total['anti']['patterns'][antidetails['name']] += anti_result
                        total['anti']['patterns'][antidetails['name']] = util.dedupe_list_of_dicts(total['anti']['patterns'][antidetails['name']])

            # Create total out of deduped list counts
            for pattern, matches in total['anti']['patterns'].items():
                total['anti']['total'] += len(matches)

        bes[be]['projects'] = projects
        # Users
        report_users = cfg['users']['map']
        users = {}

        if 'count' not in total['users']:
            total['users']['group']['count'] = len(report_users)

        for u, be_matches in report_users.items():
            users[u] = {}
            users[u]['details'] = wobj.get_member_info(u, be_matches[be])

        logging.debug('{} member details'.format(be))

        for u, uinfo in users.items():

            for sa, sa_info in cfg['users']['attributes']['show'].items():
                sa_backend = sa_info['backend']
                sa_key = sa_info['key']
                if be == sa_backend:
                    uinfo[sa_key] = uinfo['details'][sa]

            if u not in total['users']['individual']:
                total['users']['individual'][u] = {}

            if 'stats' not in users[u]:
                users[u]['stats'] = {}

            assigned = wobj.user_assigned(uinfo['details'])
            if 'assigned' not in users[u]:
                users[u]['stats']['assigned'] = assigned

            total['users']['group']['assigned'] += util.dedupe_list_of_dicts(assigned)

            if 'stats' not in total['users']['individual'][u]:
                total['users']['individual'][u]['stats'] = {}

            if 'assigned' not in total['users']['individual'][u]['stats']:
                total['users']['individual'][u]['stats']['assigned'] = []

            total['users']['individual'][u]['stats']['assigned'] += util.dedupe_list_of_dicts(assigned)

            if 'anti' in cfg['users']:

                if 'antipatterns' not in total['users']['individual'][u]['stats']:
                    total['users']['individual'][u]['stats']['antipatterns'] = []

                if 'antipatterns' not in total['users']['group']:
                    total['users']['group']['antipatterns'] = []

                users[u]['antipatterns'] = {}
                for anti, antidetails in cfg['users']['anti'].items():
                    anti_result = getattr(wobj, antidetails['method'])(assigned, antidetails, bes[be])
                    logging.debug("{} {} {}".format(u, anti, len(anti_result)))
                    if not anti_result:
                        continue

                    if antidetails['name'] not in users[u]['antipatterns']:
                        users[u]['antipatterns'][antidetails['name']] = {}
                    users[u]['antipatterns'][antidetails['name']]['all'] = anti_result
                    total['users']['individual'][u]['stats']['antipatterns'] += anti_result
                    total['users']['group']['antipatterns'] += anti_result
                    logging.info('{} {} assigned {} {} {}'.format(u, be, len(assigned), antidetails['name'], len(anti_result)))

                    users[u]['antipatterns'][antidetails['name']]['shown'] = []
                    m_shown = users[u]['antipatterns'][antidetails['name']]['all'][:antidetails['show']]
                    for task in m_shown:
                        users[u]['antipatterns'][antidetails['name']]['shown'].append(wobj.generate_task_link(task))

            time.sleep(beinfo.get('query_delay', .5))

        bes[be]['users'] = users

    total['projects']['history']['summary_table'] = format.tasks_summary_table(total['summary_header'], total['projects']['history'])

    env = Environment(
        loader=FileSystemLoader(cfg['templates']))

    template = env.get_template('body.html')

    meta['runtime'] = int(time.time() - meta['starttime'])
    meta['name'] = getname()

    data = [meta, bes, cfg, total]
    template.globals['now'] = int(time.time())
    output = template.render(data=data)

    if options.echo:
        print(output)

    if options.send:
        now = datetime.datetime.now()
        subject = "{} {}".format(cfg['job'], now.strftime('%Y-%m-%d'))
        logging.info("{} sending email '{}'".format(meta['name'], subject))
        util.send_email(
            cfg['email']['from'],
            cfg['email']['to'],
            subject,
            output,
            cfg['email']['server']
        )


main()
