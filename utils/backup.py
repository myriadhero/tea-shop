import os
import subprocess
from datetime import datetime
from datetime import timedelta as td
from shutil import make_archive, rmtree

DAYS_TO_KEEP = 14
MOST_RECENT_TO_KEEP = 5


# Step 1: Create Backup Directory
backup_dir = os.path.expanduser(
    f"~/backups/blog_backup_{datetime.now().strftime('%Y%m%d_%H%MUTC')}"
)
os.makedirs(backup_dir, exist_ok=True)
print(f"{datetime.now()}: Backing up to {backup_dir}")

# Step 2: Backup Database
db_backup_command = f"docker compose --profile prod exec -t db pg_dumpall -c -U postgres > {backup_dir}/db_backup.sql"
subprocess.run(db_backup_command, shell=True, check=True)
print(f"{datetime.now()}: DB backup dumped")

# Step 3: Copy Media Files
media_backup_command = (
    f"docker compose --profile prod cp web:/home/django/mediafiles/ {backup_dir}"
)
subprocess.run(media_backup_command, shell=True, check=True)
print(f"{datetime.now()}: Media Files dumped")

# Step 4: Archive
make_archive(backup_dir, "zip", backup_dir)
print(f"{datetime.now()}: Files archived")

# Step 5: Remove temp dir with unarchived files
rmtree(backup_dir)
print(f"{datetime.now()}: Temp files cleaned up")

# Step 5.1: Remove old backups
parent_dir = os.path.dirname(backup_dir)
cut_off_datetime = datetime.now() - td(days=DAYS_TO_KEEP)
files_in_dir = sorted(
    (os.path.join(parent_dir, f) for f in os.listdir(parent_dir) if f.endswith(".zip")),
    key=lambda f: os.path.getmtime(f),
)

files_to_delete = [
    f
    for f in files_in_dir[:-MOST_RECENT_TO_KEEP]
    if (file_modified := datetime.fromtimestamp(os.path.getmtime(f))) < cut_off_datetime
    and f"blog_backup_{file_modified.strftime('%Y%m%d')}" in f
]

for f in files_to_delete:
    os.remove(f)
    print(f"{datetime.now()}: Deleted old backup {f}")

# TODO: Step 6: Ecrypt
# TODO: the above steps endswith check for .zip may need to be changed once encryption is added
