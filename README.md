idle-runner: Run some script or command any time the session goes idle.

### building:

#### ubuntu/debian:
```
dpkg-buildpackage
```
... install debs

#### other:
```
meson builddir --prefix=/usr
ninja -C builddir
ninja -C builddir install
```
