#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Waiting queue
import time
from datetime import timedelta, date, datetime


class WaitQueue(object):
    """ Waiting queue. """

    def __init__(self, active_span=timedelta(minutes=10)):
        """
        Queue top is active.
        self.queue' s item: {
                'ssid': session.id,
                'time': client last accessed time, }
        Only queue top adding property 'active_start'
        self.queue' s item: {
                'ssid': session.id,
                'time': client last accessed time,
                'active_start': using resource start time, }
        """
        self.queue = []
        self.expire_span = timedelta(minutes=5)
        self.active_span = active_span

    def queue_pop(self, i):
        """ Pop indexed item form self.queue and
        adding 'active_start' key in queue[0] if replace queue[0].
        >>> q=WaitQueue()
        >>> q.entry('foo', datetime(2016, 8, 3, 15, 49, 10, 61274))
        >>> q.entry('bar', datetime(2016, 8, 3, 15, 52, 50, 218))
        >>> q.entry('tee', datetime(2016, 8, 3, 15, 54, 23, 788854))
        >>> q.queue_pop(3)
        >>> len(q.queue)
        3
        >>> q.queue_pop(0)
        >>> len(q.queue)
        2
        >>> 'active_start' in q.queue[0]
        True
        """
        try:
            self.queue.pop(i)
        except IndexError:
            return
        except:
            logger.warning("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            if len(self.queue) > 0:
                if 'active_start' not in self.queue[0]:
                    self.queue[0]['active_start'] = datetime.today()

    def exist_session(self, session_id):
        """ if exist session_id then return queue index else -1.

        >>> q=WaitQueue()
        >>> q.exist_session('hoge')
        -1
        >>> q.entry('foo', datetime(2016, 8, 3, 15, 49, 10, 61274))
        >>> q.entry('bar', datetime(2016, 8, 3, 15, 52, 50, 218))
        >>> q.entry('tee', datetime(2016, 8, 3, 15, 54, 23, 788854))
        >>> q.exist_session('bar')
        1
        >>> q.exist_session('hoge')
        -1
        """
        ret = -1
        try:
            ret = [s['ssid'] for s in self.queue].index(session_id)
        except ValueError:
            pass        # ret = -1
        except:
            raise       # unexpected error.
        return ret

    def entry(self, session_id, last_time):
        """ exist session update or new session entry append queue last.

        >>> q=WaitQueue()
        >>> q.queue
        []
        >>> q.entry('foo', datetime(2016, 8, 3, 15, 49, 10, 61274))
        >>> len(q.queue)
        1
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[0])
        's=foo,2016-08-03 15:49:10.061274.'
        >>> q.entry('bar', datetime(2016, 8, 3, 15, 52, 50, 218))
        >>> q.entry('tee', datetime(2016, 8, 3, 15, 54, 23, 788854))
        >>> len(q.queue)
        3
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[0])
        's=foo,2016-08-03 15:49:10.061274.'
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[1])
        's=bar,2016-08-03 15:52:50.000218.'
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[2])
        's=tee,2016-08-03 15:54:23.788854.'
        >>> q.entry('bar', datetime(2016, 8, 3, 15, 56, 15, 288239))
        >>> len(q.queue)
        3
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[0])
        's=foo,2016-08-03 15:49:10.061274.'
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[1])
        's=bar,2016-08-03 15:56:15.288239.'
        >>> 's={0[ssid]},{0[time]}.'.format(q.queue[2])
        's=tee,2016-08-03 15:54:23.788854.'
        """
        i = self.exist_session(session_id)
        if i > -1:
            self.queue[i]['time'] = last_time
        else:
            self.queue.append({'ssid': session_id,
                               'time': last_time, })

    def alive(self, session_id, last_time):
        """ update self.que_time in queue entry.
        :return: -1;not exist entry (or expiered), 0 and over; now queue index
        >>> q=WaitQueue()
        >>> d = {}
        >>> d['foo'] = datetime.today()
        >>> d['bar'] = datetime.today()
        >>> d['tee'] = datetime.today()
        >>> q.entry('foo', d['foo'])
        >>> q.entry('bar', d['bar'])
        >>> q.entry('tee', d['tee'])
        >>> len(q.queue)
        3
        >>> 's={0[ssid]}.'.format(q.queue[0])
        's=foo.'
        >>> q.queue[0]['time'] == d['foo']
        True
        >>> 's={0[ssid]}.'.format(q.queue[1])
        's=bar.'
        >>> q.queue[1]['time'] == d['bar']
        True
        >>> 's={0[ssid]}.'.format(q.queue[2])
        's=tee.'
        >>> q.queue[2]['time'] == d['tee']
        True
        >>> e = {}
        >>> e['foo'] = datetime.today()
        >>> e['bar'] = datetime.today()
        >>> e['tee'] = datetime.today()
        >>> q.alive('bar', e['bar'])
        1
        >>> len(q.queue)
        3
        >>> 's={0[ssid]}.'.format(q.queue[0])
        's=foo.'
        >>> q.queue[0]['time'] == e['foo']
        False
        >>> 's={0[ssid]}.'.format(q.queue[1])
        's=bar.'
        >>> q.queue[1]['time'] == e['bar']
        True
        >>> 's={0[ssid]}.'.format(q.queue[2])
        's=tee.'
        >>> q.queue[2]['time'] == e['tee']
        False
        """
        self.expire()
        i = self.exist_session(session_id)
        if i > -1:
            self.queue[i]['time'] = last_time
        return i

    def active(self):
        """ get now active (first cell).

        >>> q=WaitQueue()
        >>> q.entry('foo', datetime.today())
        >>> q.entry('bar', datetime.today())
        >>> q.entry('tee', datetime.today())
        >>> a=q.active()
        >>> a['ssid']
        'foo'
        """
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return None

    def next(self):
        """ Next item activate and drop
        >>> q=WaitQueue()
        >>> q.entry('foo', datetime.today())
        >>> q.entry('bar', datetime.today())
        >>> q.entry('tee', datetime.today())
        >>> q.next()
        >>> len(q.queue)
        2
        >>> q.next()
        >>> len(q.queue)
        1
        >>> q.next()
        >>> len(q.queue)
        0
        """
        if len(self.queue) > 0:
            self.queue_pop(0)

    def expire(self):
        """ check all entries last_time and expire.
        >>> q=WaitQueue()
        >>> q.entry('foo', datetime.today())
        >>> q.entry('bar', datetime.today() - timedelta(minutes=20))
        >>> q.entry('tee', datetime.today())
        >>> q.expire()
        >>> len(q.queue)
        2
        >>> 's={0[ssid]}.'.format(q.queue[0])
        's=foo.'
        >>> 's={0[ssid]}.'.format(q.queue[1])
        's=tee.'
        """
        now = datetime.today()
        for (i, item) in enumerate(self.queue):
            if now > item['time'] + self.expire_span:
                self.queue_pop(i)
        if len(self.queue) > 1:  # Not need expire if only a item in queue.
            if 'active_start' not in self.queue[0]:
                self.queue[0]['active_start'] = now
            if now > self.queue[0]['active_start'] + self.active_span:
                self.next()

    def delete(self, session_id):
        """ Explicit delete item.
        >>> q=WaitQueue()
        >>> q.entry('foo', datetime.today())
        >>> q.entry('bar', datetime.today())
        >>> q.entry('tee', datetime.today())
        >>> q.delete('foo')
        >>> len(q.queue)
        2
        """
        i = self.exist_session(session_id)
        if i > -1:
            self.queue_pop(i)

    def clear(self):
        """ delete all item.
        >>> q=WaitQueue()
        >>> q.entry('foo', datetime.today())
        >>> q.entry('bar', datetime.today())
        >>> q.entry('tee', datetime.today())
        >>> q.clear()
        >>> len(q.queue)
        0
        """
        self.queue = []


if __name__ == '__main__':
    import doctest
    doctest.testmod()
