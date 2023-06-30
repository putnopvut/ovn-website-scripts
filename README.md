# ovn-website-scripts
Scripts for making changes to the ovn website

# Installation requirements

The scripts require python 3.7+. Dependencies can be installed by running
```
pip install -r requirements.txt
```

# update\_website.py

This is the main script in this repository. The script takes as an argument an
OVN branch number, such as "22.03" or "23.09". The script then generates
appropriate OVN website content for that particular branch. The script uses
/tmp/ovn-website-workdir/ovn-website as the location for the OVN website. It is
up to the caller of the script to commit and push these changes to an appropriate
remote and/or create a pull request.

Rather than actually updating website content, the script works by regenerating
content appropriate for the branch on every run. This makes it work both for
new and old branches alike. When a new release is made on a branch, run
```
./update_website.py <branch>
```
And the script will detect the new release and update the release pages
appropriately.

The script can also be used to update the support status of old branches on the
OVN website. Like when a new release is made, you can run the script on an old
branch, like
```
./update_website.py <old_branch>
```
If any old releases' support status has changed, then the pages for those
releases will be updated to reflect this.

# website\_maintenance.sh

This is a convenience script that can be used to automatically run
`update_website.py` on all supported branches. A potential use-case for this
script is to run nightly in order to keep the support status of released
branches up-to-date on the website.

# TODO

- Add an option to `update_website.py` to automatically create a github pull
  request with the ovn-website changes from a script run.
