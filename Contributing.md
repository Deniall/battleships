## How to contribute code using branches and pull requests

When you go to make a commit or change, instead of choosing "commit directly to master branch", instead choose the other option. This will make a temporary branch. Then, switch back to master and merge the new temporary branch with the master, and then once the pull request is merged, choose the 'delete this branch' option.

ORRRR

use commandline, make a change, cd to the local directory of the repo on your computer, use the command `git remote set-url origin git@github.com:fosterjen/team-ucd-battleship.git` , then do `git commit -a -m "your message"` , then do `git push` and enter your SSH key passphrase (setting that up has been tutorial'd to death so look it up if its gibberish)
