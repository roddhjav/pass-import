mkdir -p pass-import/usr/lib/password-store/extensions
cp ../import.bash pass-import/usr/lib/password-store/extensions/import.bash
chmod 0755 pass-import/usr/lib/password-store/extensions/import.bash

mkdir -p pass-import/usr/share/man/man1
cp ../pass-import.1 pass-import/usr/share/man/man1/pass-import.1
chmod 0644 pass-import/usr/share/man/man1/pass-import.1

mkdir -p pass-import/etc/bash_completion.d
cp ../completion/pass-import.bash pass-import/etc/bash_completion.d/pass-import
chmod 0644 pass-import/etc/bash_completion.d/pass-import

mkdir -p pass-import/usr/share/zsh/site-functions
cp ../completion/pass-import.zsh pass-import/usr/share/zsh/site-functions/_pass-import
chmod 0644 pass-import/usr/share/zsh/site-functions/_pass-import

#build
dpkg-deb --build pass-import/