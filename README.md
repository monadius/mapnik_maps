# mapnik_maps

Experiments with [mapnik](https://github.com/mapnik/mapnik).

# Installation (macOS)

The official [guide](https://github.com/mapnik/mapnik/wiki/MacInstallation_Homebrew).
Also need to install [python-mapnik](https://github.com/mapnik/python-mapnik).

Steps for **mapnik**:

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

(Alternatively, run `brew link --force icu4c` before `brew install boost`).

Steps for **python-mapnik**:

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
