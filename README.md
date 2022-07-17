# fs-parse

Small library and scripts to parse FSX/FS9 object files

There is a library under the `fs_parse` folder and a bunch of utility scripts
in the `scripts` folder. Each script has a description of what it does in its header.

The library was created mainly to parse and manipulate scenery placements (e.g. find duplicate models, missing
libraries, etc.)
and to find missing/unused aircraft textures.

A lot of stuff is still not supported (e.g. airports, autogen, terrain), but given the common structure of the files
it should be relatively easy to just replace the remaining placeholder classes with their actual implementations.

One exception is FS9 MDL files, which often encapsulate old FS2002 BGL code.
I don't have a spec for those, and this means that you can extract only the basic info from FS9 aircrafts (e.g. name,
uuid)  
If you have the original specification, or a way to at least reliably extract the TEXTURE part
from FS9 .mdl files, please let me know by opening an issue.

If you want to contribute to this code, PRs are welcome.