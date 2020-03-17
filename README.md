# mapnik_maps

Experiments with [mapnik](https://github.com/mapnik/mapnik).

# Installation (macOS)

The official [guide](https://github.com/mapnik/mapnik/wiki/MacInstallation_Homebrew).
Also need to install [python-mapnik](https://github.com/mapnik/python-mapnik).

## Steps for **mapnik**:

```
brew install icu4c
brew install boost --with-icu4c

# install all dependencies and mapnik
brew install mapnik

# do not need to do further steps if mapnik-render works without errors

# install mapnik from source code
brew uninstall mapnik
git clone --recursive https://github.com/mapnik/mapnik.git
cd mapnik
./configure
make
make install
```

In case of errors, it may be required to define some variables:
```
./configure SQLITE_INCLUDES=/usr/local/opt/sqlite/include
```

If the library `proj` is not detected then it is necessary to manually edit the `SConstruct` script:

1) In `CheckProjData` return `/usr/local/Cellar/proj/6.3.0/share/proj/` (change to the actual location) manually.

2) When iterating over `OPTIONAL_LIBSHEADERS` check that `libname == 'proj'` and manually add:

```python
env.Append(CPPDEFINES = define)
env.Append(CPPDEFINES = 'ACCEPT_USE_OF_DEPRECATED_PROJ_API_H')
```

(Alternatively, run `brew link --force icu4c` before `brew install boost`).

## Steps for **python-mapnik**:

```
virtualenv mapnik
source mapnik/bin/activate

git clone https://github.com/mapnik/python-mapnik
python setup.py install

deactivate
source mapnik/bin/activate
python
import mapnik
exit()
rm -rf python-mapnik
```

If the build process fails, then try to install `mapnik` from source code and repeat the build process. Additionally it may be required to set a custom version of `boost-python` library:
```
export BOOST_PYTHON_LIB=boost_python37
```

## Fixing broken virtualenv links

find mapnik -type l -delete
virtualenv mapnik

From [here](https://stackoverflow.com/a/25947333).

# Links

- [Natural Earth Data](http://www.naturalearthdata.com/)

- [The National Map Small Scale](https://nationalmap.gov/small_scale/atlasftp.html)

- [QGIS](http://www.qgis.org/en/site/)

## Mapnik Links

- [Mapnik](https://github.com/mapnik/mapnik)

- [PyMapnik2 example](https://github.com/mapnik/pymapnik2/blob/master/src/mapnik/demo/python/rundemo.py)

- [Basic tutorial](https://github.com/mapnik/mapnik/wiki/GettingStartedInPython)

- [XML Config Reference](https://github.com/mapnik/mapnik/wiki/XMLConfigReference)

## Extra Links

- [Guide to Selecting Map Projections](http://www.georeference.org/doc/guide_to_selecting_map_projections.htm)
