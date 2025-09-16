# Notes for using GUFI

## Compile GUFI
cd GUFI

mkdir build

cd build

cmake ..

make

(sudo) make install

## create a GUFI tree
gufi_dir2index <src_dir> <index_dir>

### post-process the index
gufi_treesummary

usage: gufi_treesummary [options] GUFI_index

options:
  
  -h                     help
  
  -H                     show assigned input values (debugging)
  
  -v                     version
  
  -P                     print directories as they are encountered
  
  -n <threads>           number of threads
  
  -d <delim>             delimiter (one char)  [use 'x' for 0x1E]
  
  W-X                     Dry run

GUFI_index               path to GUFI index

# Query the index
gufi_query

## Dump the schema to explore

### Print tables
sqlite3 ./index/db.db ".tables"

### Print columns of a table
sqlite3 ./index/db.db ".schema entries"

### Reference columns in query

-T, -S, -E what SQl to run on tables at each level:

- -T = tree-summary
- -S = summary
- -E = entries
- -d = delimiter, make outputs easier. ex $'\t' tab, , CSV comma

## Fields in entries
### Core
- name: base name of the file
- type: file type
- inode: inode number on the filesystem
- mode: file mode bits, permissions/type
- nlink: number of hard links to file

### Ownership
- uid: User ID of files owner
- gid: group ID of files group

### Size and Storage
- size: file size in bytes
- blksize: preferred blocksize for filesystem I/O
- blocks: number of 512 byte blocks allocated

### Timestamps
- atime: last access time
- mtime: last modification
- ctime: last status change (metadata: owner, mode, etc)
- crtime: creation time

### Links / metadata
- linkname: target path that symlink points to
- xattr_names: extended attribute names

### Additional Fields
- ossint1-ossint4: Integer fields for site-specfic metadata
- osstext1, osstext2: Text fields for custom annotations

## Pass SQL to gufi_query

### All files bigger than 1MB
gufi_query -E "SELECT name, size FROM entries WHERE size > 1048576;" ./myindex

### Files modified in the last day
gufi_query -E "SELECT name, mtime FROM entries WHERE mtime > strftime('%s','now','-1 day');" ./myindex

### All symlinks + targets
gufi_query -E "SELECT name, linkname FROM entries WHERE type = 'l';" ./myindex