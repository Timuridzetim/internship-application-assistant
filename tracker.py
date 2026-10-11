"""Local internship application tracker; Python standard library only."""
import argparse
import csv
import sqlite3
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

STATUSES = ('saved', 'preparing', 'applied', 'interview', 'offer', 'rejected', 'withdrawn')
CLOSED = ('offer', 'rejected', 'withdrawn')


def day(value):
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use YYYY-MM-DD.') from exc


def url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('https', 'http') or not parsed.netloc:
        raise argparse.ArgumentTypeError('Use an absolute HTTP(S) vacancy URL.')
    return value.strip()


def nonempty(value):
    if not value.strip():
        raise argparse.ArgumentTypeError('Value must not be empty.')
    return value.strip()


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY, company TEXT NOT NULL, role TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE, location TEXT NOT NULL, status TEXT NOT NULL,
        deadline TEXT, next_action TEXT NOT NULL, next_date TEXT NOT NULL,
        notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL, applied_at TEXT)''')
    db.commit()
    return db


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', default='data/applications.sqlite3')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    add = sub.add_parser('add')
    for field in ('company', 'role', 'location', 'next-action'):
        add.add_argument('--' + field, required=True, type=nonempty)
    add.add_argument('--url', required=True, type=url)
    add.add_argument('--deadline', type=day)
    add.add_argument('--next-date', required=True, type=day)
    add.add_argument('--notes', default='')
    listing = sub.add_parser('list')
    listing.add_argument('--status', choices=STATUSES)
    due = sub.add_parser('due')
    due.add_argument('--on', type=day, default=date.today().isoformat())
    update = sub.add_parser('update')
    update.add_argument('id', type=int)
    update.add_argument('--status', choices=STATUSES)
    update.add_argument('--next-action', type=nonempty)
    update.add_argument('--next-date', type=day)
    update.add_argument('--notes')
    export = sub.add_parser('export')
    export.add_argument('path')
    return p


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if args.command == 'update':
        if (args.next_action is None) != (args.next_date is None):
            p.error('Provide --next-action and --next-date together.')
        if all(getattr(args, k) is None for k in ('status', 'next_action', 'next_date', 'notes')):
            p.error('Provide at least one update.')
    try:
        with connect(args.db) as db:
            today = date.today().isoformat()
            if args.command == 'init':
                print(f'Ready: {args.db}')
            elif args.command == 'add':
                cur = db.execute('''INSERT INTO applications
                    (company,role,url,location,status,deadline,next_action,next_date,notes,created_at,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                    (args.company,args.role,args.url,args.location,'saved',args.deadline,
                     args.next_action,args.next_date,args.notes,today,today))
                print(f'Added application #{cur.lastrowid}')
            elif args.command == 'update':
                row = db.execute('SELECT * FROM applications WHERE id=?', (args.id,)).fetchone()
                if row is None:
                    p.error(f'Application #{args.id} does not exist.')
                changes = {k: getattr(args, k) for k in ('status','next_action','next_date','notes') if getattr(args,k) is not None}
                changes['updated_at'] = today
                if args.status == 'applied' and row['applied_at'] is None:
                    changes['applied_at'] = today
                db.execute('UPDATE applications SET ' + ', '.join(k+'=?' for k in changes) + ' WHERE id=?', (*changes.values(),args.id))
                print(f'Updated application #{args.id}')
            else:
                sql, params = 'SELECT * FROM applications', []
                if args.command == 'list' and args.status:
                    sql += ' WHERE status=?'
                    params = [args.status]
                elif args.command == 'due':
                    sql += " WHERE status NOT IN ('offer','rejected','withdrawn') AND (next_date<=? OR (status IN ('saved','preparing') AND deadline<=?))"
                    params = [args.on,args.on]
                rows = db.execute(sql + ' ORDER BY next_date, id', params).fetchall()
                if args.command == 'export':
                    dest = Path(args.path)
                    if dest.resolve() == Path(args.db).resolve():
                        p.error('Export path must differ from database path.')
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    columns = [r[1] for r in db.execute('PRAGMA table_info(applications)')]
                    with dest.open('w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        writer.writerows(tuple(r) for r in rows)
                    print(f'Exported {len(rows)} applications to {dest}')
                else:
                    for row in rows:
                        print(f"#{row['id']} | {row['company']} | {row['role']} | {row['location']} | {row['status']} | deadline: {row['deadline'] or 'unknown'} | {row['next_date']}: {row['next_action']}")
                        print(f"  {row['url']}")
                        if row['notes']:
                            print(f"  Notes: {row['notes']}")
                    if not rows:
                        print('No applications found.')
    except (sqlite3.Error, OSError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()
