# How to build a debian package for debian and ubuntu?

1. checkout the git tag which you want to package as a debian package
2. change version string in "build-deb/pass-import/DEBIAN/control" to that tag (version number)
3. change directory to here: "cd build-deb"
4. run build script: "./build-now.sh"
5. verify that your release (pass-import.deb) is good enough for releasing to a package repo