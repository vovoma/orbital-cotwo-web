# coding=utf-8
from sqlalchemy import func, select
import geojson

__author__ = 'Lorenzo'

from src.dbproxy import dbProxy


class spatial(dbProxy):
    """
    Handle spatial read operations on the database.

    Part of Database Manipulation Layer.
    """
    @classmethod
    def shape_geometry(cls, long, lat):
        """
        Return a EWKT string representing a point.

        :param long:
        :param lat:
        :return str: the EWKT representation of the Geometry
        """
        return 'SRID=3857;POINT({long!s} {lat!s})'.format(
            long=long,
            lat=lat
        )

    @classmethod
    def shape_geography(cls, long, lat, mode='POINT'):
        """Return a EWKT string representing a point.

        :param long:
        :param lat:
        :return str: the EWKT representation of the Geography
        """
        return 'SRID=4326;{mode!s}({long!s} {lat!s})'.format(
            mode=mode,
            long=long,
            lat=lat
        )

    @classmethod
    def shape_aoi(cls, center, size=1.4):
        """Build a square around a center point, to define a Area of Interest.

        Basic algorithm to build a square:
            nw: X - 0.5*width, Y + 0.5*height
            ne: X + 0.5*width, Y + 0.5*height
            se: Y + 0.5*height, Y - 0.5*height
            sw: Y - 0.5*height, Y - 0.5*height

        Reminder:
           Geography(SRID=4326)
           Geometry(SRID=3857)

        Example query to cast a EWKT string in Geometry type:
            SELECT 'SRID=3857;POLYGON(((-179.748110962 -22.8178), (-178.348110962 -22.8178),
            (-179.048 -22.1178405762), (-179.048 -23.5178405762), (-179.748110962 -22.8178), ))'::geometry;

        :return tuple: polygon's EWKT and center's EWKT
        """
        _SIZE = size  # polygon side = 1.4 degree

        center_ = center if isinstance(center, tuple) else cls.unshape_geo_hash(center)

        polygon = [[center_[0] - 0.5 * _SIZE, center_[1] + 0.5 * _SIZE],
                   [center_[0] + 0.5 * _SIZE, center_[1] + 0.5 * _SIZE],
                   [center_[0] + 0.5 * _SIZE, center_[1] - 0.5 * _SIZE],
                   [center_[0] - 0.5 * _SIZE, center_[1] - 0.5 * _SIZE],
                   [center_[0] - 0.5 * _SIZE, center_[1] + 0.5 * _SIZE]]

        shape = cls.from_list_to_ewkt(polygon)
        return shape, center

    @classmethod
    def from_list_to_ewkt(cls, geodata):
        """
        Take a list of points and return a EWKT POLYGON().

        :param list geodata:
        :return str:
        """
        string = str()
        for i, p in enumerate(geodata):
            string += str(p[0]) + ' ' + str(p[1])
            if i != len(geodata) - 1:
                string += ', '
        return 'SRID=3857;POLYGON(({polygon}))'.format(
            polygon=string
        )

    @classmethod
    def aggregate_aoi_data_(cls, aoi):
        """
        From a polygon collect all the points in the `t_co2` table that lays inside it.
        Serialize them into a GEOJSON and store them in the `json` column.
        :param aoi:
        :return:
        """
        pass

    @classmethod
    def unshape_geo_hash(cls, geohash, ):
        """Return a tuple of (long, lat, ) from a hashed geometry/geography.

        Example:
            SELECT ST_AsEWKT('0101000020110F0000000000C0A947264000000020BB9165C0');
            --------------------------------------------------
            SRID=4326;POINT(11.111065864563 -7.45048522949219)

        Possible outputs:
            ST_AsGEOJSON
            ST_AsText
            ST_X
            ST_Y

        :param geohash: the value of a Geometry or Geography column or the EWKT
        :return tuple: (longitude, latitude, )
        """

        return cls._connected(
            "SELECT ST_X(%s), ST_Y(%s)",
            **{'values': (str(geohash), str(geohash), )}
        )

    @classmethod
    def coordinates_from_geojson(cls, geojs):
        """Return coordinates from a GeoJSON Feature.
        :param str geojs:
        :return generator:
        """
        obj = geojson.loads(geojs)
        gen = geojson.utils.coords(obj)
        coords = [g for g in list(gen)]
        return coords



__all__ = ['shape_geometry',
           'shape_geography',
           'from_list_to_ewkt',
           'coordinates_from_geojson',
           'from_list_to_ewkt']
