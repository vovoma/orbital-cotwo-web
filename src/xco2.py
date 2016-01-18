# coding=utf-8
"""
Xco2 class. Main table/class/mapper of the application.

Create database table and bind to persistence layer (PostGRE/PostGIS)
<https://www.python.org/dev/peps/pep-0249/>

 Before running this script INSTALL and CREATE THE DATABASES (gis and test)
 as explained in README.md

"""

from sqlalchemy import orm
from sqlalchemy import Table, Column, Integer, MetaData, DateTime
from sqlalchemy.dialects.postgresql import JSON, NUMERIC
from sqlalchemy import UniqueConstraint
from geoalchemy2 import Geography, Geometry
from sqlalchemy.ext.declarative import declarative_base

__author__ = 'Lorenzo'

from config.config import DATABASES

Base = declarative_base()


class Xco2(Base):
    """
    Main table's model
    """
    #
    # Table definition
    # ------------------------------------------------------------------------
    __tablename__ = 't_co2'

    id = Column('id', Integer, primary_key=True)
    xco2 = Column('xco2', NUMERIC(precision=18), nullable=False)
    timestamp = Column('timestamp', DateTime, nullable=False)
    # use a geography with coordinates
    coordinates = Column(
        'coordinates',
        Geography('POINT', srid=4326, spatial_index=True),
        nullable=False
    )
    # use a geometry with pixels (for Web maps)
    pixels = Column(
        'pixels',
        Geometry('POINT', srid=3857, spatial_index=True),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint('timestamp', 'coordinates', name='uix_time_coords'),
    )

    #
    # Constructor
    # ------------------------------------------------------------------------
    def __init__(self, xco2, timestamp, longitude, latitude):
        self.xco2 = xco2
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude

    # #todo: implement the reconstructor (from query object to py object)
    @orm.reconstructor
    def init_on_load(self):
        from src.spatial import spatialRef
        unshape = spatialRef.unshape_geo_hash(str(self.coordinates))
        self.latitude = unshape[1]
        self.longitude = unshape[0]

    def __repr__(self):
        return 'Point {coordinates!r}'.format(
            coordinates=repr(self.coordinates)
        )

    def __str__(self):
        return 'Point {coordinates!s} has Xco2 level at {xco2!s}'.format(
            coordinates=self._long_lat,
            xco2=self.xco2
        )

    # #todo: implement descriptors ?
    @property
    def _long_lat(self):
        """Return latitude and longitude"""
        if all(k in self.__dict__.keys() for k in ('latitude', 'longitude',)):
            return self.longitude, self.latitude
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')

    @property
    def hash_coordinates(self):
        if all(k in self.__dict__.keys() for k in ('latitude', 'longitude',)):
            return self.shape_geography(self.longitude, self.latitude)
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')

    @property
    def hash_pixels(self):
        if all(k in self.__dict__.keys() for k in ('latitude', 'longitude',)):
            return self.shape_geometry(self.longitude, self.latitude)
        else:
            raise NotImplemented('This method is accessible only if the object'
                                 'is created with the Xco2 constructor')


class Areas(Base):
    """
    Lookup table's model.

    It stores pre-cached squared POLYGONs (Area of Interest, generated by picking
    random points as centers and a side of approximately 150 kms) mapped to
    GEOJSONs with data about points contained in these same polygons.

    see `src.areasOps` module for further documentation.
    """
    #
    # Table definition
    # ------------------------------------------------------------------------
    __tablename__ = 't_areas'

    id = Column('id', Integer, primary_key=True)
    # area of interest, a polygon (square)
    aoi = Column(
        'aoi',
        Geometry('POLYGON', srid=3857, spatial_index=True),
        nullable=False
    )
    # center of the square
    center = Column(
        'center',
        Geometry('POINT', srid=3857, spatial_index=True),
        nullable=False
    )
    # GEOJSON of points contained in the area
    data = Column(
        'data',
        JSON,
        nullable=True
    )
    __table_args__ = (
        UniqueConstraint('aoi', 'center', name='uix_aoi_center'),
    )

    def __init__(self, long, lat):
        from src.spatial import spatialRef
        self.long = long
        self.lat = lat
        self.center = spatialRef.shape_geometry(long, lat)
        self.aoi = spatialRef.shape_aoi((long, lat))

    def __repr__(self):
        return 'Area POLYGON: {aoi!r}'.format(
            aoi=repr(self.aoi)
        )

    def __str__(self):
        return 'Area POLYGON: {aoi!s} with center {center!s}'.format(
            aoi=str(self.aoi),
            center=str(self.center)
        )

if __name__ == '__main__':
    try:
        from src.dbops import dbOps
        dbOps.create_tables_in_databases(Base)
        print('####################################\n'
              '#Databases and tables created      #\n'
              '#Enter your psql command line and  #\n'
              '#check that databases {} #\n'
              '#and table t_co2, t_areas are present. #\n'
              '####################################\n'.format(DATABASES))
    except Exception as e:
        raise e
